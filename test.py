from selenium import webdriver
import time
driver = webdriver.PhantomJS(executable_path='')
driver.get("https://finance.yahoo.com/quote/LMRK/key-statistics?p=LMRK") time.sleep(3)
print(driver.find_element_by_id("reactid").text)
driver.close()
