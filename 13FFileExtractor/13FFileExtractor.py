import xml.etree.ElementTree as ET
import csv
import os
import requests
from bs4 import BeautifulSoup
import urllib.request
#from DownloaderFunctionFile import txt_Downloader
#from ImporterFunctionFile import importer
#from RemoverFunctionFile import txt_to_xml

#########################
#Function Definitions
#########################

def txt_to_xml(filename):
    # Open file and read the lines of the file and then close the file
    file = open(filename, 'r')
    lines = file.readlines()
    file.close()

    # Create count variable to index where the xml of the data table info begins
    count = 0
    for line in lines:
        count += 1
        if line.startswith("<informationTable xsi"): break

    # Remove all lines up to the first line of the data table xml info
    del lines[0:count]

    # Remove last 4 lines of excess data
    del lines[-4:]

    # Write new info to new file which doesnt contain deleated files
    new_file = open(filename[:-4] + ".xml", "w+")
    new_file.write("<informationTable >\n")
    for line in lines:
        new_file.write(line)
    pass

def txt_Downloader(urlInput,count,cwd):

    #Beautiful soup to parse html
    response2 = requests.get(urlInput)
    soup2 = BeautifulSoup(response2.content, 'html.parser')

    #Create base url
    baseURL = "http://sec.gov"

    #Create list of urls contained on the entire page (We only care about the 3rd to last one (the .txt file))
    urlList = []
    for link in soup2.find_all('a'):
        # print(link.get('href'))
        urlList.append(link.get('href'))

    #Find that one .txt file we care about
    for l in urlList:
        if l[-3:] == 'txt':
            finalUrl = baseURL + l

    #Download that file and save it (takes a counter input to help with naming))

    urllib.request.urlretrieve(finalUrl, cwd + "/"+ str(count) + '.txt')
    pass

def importer(myCIK,cwd):

    ## From Sigma coding github
    # base URL for the SEC EDGAR browser
    endpoint = r"https://www.sec.gov/cgi-bin/browse-edgar"

    # define our parameters dictionary
    param_dict = {'action': 'getcompany',
                  'CIK': myCIK,  # 0001633313 <-AVORO CIK
                  'type': '13F-HR',
                  'datea': '20180101',
                  'owner': 'exclude',
                  'start': '',
                  'output': '',
                  'count': '100'}

    # request the url, and then parse the response.
    response = requests.get(url=endpoint, params=param_dict)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Let the user know it was successful.
    print('Request Successful')
    print(response.url)

    # find the document table with our data
    doc_table = soup.find_all('table', class_='tableFile2')

    # define a base url that will be used for link building.
    base_url_sec = r"https://www.sec.gov"

    master_list = []

    # loop through each row in the table.
    for row in doc_table[0].find_all('tr'):

        # find all the columns
        cols = row.find_all('td')

        # if there are no columns move on to the next row.
        if len(cols) != 0:

            # grab the text
            filing_type = cols[0].text.strip()
            filing_date = cols[3].text.strip()
            filing_numb = cols[4].text.strip()

            # find the links
            filing_doc_href = cols[1].find('a', {'href': True, 'id': 'documentsbutton'})
            filing_int_href = cols[1].find('a', {'href': True, 'id': 'interactiveDataBtn'})
            filing_num_href = cols[4].find('a')

            # grab the the first href
            if filing_doc_href != None:
                filing_doc_link = base_url_sec + filing_doc_href['href']
            else:
                filing_doc_link = 'no link'

            # grab the second href
            if filing_int_href != None:
                filing_int_link = base_url_sec + filing_int_href['href']
            else:
                filing_int_link = 'no link'

            # grab the third href
            if filing_num_href != None:
                filing_num_link = base_url_sec + filing_num_href['href']
            else:
                filing_num_link = 'no link'

            # create and store data in the dictionary
            file_dict = {}
            file_dict['file_type'] = filing_type
            file_dict['file_number'] = filing_numb
            file_dict['file_date'] = filing_date
            file_dict['links'] = {}
            file_dict['links']['documents'] = filing_doc_link
            file_dict['links']['interactive_data'] = filing_int_link
            file_dict['links']['filing_number'] = filing_num_link

            # let the user know it's working
            # print('-' * 100)
            # print("Filing Type: " + filing_type)
            # print("Filing Date: " + filing_date)
            # print("Filing Number: " + filing_numb)
            # print("Document Link: " + filing_doc_link)
            # print("Filing Number Link: " + filing_num_link)
            # print("Interactive Data Link: " + filing_int_link)

            # append dictionary to master list
            master_list.append(file_dict)

    # print(master_list[0]['links']['documents'])

    # loop through to get the links from the dictionary (link to individual filing page)
    # Calls txt downloader to
    count = 0
    for report in master_list:
        print('-' * 100)
        print(report['links']['documents'])

        txt_Downloader(report['links']['documents'], count,cwd)
        count = count + 1
    pass


###################### Start of Program!

#How many quarters we want to go back
FILE_NUM=10
# Enter CIK number of Money Manager you want to get info on
compName=input("Enter Company Name (No Spaces):")
CIK=input("Enter CIK Number:") ## 0001633313 # 0001600004 <- First Light
#Call importer function with CIK number which imports txt files from SEC EDGAR
cwd=os.getcwd()
importer(CIK,cwd)

# Clean up txt using txt_to_xml function and rename with numbers (e.g 0.xml)
for x in range(FILE_NUM):
    fixName = str(x) + ".txt"
    txt_to_xml(fixName)

# loop through Number.xml files and scrape relevant stock data
masterDictionary = {}
for x in range(FILE_NUM):
    fileName = str(x) + ".xml"
    tree = ET.parse(fileName)
    root = tree.getroot()
    count = 0
    # Loop through individual companies in file and place company info into masterDictionary(key=name, value=list of ints representing data through time
    # (e.g shares per quarter since Q2 2018))
    for company in root.findall("infoTable"):
        name = company.find('nameOfIssuer').text
        #share = company.find('shrsOrPrnAmt/sshPrnamt').text
        value = company.find('value').text

        fillList = masterDictionary.get(name, [0]*FILE_NUM)
        fillList[FILE_NUM-x-1] = int(value)*1000
        masterDictionary[name] = fillList

# Prints the entire dictionary for some visual clues that this program actually worked
print(masterDictionary)


#Prints Dictionary to .csv file
with open(compName +'.csv', 'w', newline='') as file:
    writer = csv.writer(file)

    #Header row (Will have to update in 2021) gets written
    headerRow = ["Company", "Q1 2018","Q2 2018", "Q3 2018", "Q4 2018", "Q1 2019", "Q2 2019", "Q3 2019", "Q4 2019", "Q1 2020", "Q2 2020", "Q3 2020", "Q4 2020", "Q1 2021", "Q2 2021", "Q3 2021", "Q4 2021"]
    writer.writerow(headerRow[0:FILE_NUM+1])

    #Prints the data rows into the csv
    for key in masterDictionary:
        tempList = masterDictionary[key]
        tempList.insert(0, key)
        writer.writerow(tempList)

