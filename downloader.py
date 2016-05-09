import time, datetime, urllib3, re, requests, os, csv, sys
# import mechanize
import time, datetime
from bs4 import BeautifulSoup

#disable warnings
urllib3.disable_warnings()

# Create a CSV to log the work
# Write in a first row with the following labels, to become our column headers
headers = ["Name", "Url", "Status"]

with open('foia-download-log.csv', 'a', newline='') as logfile:
    writer = csv.writer(logfile)
    writer.writerow(headers)

http = urllib3.PoolManager()

foia_online_id = sys.argv[1]
url = "https://foiaonline.regulations.gov/foia/action/public/view/request?objectId={}".format(foia_online_id)

# using urllib3 to open the page
html = http.urlopen('GET',url)

# and to read the html data from the request
html = html.data

# feed it into Beautiful Soup, our html parsing library
bs = BeautifulSoup(html, "lxml")

#find how many pages there are holding our documents. Obtained by grabbing the page number out of the url in the "last page"
number_of_pages = bs.find_all("a", {"class": "resPagNav"})[3].get('href')
number_of_pages = re.findall('(?<=p=)(.*?)(?=#dttPubRecords)', number_of_pages)

number_of_pages = int(number_of_pages[0])
print("Total pages: {}".format(number_of_pages))

counter = 0
# iterate through a list of numbers, add 1 to number_of_pages so list doesn't stop short
for d in range(1,(number_of_pages+1)):

    # open a url, changing the 'p=' for each number in our list, so that it opens all pages 1-5, in order
    page_url = "https://foiaonline.regulations.gov/foia/action/public/view/request?event=request&objectId=090004d280b6c05e&d-8138531-p={}#dttPubRecords".format(d)
    # print(page_url)

    #open the page_url and pull the html out of it and into a variable
    page_html = http.urlopen('GET', page_url)
    page_html = page_html.data

    #feed it into Beautiful Soup, our library for parsing html
    document_bs = BeautifulSoup(page_html, "lxml")
   
    #find the table on the page we want based on its id
    documents_table = document_bs.find("table", {"id": "dttPubRecords"})
   
    # find the tbody so we're ignoring rows in the header
    documents_table_body = documents_table.find("tbody")
    
    # iterate through each row of the table
    for tr in documents_table_body.find_all("tr"):
        logfile = open("foia-download-log.csv", "a")

        output_row = []
       
        #find all the link tags
        document_link = tr.find("a").get('href')
        document_name = tr.find("a").get_text()

        output_row.append(document_name)
        output_row.append(document_link)

        #open the document url
        document_url = "https://foiaonline.regulations.gov{}".format(document_link)
        document_html = http.urlopen('GET', document_url)
        document_html = document_html.data

        document_bs = BeautifulSoup(document_html, "lxml")

        download_link_div = document_bs.find("div", {"class": "subContentFull"})
        download_link = download_link_div.find("a").get("href")

        try:
            download_url = "https://foiaonline.regulations.gov{}".format(download_link)
            download_content = requests.get(download_url)

            file = open("{}.pdf".format(document_name), 'wb')
            file.write(download_content.content)
            file.close()

            output_row.append("Downloaded successfully")
            counter += 1
        except:
            output_row.append("Error on downloaded")

        with open('foia-download-log.csv', 'a', newline='') as logfile:
            writer = csv.writer(logfile)
            writer.writerow(output_row)

    print("Finished with page{}".format(d))

print("Finished downloading! {} files in total".format(counter))
