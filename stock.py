class Stock:
   'Common base class for all stocks'
   stockCount = 0

   def __init__(self, company, symbol, currentPrice, marketCap, divAmount, divYield, returns):
      self.company = company
      self.symbol = symbol
      self.currentPrice = currentPrice
      self.marketCap = marketCap
      self.divAmount = divAmount
      self.divYield = divYield
      self.returns = returns
      Stock.stockCount += 1

   def displayCount(self):
     print "Total Players %d" % Stock.stockCount

   def displayStock(self):
      print "Company: ", self.company,  ", Ticker Symbol: ", self.symbol
