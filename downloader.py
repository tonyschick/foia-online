import time, datetime, urllib3, re, requests, os, csv
# import mechanize
import time, datetime
from bs4 import BeautifulSoup

#disable warnings
#urllib3.disable_warnings()

# Create a CSV to log the work
# Write in a first row with the following labels, to become our column headers
headers = ["Name", "Url", "Status"]

with open('foia-download-log.csv', 'a', newline='') as logfile:
    writer = csv.writer(logfile)
    writer.writerow(headers)

http = urllib3.PoolManager()

# Ex. https://foiaonline.regulations.gov/foia/action/public/view/request?objectId=090004d280c519ce
foia_online_id = input("Copy and paste the ID for your FOIA (the numbers after objectId= ) ")

url = foia_online_id

try:
    # using urllib3 to open the page
    html = http.urlopen('GET',url)
    # and to read the html data from the request
    html = html.data
    # feed it into Beautiful Soup, our html parsing library
    bs = BeautifulSoup(html, "lxml")

    #find how many pages there are holding our documents. Divide by 2 because they're listed twice, at the top and bottom of the page
    number_of_pages = len(bs.findAll(True, {"class": "resPagNum"})) / 2
    number_of_pages = int(number_of_pages)

    print(number_of_pages)
except:
    print("Error!")


counter = 0
# iterate through a list of numbers, add 1 to number_of_pages so list doesn't stop short
for d in range(1,(number_of_pages+1)):

    # open a url, changing the 'p=' for each number in our list, so that it opens all pages 1-5, in order
    page_url = "https://foiaonline.regulations.gov/foia/action/public/view/request?event=request&objectId=090004d280b6c05e&d-8138531-p={}#dttPubRecords".format(d)

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
        logfile = open("foia-log.csv", "a")

        output_row = []
        document_link = tr.find("a").get('href')
        document_name = tr.find("a").get_text()

        output_row.append(document_name)
        output_row.append(document_link)

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
            output_row.append("Error on download")

        with open('foia-log.csv', 'a', newline='') as logfile:
            writer = csv.writer(logfile)
            writer.writerow(output_row)

    print("Finished with page{}".format(d))

print("Finished downloading! {} files in total".format(counter))
