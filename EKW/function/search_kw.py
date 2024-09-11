from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def search_kw(browser, kw):
    """browser.find_element(By.ID, 'kodWydzialuInput').send_keys(kw[0])  # Find the search box
    browser.find_element(By.NAME, 'numerKw').send_keys(kw[1])  # Find the search box
    browser.find_element(By.NAME, 'cyfraKontrolna').send_keys(kw[2])  # Find the search box
    browser.find_element(By.NAME, 'wyszukaj').send_keys(Keys.RETURN)  # Find the search box"""

    find_wait(browser, "#kodWydzialuInput").send_keys(kw[0])
    find_wait(browser, "#numerKsiegiWieczystej").send_keys(kw[1])
    find_wait(browser, "#cyfraKontrolna").send_keys(kw[2])
    find_wait(browser, "#wyszukaj").click()


def find_wait(browser, value: str, by: By = By.CSS_SELECTOR, wait_seconds: int = 60):
    """Returns the element found by the given method and value after waiting for it to be present."""
    wdw = WebDriverWait(browser, wait_seconds)
    method = expected_conditions.presence_of_element_located
    return wdw.until(method((by, value)))


if __name__ == "__main__":
    pass