import pickle
import time

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

def main():
    driver = webdriver.Chrome()
    driver.get(AUTOSCOUT24_URL)
    driver.implicitly_wait(20)
    driver.find_element(By.XPATH, '//*[@id="as24-cmp-popup"]/div/div[3]/button[2]').click()
    #save_cookies(driver, AUTOSCOUT24_COOKIES_FILE)
    load_cookies(driver, AUTOSCOUT24_COOKIES_FILE)
    driver.refresh()
    scrape_autoscout(driver)


def scrape_autoscout(driver):
    base_window = driver.window_handles[0]

    items = driver.find_elements(By.CSS_SELECTOR, 'article')
    print(len(items))

    links = []
    for item in items:
        links.append(item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href'))

    for href in links:
        driver.execute_script("window.open('{}');".format(href))
        time.sleep(1)

    for i, link in enumerate(links):
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])
        time.sleep(10)

        title_element = driver.find_element(By.CLASS_NAME, 'StageTitle_makeModelContainer__RyjBP')
        title = title_element.text
        print(title)
        driver.close()
    driver.switch_to.window(base_window)






if __name__ == "__main__":
    main()