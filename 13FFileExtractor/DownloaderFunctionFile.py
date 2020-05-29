import requests
from bs4 import BeautifulSoup
import urllib.request
import os
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




