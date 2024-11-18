import urllib.request
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb+srv://nathanzamora45:al7bJQa8WRxkhfxk@cluster0.ubcxi.mongodb.net/")
db = client["cs_website"]
collection = db["pages"]

# URL Frontier Class to manage URLs
class URLFrontier:
    def __init__(self):
        self.frontier = ["https://www.cpp.edu/sci/computer-science/"]  # Initial URL
        self.visited = set()

    def done(self):
        return len(self.frontier) == 0

    def nextURL(self):
        url = self.frontier.pop(0)
        self.visited.add(url)
        return url

    def addURL(self, url):
        if url not in self.visited and url not in self.frontier:
            self.frontier.append(url)

def retrieveHTML(url):
    try:
        with urllib.request.urlopen(url) as response:
            if "text/html" in response.headers.get("Content-Type", ""):
                return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error retrieving {url}: {e}")
    return None

def storePage(url, html):
    if html:
        collection.insert_one({"url": url, "html": html})

def parse(html):
    return BeautifulSoup(html, 'html.parser')

def target_page(soup):
    # Stop criteria: when the crawler finds <h1 class="cpp-h1">Permanent Faculty</h1>
    heading = soup.find('h1', class_='cpp-h1')
    return heading is not None and heading.text.strip() == "Permanent Faculty"

# Strictly following the pseudocode
def crawlerThread(frontier):
    while not frontier.done():
        url = frontier.nextURL()
        html = retrieveHTML(url)
        if html:
            storePage(url, html)
            soup = parse(html)

            if target_page(soup):
                print(f"Target page found: {url}")
                break  # clear_frontier() in this context

            # For each unvisited URL in parse(html), add to frontier
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(url, href)
                # Consider only .html and .shtml URLs
                if absolute_url.endswith('.html') or absolute_url.endswith('.shtml'):
                    parsed_url = urlparse(absolute_url)
                    # Restrict crawling to the target domain
                    if parsed_url.netloc == "www.cpp.edu":
                        frontier.addURL(absolute_url)

# Initialize and run the crawler
frontier = URLFrontier()
crawlerThread(frontier)
