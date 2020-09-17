import json
import os
import time
from dataclasses import dataclass
# from pprint import pprint
from typing import List, Dict, Any

import vk


class VKAuth:
    def __init__(self, username: str, password: str):
        self.username: str = username
        self.password: str = password
        self.app_id: str = '7595057'
        self.version: str = '5.124'
        self.session = vk.AuthSession(self.app_id, self.username, self.password,
                                      scope='users, friends, photos, wall, groups, status, email')
        self.vk = vk.API(self.session)

    def _get_countries(self) -> List[Dict[int, str]]:
        """Служебный метод для сбора всех стран.
        Используется для заполнения БД."""

        print('Страны')
        countries = self.vk.database.getCountries(need_all=1, count=1000, v='5.120')['items']
        with open('countries.json', 'w', encoding='utf-8') as f:
            json.dump(countries, f)
        return countries

    def _get_regions(self, countries) -> List[Dict[int, str]]:
        """Служебный метод для сбора всех регионов во всех странах.
        Используется для заполнения БД."""

        print('Регионы')
        regions = []
        for country in countries:
            print(".", end='')
            time.sleep(0.3)
            regions_quantity = self.vk.database.getRegions(country_id=country['id'], offset=0,
                                                           count=1000, v='5.120')['count']
            if not regions_quantity:
                continue
            elif regions_quantity > 1000:
                queries = regions_quantity // 1000 + 1
                for query in range(queries):

                    time.sleep(0.3)
                    offset = 1000 * query
                    region_list = self.vk.database.getRegions(country_id=country['id'], offset=offset,
                                                              count=1000, v='5.120')['items']
                    if region_list:
                        for region in region_list:
                            region.update({'country_id': country['id']})
                            regions.append(region)
                    else:
                        continue
            else:
                time.sleep(0.4)
                region_list = self.vk.database.getRegions(country_id=country['id'], offset=0,
                                                          count=1000, v='5.120')['items']
                if region_list:
                    for region in region_list:
                        region.update({'country_id': country['id']})
                        regions.append(region)
                else:
                    continue
        with open('regions.json', 'w', encoding='utf-8') as f:
            json.dump(regions, f)
        return regions

    def _get_cities(self, countries) -> List[Dict[str, Any]]:
        """Служебный метод для сбора всех городов во всех странах.
        Используется для заполнения БД."""

        print('Города')
        cities = []
        for country in countries:
            print(".", end='')
            time.sleep(0.3)
            cities_quantity = self.vk.database.getCities(country_id=country['id'], offset=0,
                                                         need_all=1, count=1000, v='5.120')['count']

            if not cities_quantity:
                continue
            elif cities_quantity > 1000:
                queries = cities_quantity // 1000 + 1
                for query in range(queries):
                    time.sleep(0.3)
                    offset = 1000 * query
                    cities_list = self.vk.database.getCities(country_id=country['id'], offset=offset,
                                                             need_all=1, count=1000, v='5.120')['items']
                    if cities_list:
                        for city in cities_list:
                            cities.append(city)
                    else:
                        continue
            else:
                time.sleep(0.4)
                cities_list = self.vk.database.getCities(country_id=country['id'], offset=0,
                                                         need_all=1, count=1000, v='5.120')['items']
                if cities_list:
                    for city in cities_list:
                        cities.append(city)
                else:
                    continue
        with open('cities.json', 'w', encoding='utf-8') as f:
            json.dump(cities, f)
        return cities


class VKUser(VKAuth):
    def get_self_name(self, user_id: str = '427195814') -> str:
        return self.vk.users.get(user_id=user_id, v=self.version)[0]['first_name']

    def get_self_info(self, user_id='427195814') -> List[Dict[str, Any]]:
        return self.vk.users.get(user_ids=user_id, fields=['bdate', 'city', 'sex'], v=self.version)

    def search_users(self):
        users_list = self.vk.users.search(count=1000, offset=0, city=1, sex=1, age_from=18, age_to=25,
                                          has_photo=1, status=1, is_closed=0, can_access_closed=1,
                                          fields=['id', 'bdate', 'domain'], v=self.version)['count']
        if users_list['items']:
            return users_list['items']
        return


@dataclass
class DatingUser(VKAuth):
    user_id: int
    first_name: str
    last_name: str
    birthday: str
    vk_link: str

    def get_photo(self):
        response = self.vk.photos.get(owner_id=self.user_id, album_id='profile', count=1000, extended=1, photo_sizes=1)
        count_likes = [likes['likes']['count'] for likes in response['items']]
        link_photos = [photo['sizes'][-1]['url'] for photo in response['items']]
        top3_photos = sorted(zip(count_likes, link_photos), reverse=True)[:3]
        return top3_photos


# TODO: удалить пароли и явки!
user = VKUser(os.getenv("VK_USER_LOGIN"), os.getenv("VK_USER_PASS"))
# print(user.get_self_name())
# print(user.get_self_info())
# print(user.search_users())
# user._get_regions(user._get_countries())
# user._get_cities(user._get_countries())

# with open('cities.json', 'r', encoding='utf-8') as f:
#     all_cities = json.load(f)
# for city in all_cities:
#     if "Ростов" in city['title']:
#         print(city)
