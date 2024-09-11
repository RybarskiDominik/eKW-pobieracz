from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import time


def search_kw(browser, kw):

    browser = get_driver()
    browser.get('https://przegladarka-ekw.ms.gov.pl/eukw_prz/KsiegiWieczyste/wyszukiwanieKW')

    time.sleep(3)

    elem = browser.find_element(By.ID, 'kodWydzialuInput')  # Find the search box
    elem.send_keys(kw[0])

    elem = browser.find_element(By.NAME, 'numerKw')  # Find the search box
    elem.send_keys(kw[1])

    elem = browser.find_element(By.NAME, 'cyfraKontrolna')  # Find the search box
    elem.send_keys(kw[2])

    elem = browser.find_element(By.NAME, 'wyszukaj')  # Find the search box
    elem.send_keys(Keys.RETURN)

    time.sleep(1)


if __name__ == "__main__":
    from get_driver import get_driver
    kw = " ", " ", " "
    browser = get_driver
    search_kw(browser, kw)