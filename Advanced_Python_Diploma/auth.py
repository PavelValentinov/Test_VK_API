""" Модуль определяет порядок авторизации и дальнейшей работы с сервисом vk.com"""
import json
import os
import time
from datetime import datetime

import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from tqdm import tqdm

now = int(time.mktime(datetime.now().timetuple()))


class VKAPIAuth:
    """ Класс предназначен для авторизации на сервисе vk.com"""
    ACCESS_TOKEN = ""

    def __init__(self, login=None, password=None):
        self.AUTHORIZE_URL = 'https://oauth.vk.com/authorize'
        self.ACCESS_TOKEN = ''
        self.oath_params = {
            'client_id': 7595057,
            'scope': "users,friends,photos,stories,status,wall,groups,notify",
            # 'scope': "offline",
            'display': 'page',
            'response_type': 'token',
            'v': '5.120',
        }

        self.login = login
        self.password = password
        self.expires_in = 0


        if os.path.exists(os.path.join(os.path.curdir, "access_token.json")):
            with open("access_token.json") as file:
                access_key_dic = json.load(file)
        else:
            access_key_dic = {}

        if access_key_dic:
            if access_key_dic.get("expires_in") > now:
                self.ACCESS_TOKEN = access_key_dic["access_token"]
                self.expires_in = access_key_dic["expires_in"]
                print(f"\nТокен пользователя действителен в течение {int((self.expires_in - now) / 3600)} ч.\n")
            else:
                self.get_token = self.authorize()
                print(f"\nТокен пользователя выдан со сроком действия {self.expires_in} ч.\n")
        else:
            self.get_token = self.authorize()
            print(f"\nТокен пользователя выдан со сроком действия {self.expires_in} ч.\n")



    def authorize(self):
        """Метод получает токен пользователя"""

        def get_token(url):
            access_key_dic = {}
            self.ACCESS_TOKEN = url.split("access_token=")[1].split("&")[0]
            self.expires_in = int(int(url.split("expires_in=")[1].split("&")[0]) / 3600)
            access_key_dic["access_token"] = self.ACCESS_TOKEN
            access_key_dic["granted"] = now
            access_key_dic["expires_in"] = now + self.expires_in * 3600
            with open("access_token.json", "w", encoding="utf-8") as file:
                json.dump(access_key_dic, file)
            return True

        print("\nПолучаем токен пользователя")
        # собираем ссылку для авторизации
        url = requests.get(self.AUTHORIZE_URL, params=self.oath_params).url

        # параметры запуска Selenium
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(ChromeDriverManager().install(), port=443, options=options)

        # процесс авторизации
        driver.get(url)
        login = driver.find_element(By.XPATH, '//*[@id="login_submit"]/div/div/input[6]')
        ActionChains(driver).move_to_element(login).click().perform()

        login.send_keys(self.login)

        password = driver.find_element(By.XPATH, '//*[@id="login_submit"]/div/div/input[7]')
        ActionChains(driver).move_to_element(password).click().perform()

        password.send_keys(self.password)

        enter = driver.find_element(By.XPATH, '//*[@id="install_allow"]')
        ActionChains(driver).move_to_element(enter).click().perform()
        time.sleep(1)

        # получаем ключ доступа из новой ссылки
        url = driver.current_url
        # print(url)

        if "access_token" not in url:
            enter = driver.find_element(By.XPATH, '//*[@id="oauth_wrap_content"]/div[3]/div/div[1]/button[1]')
            ActionChains(driver).move_to_element(enter).click().perform()

        url = driver.current_url
        page = driver.page_source
        driver.close()
        driver.quit()

        if "access_token" in url:
            return get_token(url)
        else:
            return False


if __name__ == '__main__':
    username = 89645338731
    password = 'zaxs83cdRYB'

    auth = VKAPIAuth(login=username, password=password)
    if auth:
        pass
    else:
        print("\nЧто-то пошло не так.")
