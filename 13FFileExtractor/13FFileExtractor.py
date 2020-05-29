import xml.etree.ElementTree as ET
import csv
import os
from ImporterFunctionFile import importer
from RemoverFunctionFile import txt_to_xml


#How many quarters we want to go back
FILE_NUM=10
# Enter CIK number of Money Manager you want to get info on
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
with open('test.csv', 'w', newline='') as file:
    writer = csv.writer(file)

    #Header row (Will have to update in 2021) gets written
    headerRow = ["Company", "Q1 2018","Q2 2018", "Q3 2018", "Q4 2018", "Q1 2019", "Q2 2019", "Q3 2019", "Q4 2019", "Q1 2020", "Q2 2020", "Q3 2020", "Q4 2020", "Q1 2021", "Q2 2021", "Q3 2021", "Q4 2021"]
    writer.writerow(headerRow[0:FILE_NUM+1])

    #Prints the data rows into the csv
    for key in masterDictionary:
        tempList = masterDictionary[key]
        tempList.insert(0, key)
        writer.writerow(tempList)

