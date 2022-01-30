import sqlite3
import re
import requests
from bs4 import BeautifulSoup
import time

start = time.time()

#CONNECTING TO THE DATABASE

db = sqlite3.connect('database.db')
cursor = db.cursor()


#GETTING URL

url = input("URL: ")
while(len(url)<1):
    print("Please input a valid url.\n")
    url = input("URL: ")


#MAKING TABLE NAME

def make_db_name(url):
    if 'www' in url:
        table_name = re.findall('ht.*://www\.(.*?)\.', url)
        table_name = table_name[0]
        return table_name
    else: 
        table_name = re.findall('ht.*://(.*?)\.', url)
        table_name = table_name[0]
        return table_name    
name = make_db_name(url)


#CREATING THE DATABASE

cursor.execute("CREATE TABLE IF NOT EXISTS " + name + " (ID INTEGER PRIMARY KEY AUTOINCREMENT,URL varchar(255),Title varchar(255),Description varchar(255),InternalLinks INTEGER,ExternalLinks INTEGER, PageContents TEXT, Canonical varchar(255), Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)" )
all_urls = []
all_urls.append(url)


#EXTRACTING DATA

def extract_data(soup):
    #get title
    title = soup.title.string
    #get descriptions
    try:
        description = soup.find("meta", {"name": "description"})['content']
    except:
        description = "Null"
    #get canonical
    try:
        canonical = soup.fine('link', {'rel':'canonical'})['href']
    except:
        canonical = "Null"
    contents = soup.text.replace("\n", "")
    return (title, description, contents, canonical)


#EXTRACTING LINKS

def extract_links(soup):
    raw_data = soup.find_all('a')
    for link in raw_data:
        if str(link.get('href')).startswith(url) == True and link.get('href') not in all_urls:
            if '.jpg' in link.get('href') or '.png' in link.get ('href'):
                continue
        else:
            all_urls.append(link.get('href'))
    return len(raw_data)


#INSERT INTO SQLITE

def insert_data(data):
    url, title, description, contents, no_of_links, canonical = data
    cursor.execute("INSERT INTO " + name + " (URL, Title, Description, ExternalLinks, PageContents, Canonical) VALUES(?,?,?,?,?,?)",(url, title, description, no_of_links, contents, canonical,))
    db.commit()


#CRAWLING THE WEB
count = 0
while count < len(all_urls):
    try:
        print(str(count) + ": " + all_urls[count])
        r = requests.get(all_urls[count])
        if r.status_code == 200:
            html = r.text
            soup = BeautifulSoup(html, "html.parser")
            no_of_links = extract_links(soup)
            title, description, contents, canonical = extract_data(soup)
            insert_data((all_urls[count], title, description, contents, no_of_links,canonical))

        count += 1
    except Exception as e:
        count += 1
        print(str(e))
cursor.close()
db.close()
end = time.time()
print(end - start)