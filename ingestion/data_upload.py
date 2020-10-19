import requests
from bs4 import BeautifulSoup
import time
import zipfile
import boto3
import os

def upload_s3(pair,year,month):
    """ Specify filename and upload file to S3 """
	u = 'DAT_ASCII_' + p + '_T_' + y + m + '.csv'
	aws s3 cp '/app/data/DAT_ASCII_{pair}_T_{year}{month}.csv' s3://historical-forex-data/

def downloadzipfile(zipfilefxpair, zipfileyear, zipfilemonth):
    """ Download csv file from histdata.com """
    postuseragent     = 'Mozilla/5.1'
    postorigin        = 'http://www.histdata.com'
    posturl           = postorigin+'/download-free-forex-historical-data/?/'+'ascii/tick-data-quotes/'+zipfilefxpair+'/'+zipfileyear+'/'+zipfilemonth
    targetfolder      = '/app/data/'
    # Get the page and make the soup
    r = requests.get(posturl)
    data = r.text
    soup = BeautifulSoup(data, "lxml")
    table = soup.find("div", style="display:none;")
    try:
        posttk = table.find('input', {'id': 'tk'}).get('value')
    except:
        pass
    try:
        postdate = table.find('input', {'id': 'date'}).get('value')
    except:
        pass
    try:
        postdatemonth = table.find('input', {'id': 'datemonth'}).get('value')
    except:
        pass
    try:
        posttimeframe = table.find('input', {'id': 'timeframe'}).get('value')
    except:
        pass
    try:
        postfxpair = table.find('input', {'id': 'fxpair'}).get('value')
    except:
        pass
    targetfilename='HISTDATA_COM_ASCII_'+postfxpair+'_T_'+posttimeframe+postdatemonth+'.zip'
    targetpathfilename=targetfolder+targetfilename
    resp = requests.post(postorigin+'/get.php',
    data = {'tk': posttk, 'date': postdate, 'datemonth': postdatemonth, 'platform': 'ASCII', 'timeframe': posttimeframe, 'fxpair': postfxpair},
    headers = {'User-Agent': postuseragent, 'Origin': postorigin, 'Referer': posturl})
    # Wait here for the file to download
    result = None
    while result is None:
      with open(targetpathfilename, 'wb') as fpw:
        for chunk in resp.iter_content():
          fpw.write(chunk)
      time.sleep(1)
      result = 1

def extract_zip(pair,year,month):
    """ Unzip the file file """
	base = "HISTDATA_COM_ASCII_"
	u = "HISTDATA_COM_ASCII_" + pair + "_T_T" + year + month + ".zip"
	with zipfile.ZipFile(u,"r") as zip_ref:
		zip_ref.extractall("/app/data")

def main():  
	symbolsub = ["EURGBP"]
	for symbolsubstring in symbolsub:
		for yearsub in range (2010, 2021):
			for monthsub in range(1, 13):
				currencypair = symbolsubstring
				fileyear = str(yearsub)
				filemonth = str(monthsub)
				downloadzipfile(currencypair, fileyear, filemonth)
				extract_zip(currencypair, fileyear, filemonth)
				upload_s3(currencypair,fileyear,filemonth)

if __name__ == '__main__':
	main()