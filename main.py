import pickle
import time
from dataclasses import dataclass
from typing import Optional
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import project_db

AUTOSCOUT24_URL = "https://www.autoscout24.com/lst?atype=C&body=4%2C5%2C12&cy=D%2CA%2CB%2CE%2CF%2CI%2CL%2CNL&damaged_listing=exclude&desc=0&fregfrom=2020&powertype=kw&priceto=30000&search_id=1pm3o8dklez&sort=standard&source=homepage_search-mask&ustate=N%2CU"
AUTOSCOUT24_COOKIES_FILE = 'cookies/autoscout24.pkl'


@dataclass
class CarData:
    url: str
    brand: str
    model_ver: str
    price: int
    year: str
    location: Optional[str]
    fuel: Optional[str]
    engine_power: str
    gearbox: str
    mileage: str


class Autoscout24Scraper:
    def __init__(self, url: str, cookies_file: str):
        self.url = url
        self.cookies_file = cookies_file
        self.driver = None
        self.base_window = None

    def setup_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(self.url)

        try:
            selectors = [
                (By.CLASS_NAME, 'sc-btn-primary'),
                (By.CLASS_NAME, 'privacy-consent-accept'),
                (By.CSS_SELECTOR, '[data-testid="consent-button"]'),
                (By.XPATH, '//button[contains(text(), "Accept All")]'),
            ]

            for by, selector in selectors:
                try:
                    cookie_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    cookie_button.click()
                    break
                except:
                    continue

            self.load_cookies()
            self.driver.refresh()
            self.base_window = self.driver.window_handles[0]
        except Exception as e:
            print(f"Error setting up driver: {e}")
            self.driver.quit()
            raise

    def load_cookies(self):
        try:
            with open(self.cookies_file, 'rb') as f:
                cookies = pickle.load(f)
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        except Exception as e:
            print(f"Error loading cookies: {e}")

    def extract_car_data(self) -> Optional[CarData]:
        try:
            wait = WebDriverWait(self.driver, 10)
            brand = wait.until(EC.presence_of_element_located(
                (By.CLASS_NAME, 'StageTitle_makeModelContainer__RyjBP'))).text
            model_ver = self.driver.find_element(By.CLASS_NAME, 'StageTitle_modelVersion__Yof2Z').text
            price_text = self.driver.find_element(By.CLASS_NAME, 'PriceInfo_price__XU0aF').text
            if len(price_text) > 8:
                price_text = price_text[:-1]
            price = int(price_text.strip('€').replace(' ', '').replace(',', ''))

            year = self.driver.find_element(By.XPATH, '//*[@id="listing-history-section"]/div/div[2]/dl/dd[2]').text

            try:
                location_element = self.driver.find_element(By.XPATH, '//*[@id="vendor-and-cta-section"]/div/div[1]/div/div[2]/div[1]/div[2]/div[2]/a')
            except NoSuchElementException:
                location_element = None

            if location_element is not None:
                location = location_element.text
            else:
                location = None

            try:
                fuel_element = self.driver.find_element(By.XPATH, '//*[@id="environment-details-section"]/div/div[2]/dl/dd[2]')
            except NoSuchElementException:
                fuel_element = None
            if fuel_element is not None:
                fuel = fuel_element.text
            else:
                fuel = None

            engine_power = self.driver.find_element(By.XPATH, '//*[@id="technical-details-section"]/div/div[2]/dl/dd[1]').text
            gearbox = self.driver.find_element(By.XPATH, '//*[@id="technical-details-section"]/div/div[2]/dl/dd[2]').text
            mileage = self.driver.find_element(By.XPATH, '//*[@id="listing-history-section"]/div/div[2]/dl/dd[1]/div').text

            return CarData(
                url=self.driver.current_url,
                brand=brand,
                model_ver=model_ver,
                price=price,
                year=year,
                location=location,
                fuel=fuel,
                engine_power=engine_power,
                gearbox=gearbox,
                mileage=mileage
            )
        except Exception as e:
            print(f"Error extracting car data: {e}")
            return None

    def _safe_find_element(self, xpath: str) -> Optional[str]:
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            return element.text
        except NoSuchElementException:
            return None

    def _safe_find_element_class(self, selector: str) -> Optional[str]:
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.text
        except NoSuchElementException:
            return None

    def scrape(self):
        self.setup_driver()
        items = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article'))
        )
        links = [item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href') for item in items]

        batch_size = 5
        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]
            self._process_batch(batch)
        self.driver.quit()

    def _process_batch(self, batch):
        for href in batch:
            self.driver.execute_script("window.open('{}');".format(href))
            time.sleep(0.5)

        for _ in batch:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            WebDriverWait(self.driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == 'complete'
            )

            if 'autoscout24' not in self.driver.current_url:
                self.driver.close()
                continue

            if not project_db.check_if_post_exists_in_db(self.driver.current_url):
                car_data = self.extract_car_data()
                if car_data:
                    project_db.add_to_db(
                        car_data.url,
                        'Autoscout24',
                        car_data.brand,
                        car_data.model_ver,
                        car_data.year,
                        car_data.price,
                        car_data.mileage,
                        car_data.gearbox,
                        car_data.fuel,
                        car_data.engine_power,
                        car_data.location
                    )

            self.driver.close()
            self.driver.switch_to.window(self.base_window)


def main():
    scraper = Autoscout24Scraper(AUTOSCOUT24_URL, AUTOSCOUT24_COOKIES_FILE)
    scraper.scrape()


if __name__ == '__main__':
    main()