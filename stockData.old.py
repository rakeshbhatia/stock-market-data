"""Script to collect and present stock market data for Nasdaq, S&P 500, and Dow 30 indexes."""
import os
import sys
import math
import csv
import time
import itertools
import bisect
import bs4
from bs4 import BeautifulSoup
import urllib2
import string

import stock
from stock import Stock

csv.register_dialect(
    'mydialect',
    delimiter = ',',
    quotechar = '"',
    doublequote = True,
    skipinitialspace = True,
    lineterminator = '\r\n',
    quoting = csv.QUOTE_MINIMAL)

def createNasdaqDict(inFile):
    nasdaqDict = {}
    with open(inFile) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            if row[1].find('iShares') == -1 and row[1].find('iPath') == -1:
                nasdaqDict[row[0]] = row[1]
    return nasdaqDict

def createSpDict(spLink):
    spList = []
    spDict = {}
    spWikiPage = urllib2.urlopen(spLink)
    soup = BeautifulSoup(spWikiPage, 'html.parser')

    #Store the list of s&p 500 components
    for a in soup.findAll('table', attrs={'class': 'wikitable sortable'}, limit=1):
        for b in a.findAll('tr'):
            count = 1
            for c in b.findAll('td', limit=2):
                if count == 1:
                    stockSymbol = c.text
                    count += 1
                elif count == 2:
                    companyName = c.text
                    print 'c.text = ' + c.text
                    spDict[stockSymbol] = companyName
                    count = 1

    return spDict

def createDowDict(dowLink):
    dowList = []
    dowDict = {}
    dowWikiPage = urllib2.urlopen(dowLink)
    soup = BeautifulSoup(dowWikiPage, 'html.parser')

    #Store the list of dow 30 components
    for a in soup.findAll('table', attrs={'class': 'wikitable sortable'}):
        for b in a.findAll('tr'):
            count = 1
            for c in b.findAll('td', limit=3):
                if count == 1:
                    companyName = c.text
                    count += 1
                elif count == 2:
                    count += 1
                elif count == 3:
                    stockSymbol = c.text
                    dowDict[stockSymbol] = companyName
                    count = 1

    return dowDict

def queryStockSymbol(stockSymbol, companyName):
    #create a new beautiful soup object that can query the ticker symbol
    stockLink = 'https://finance.yahoo.com/quote/%s/?p=%s' % (stockSymbol, stockSymbol)
    stockPage = urllib2.urlopen(stockLink)
    soup = BeautifulSoup(stockPage, 'html.parser')

    stockData = []
    for a in soup.findAll('div', attrs={'data-test': 'left-summary-table'}):
        for b in a.findAll('td'):
            print b.text
            stockData.append(b.text)

    for a in soup.findAll('div', attrs={'data-test': 'right-summary-table'}):
        for b in a.findAll('td'):
            print b.text
            stockData.append(b.text)

    for i in xrange(0, len(stockData)):
        if stockData[i] == 'Previous Close':
            stockPriceStr = stockData[i+1].replace(',', '')
            if stockPriceStr != 'N/A':
                stockPrice = float(stockPriceStr)
            else:
                stockPrice = -1
        elif stockData[i] == 'Yield':
            return None
        elif stockData[i] == 'Market Cap':
            stockMarketCapStr = stockData[i+1].strip('B')
            stockMarketCapStr = stockMarketCapStr.strip('M')
            if stockMarketCapStr != 'N/A':
                stockMarketCap = float(stockMarketCapStr)
            else:
                stockMarketCap = -1
        elif stockData[i] == 'Dividend & Yield':
            divAmountStr = stockData[i+1].split(' (')[0]
            divYieldStr = stockData[i+1].split('(')[1].strip('%)')
            if divAmountStr != 'N/A':
                divAmount = float(divAmountStr)
                divYield = float(divYieldStr)
                #divYieldStr = divYieldStr + '%'
            else:
                divAmount = -1
                divYield = -1

    #dowDict = {}
    prevYearReturnLink = 'https://finance.yahoo.com/quote/%s/key-statistics?p=%s' % (stockSymbol, stockSymbol)
    prevYearReturnPage = urllib2.urlopen(prevYearReturnLink)
    soup = BeautifulSoup(prevYearReturnPage, 'html.parser')

    for a in soup.findAll('table', attrs={'class': 'table-qsp-stats Mt(10px)'}):
        for b in a.findAll('td', limit=4):
            print b.text
            prevYearReturnBlock.append(b.text)
            #for c in b.find('span'):
            #    if c.text == '52-Week Change':


    prevYearReturn = 0
    newStock = Stock(companyName, stockSymbol, stockPrice, stockMarketCap, divAmount, divYield, prevYearReturn)
    return newStock

    '''elif stockData[i] == '52 Week Range':
        prevPriceStr = stockData[i+1].split(' - ')[0].replace(',', '')
        currPriceStr = stockData[i+1].split(' - ')[1].replace(',', '')
        if prevPriceStr != 'undefined' and currPriceStr != 'undefined':
            prevPrice = float(prevPriceStr)
            currPrice = float(currPriceStr)
            prevYearReturn = ((currPrice - prevPrice) / (prevPrice)) * 100
            #prevYearReturnStr = str(prevYearReturn) + '%'
        else:
            prevPrice = -1
            currPrice = -1
            prevYearReturn = -1'''
    #return None

def createStockList():
    myStockSymbolList = []
    myStockList = []

    myNasdaqFile = '../docs/dividend-stocks-nasdaq.csv'
    myNasdaqDict = createNasdaqDict(myNasdaqFile)
    #mySpDict = createSpDict('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    #myDowDict = createDowDict('https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average#Components')

    myCount = 0
    for key, value in myNasdaqDict.items():
        print key + ', ' + value
        myStock = queryStockSymbol(key, value)
        if myStock != None:
            myStockList.append(queryStockSymbol(key, value))
            myCount += 1
        if myCount == 3:
            break

    '''for key, value in mySpDict.items():
        print key + ', ' + value
        myStockList.append(queryStockSymbol(key, value))

    for key, value in myDowDict.items():
        print key + ', ' + value
        myStockList.append(queryStockSymbol(key, value))'''

    myStockList.sort(key=lambda stock: stock.divYield, reverse=True)

    #mySize = len(myStockList)
    #for i in xrange(0, mySize):
    #    print 'Company: ' + myStockList[i].company + ' Symbol: ' + myStockList[i].symbol + ' Yield: ' + str(myStockList[i].divYield)

    return myStockList

def fromDictToCSV():

    headings = ['Company','Symbol','Current Price','Market Cap','Dividend', 'Yield', '52-Week Return']
    myNewStockList = createStockList()
    myNewStockData = []
    for i in xrange(0, len(myNewStockList)):
        myNewDict = {}
        myNewDict['Company'] = myNewStockList[i].company
        myNewDict['Symbol'] = myNewStockList[i].symbol
        myNewDict['Current Price'] = myNewStockList[i].currentPrice
        myNewDict['Market Cap'] = myNewStockList[i].marketCap
        myNewDict['Dividend'] = myNewStockList[i].divAmount
        if myNewStockList[i].divYield != -1:
            myNewDict['Yield'] = str(myNewStockList[i].divYield) + '%'
        else:
            myNewDict['Yield'] = '-1'
        if myNewStockList[i].returns != -1:
            myNewDict['52-Week Return'] = str(myNewStockList[i].returns) + '%'
        else:
            myNewDict['52-Week Return'] = '-1'
        myNewStockData.append(myNewDict)

    try:
        with open('../docs/nasdaq-dividend-stocks-sorted.csv', "wb") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headings, dialect='excel', delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            for data in myNewStockData:
                writer.writerow(data)

    except IOError as (errno, strerror):
        print("I/O error({0}): {1}".format(errno, strerror))

    return

def main():
    #mySpLink = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    #myDowLink = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average#Components'
    #myNasdaqFile = '../docs/dividend-stocks-nasdaq'
    #createSpList(mySpLink)
    #createDowList(myDowLink)
    #createNasdaqList(myNasdaqFile)
    #pass #path for the current file
    #currentPath = os.path.dirname(__file__)
    #global filepath
    #filePath = os.path.abspath(os.path.join(currentPath, os.pardir,os.pardir,'data'))
    fromDictToCSV()
    #queryStockSymbol('GOOG')

if __name__ == '__main__':
    sys.exit(main())