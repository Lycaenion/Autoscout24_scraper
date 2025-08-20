import pickle
import time

from selenium.common import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait

import project_db
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
    driver.implicitly_wait(45)
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
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == 'complete'
        )

        url = driver.current_url

        result = project_db.check_if_post_exists_in_db(url)

        if result is False:
            webpage = 1
            print(webpage)

            brand_element = driver.find_element(By.CLASS_NAME, 'StageTitle_makeModelContainer__RyjBP')
            brand = brand_element.text

            model_ver_element = driver.find_element(By.CLASS_NAME, 'StageTitle_modelVersion__Yof2Z')
            model_ver = model_ver_element.text

            price_element = driver.find_element(By.CLASS_NAME, 'PriceInfo_price__XU0aF')
            temp_price = price_element.text

            if len(temp_price) > 8:
                price = temp_price[:-1]
                price = price.strip('€')
                price = price.replace(' ', '')
                price = price.replace(',', '')
                int_price = int(price)
            else:
                price = temp_price
                price = price.strip('€')
                price = price.replace(' ', '')
                price = price.replace(',', '')
                int_price = int(price)


            year_element = driver.find_element(By.XPATH, '//*[@id="listing-history-section"]/div/div[2]/dl/dd[2]')
            year = year_element.text

            try:
                location_element = driver.find_element(By.XPATH, '//*[@id="vendor-and-cta-section"]/div/div[1]/div/div[2]/div[1]/div[2]/div[2]/a')
            except NoSuchElementException:
                location_element = None
                with open('page.html', 'w', encoding='utf-8') as file:
                    file.write(driver.page_source)

            if location_element is not None:
                location = location_element.text
            else:
                location = None

            try:
                fuel_element = driver.find_element(By.XPATH, '//*[@id="environment-details-section"]/div/div[2]/dl/dd[2]')
            except NoSuchElementException:
                fuel_element = None
                with open('page.html', 'w', encoding='utf-8') as file:
                    file.write(driver.page_source)

            if fuel_element is not None:
                fuel = fuel_element.text
            else:
                fuel = None

            engine_power_element = driver.find_element(By.XPATH, '//*[@id="technical-details-section"]/div/div[2]/dl/dd[1]')
            engine_power = engine_power_element.text

            gearbox_element = driver.find_element(By.XPATH, '//*[@id="technical-details-section"]/div/div[2]/dl/dd[2]')
            gearbox = gearbox_element.text

            mileage_element = driver.find_element(By.XPATH, '//*[@id="listing-history-section"]/div/div[2]/dl/dd[1]/div')
            mileage = mileage_element.text

            project_db.add_to_db(url,webpage, brand, model_ver, year, int_price, mileage, gearbox, fuel, engine_power, location)
            driver.close()
            driver.switch_to.window(base_window)
        else:
            driver.close()
            driver.switch_to.window(base_window)

if __name__ == "__main__":
    main()