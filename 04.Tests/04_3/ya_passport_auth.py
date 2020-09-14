import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class YaAuth:
    URL = 'https://passport.yandex.ru/auth'

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), port=443, options=self.options)

    def input_login(self):
        self.driver.get(self.URL)
        login = self.driver.find_element(By.XPATH, '//*[@id="passp-field-login"]')
        ActionChains(self.driver).move_to_element(login).click().perform()
        login.send_keys(self.username)
        enter = self.driver.find_element(By.XPATH,
                                         '//*[@id="root"]/div/div/div[2]/div/div/div[2]/div[3]/div/div/div[1]/form/div[3]/button')
        ActionChains(self.driver).move_to_element(enter).click().perform()
        time.sleep(1)

        return self.driver.current_url

    def input_pass(self):
        password = self.driver.find_element(By.XPATH, '//*[@id="passp-field-passwd"]')
        ActionChains(self.driver).move_to_element(password).click().perform()
        password.send_keys(self.password)
        enter = self.driver.find_element(By.XPATH,
                                         '//*[@id="root"]/div/div/div[2]/div/div/div[2]/div[3]/div/div/form/div[3]/button')
        ActionChains(self.driver).move_to_element(enter).click().perform()
        time.sleep(1)

        return self.driver.current_url

    def close(self):
        self.driver.close()
        self.driver.quit()
        return 'CLOSED'


if __name__ == '__main__':
    login = input('login: ')
    password = input('password: ')
    auth = YaAuth(login, password)

    auth.input_login()
    auth.input_pass()
    auth.close()
