"""Задача №1
У Яндекс.Диска есть очень удобное и простое API. Для описания всех его методов существует Полигон.
Нужно написать программу, которая принимает на вход путь до файла на компьютере и сохраняет на Яндекс.Диск с таким же именем.

Все ответы приходят в формате json;
Загрузка файла по ссылке происходит с помощью метода put и передачи туда данных;
Токен можно получить кликнув на полигоне на кнопку "Получить OAuth-токен".
HOST: https://cloud-api.yandex.net:443

Важно: Токен публиковать в github не нужно, переменную для токена нужно оставить пустой!"""


import requests as r
import os


class YaUploader:
    def __init__(self, file_path: str = ''):
        self.token = os.getenv('YA_DISK_TOKEN')
        self.file_path = file_path
        if not file_path:
            self.folder_name = 'test_folder'
        else:
            self.folder_name = file_path
        self.URL = f"https://cloud-api.yandex.net/v1/disk/resources?path={self.folder_name}"
        self.headers = {"port": "443", "Authorization": f"OAuth {self.token}"}

    def get_status_code(self):
        """метод получает статус-код ответа на запрос"""
        return r.get(self.URL, headers=self.headers).status_code

    def create_folder(self):
        """метод создает папку на яндекс.диске с таким же именем как и в self.file_path"""
        put = r.put(self.URL, headers=self.headers)
        try:
            return put.status_code, put.json()["message"]
        except KeyError:
            return put.status_code, put.json()["href"]

    def remove_folder(self):
        """метод удаляет папку на яндекс.диске с таким же именем как и в self.file_path"""
        param = {"permanently": "true"}
        put = r.delete(self.URL, headers=self.headers, params=param)
        return put.status_code

if __name__ == '__main__':
    pass
