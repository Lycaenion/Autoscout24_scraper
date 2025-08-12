import pickle

from selenium import webdriver
from selenium.webdriver.common.by import By


AUTOSCOUT24_URL = "https://www.autoscout24.com/lst?atype=C&body=4%2C5%2C12&cy=D%2CA%2CB%2CE%2CF%2CI%2CL%2CNL&damaged_listing=exclude&desc=0&fregfrom=2020&powertype=kw&priceto=30000&search_id=1pm3o8dklez&sort=standard&source=homepage_search-mask&ustate=N%2CU"
AUTOSCOUT24_COOKIES_FILE = 'cookies/autoscout24.pkl'

def save_cookies(driver, filename):
    with open(filename, 'wb') as f:
        pickle.dump(driver.get_cookies(), f)
        print("Cookies saved to " + filename)

def load_cookies(driver,filename):
    with open(filename, 'rb') as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
        print("Cookies loaded")

def scrape():
    driver = webdriver.Chrome()
    driver.get(AUTOSCOUT24_URL)
    #save_cookies(driver, AUTOSCOUT24_COOKIES_FILE)
    driver.implicitly_wait(20)
    driver.find_element(By.XPATH, '//*[@id="as24-cmp-popup"]/div/div[3]/button[2]').click()
    load_cookies(driver, AUTOSCOUT24_COOKIES_FILE)
    driver.refresh()


if __name__ == "__main__":
    scrape()