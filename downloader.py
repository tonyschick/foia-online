import time, datetime, urllib3, csv, re, requests, os
# import mechanize
import time, datetime
from bs4 import BeautifulSoup

#disable warnings
#urllib3.disable_warnings()

http = urllib3.PoolManager()

url = input("Copy and paste your FOIA Online URL ")

html = http.urlopen('GET',url)
html = html.data

bs = BeautifulSoup(html, "lxml")

# page_holder = bs.findAll("div", { "class" : "resPagArea" })

#find how many pages there are holding our documents. Divide by 2 because they're listed twice, at the top and bottom of the page
number_of_pages = len(bs.findAll(True, {"class": "resPagNum"})) / 2
number_of_pages = int(number_of_pages)

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
        #find all the link tags
        document_link = tr.find("a").get('href')
        document_name = tr.find("a").get_text()

        #open the document url
        document_url = "https://foiaonline.regulations.gov{}".format(document_link)
        document_html = http.urlopen('GET', document_url)
        document_html = document_html.data

        document_bs = BeautifulSoup(document_html, "lxml")

        download_link_div = document_bs.find("div", {"class": "subContentFull"})
        download_link = download_link_div.find("a").get("href")

        download_url = "https://foiaonline.regulations.gov{}".format(download_link)
        download_content = requests.get(download_url)

        file = open("{}.pdf".format(document_name), 'wb')
        file.write(download_content.content)
        file.close()
