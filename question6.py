import pymongo
from bs4 import BeautifulSoup

# Connect to MongoDB
client = pymongo.MongoClient("mongodb+srv://nathanzamora45:al7bJQa8WRxkhfxk@cluster0.ubcxi.mongodb.net/")
db = client["cs_website"]
collection = db["pages"]

# Collection to store faculty data
faculty_collection = db["faculty_info"]

def parse_faculty_info():
    documents = collection.find()

    for doc in documents:
        if "html" not in doc:
            continue

        html_content = doc["html"]
        if isinstance(html_content, bytes):
            html_content = html_content.decode('utf-8')

        soup = BeautifulSoup(html_content, 'html.parser')

        # Focus on "Permanent Faculty" page for testing
        if "Permanent Faculty" in (soup.title.string if soup.title else ""):
            print("Inspecting 'Permanent Faculty' page structure:")

            # Extract faculty entries contained in <div class="clearfix">
            faculty_entries = soup.find_all('div', class_='clearfix')
            for entry in faculty_entries:
                # Extract relevant fields using BeautifulSoup
                name = entry.find('h2').text.strip() if entry.find('h2') else "N/A"

                # Improved logic for title, office, phone, etc.
                title = "N/A"
                office = "N/A"
                phone = "N/A"
                email = "N/A"
                website = "N/A"

                # Extract text by searching for <p> tags
                for p_tag in entry.find_all('p'):
                    if "Title:" in p_tag.text:
                        title = p_tag.text.replace("Title:", "").strip()
                    elif "Office:" in p_tag.text:
                        office = p_tag.text.replace("Office:", "").strip()
                    elif "Phone:" in p_tag.text:
                        phone = p_tag.text.replace("Phone:", "").strip()

                # Extract email
                email_tag = entry.find('a', href=True)
                if email_tag:
                    email = email_tag.text.strip()
                    website = email_tag.get('href').strip()

                # Store parsed data in MongoDB
                faculty_data = {
                    "name": name,
                    "title": title,
                    "office": office,
                    "phone": phone,
                    "email": email,
                    "website": website
                }
                faculty_collection.insert_one(faculty_data)
                print(f"Inserted: {faculty_data}")

# Run the parser
parse_faculty_info()
