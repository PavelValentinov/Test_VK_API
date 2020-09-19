import json
import os
import time
# from pprint import pprint
from datetime import datetime
from typing import List, Dict, Any

import vk_api
from tqdm import tqdm


class VKAuth:
    username: str = os.getenv("VK_USER_LOGIN")
    password: str = os.getenv("VK_USER_PASS")
    session = vk_api.VkApi(username, password)

    try:
        session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)

    def _get_countries(self) -> List[Dict[str, Any]]:
        """Служебный метод для сбора всех стран.
        Используется для заполнения БД."""

        print('Страны')
        countries = []
        countries_query = self.session.method('database.getCountries', values={'need_all': 1, 'count': 1000})['items']

        for country in countries_query:
            new_dic = {'model': 'country', 'fields': country}
            countries.append(new_dic)

        with open('../DB/Fixtures/countries.json', 'w', encoding='utf-8') as f:
            json.dump(countries, f)
        return countries_query

    def _get_regions(self, countries: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Служебный метод для сбора всех регионов во всех странах.
        Используется для заполнения БД."""

        print('Регионы')
        regions = []
        if not countries:
            try:
                with open('../DB/Fixtures/countries.json', 'r', encoding='utf-8') as f:
                    countries = json.load(f)
            except:
                countries = self._get_countries()
        for country in countries:
            print(".", end='')
            time.sleep(0.3)
            regions_quantity = self.session.method('database.getRegions', values={'country_id': country['fields']['id'],
                                                                                  'count': 1000})['count']
            if not regions_quantity:
                continue
            else:
                time.sleep(0.3)
                region_list = self.session.method('database.getRegions', values={'country_id': country['fields']['id'],
                                                                                 'count': 1000})['items']
                if region_list:
                    for region in region_list:
                        region.update({'country_id': country['fields']['id']})
                        new_dic = {'model': 'region', 'fields': region}
                        regions.append(new_dic)

                else:
                    continue

        regions.append({'model': 'region', 'fields': {"id": 1, "title": "Москва город", "country_id": 1}})
        regions.append({'model': 'region', 'fields': {"id": 2, "title": "Санкт-Петербург город", "country_id": 1}})

        with open('../DB/Fixtures/regions.json', 'w', encoding='utf-8') as f:
            json.dump(regions, f)
        return regions

    def _get_cities(self, countries: List[Dict[str, Any]] = None, regions: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Служебный метод для сбора всех городов во всех странах.
        Используется для заполнения БД."""

        print('Города')
        cities = []
        if not countries:
            try:
                with open('../DB/Fixtures/countries.json', 'r', encoding='utf-8') as f:
                    countries = json.load(f)
            except:
                countries = self._get_regions()
        for country in countries:
            print(".", end='')
            time.sleep(0.3)
            search_values = {'country_id': country['fields']['id'], 'need_all': 1, 'count ': 1000}
            cities_quantity = self.session.method('database.getCities', values=search_values)['count']

            if not cities_quantity:
                continue
            elif cities_quantity > 1000:
                queries = cities_quantity // 1000 + 1
                values = {'country_id': country['fields']['id'], 'offset': 0, 'need_all': 1, 'count ': 1000}
                for query in tqdm(range(queries), desc=f"Обходим города в стране {country['fields']['title']}"):
                    time.sleep(0.3)
                    values['offset'] = 1000 * query
                    cities_list = self.session.method('database.getCities', values=values)['items']
                    if cities_list:
                        for city in cities_list:
                            city.update({'region_id': None})
                            new_dic = {'model': 'city', 'fields': city}
                            cities.append(new_dic)
                    else:
                        continue
            else:
                time.sleep(0.3)
                cities_list = self.session.method('database.getCities', values=search_values)['items']
                if cities_list:
                    for city in cities_list:
                        city.update({'region_id': None})
                        new_dic = {'model': 'city', 'fields': city}
                        cities.append(new_dic)
                else:
                    continue
        if not regions:
            try:
                with open('../DB/Fixtures/regions.json', 'r', encoding='utf-8') as f:
                    regions = json.load(f)
            except:
                regions = self._get_regions()
        for region in regions:
            print(".", end='')
            time.sleep(0.3)
            search_values = {'country_id': region['fields']['country_id'], 'region_id': region['fields']['id'],
                             'need_all': 1, 'count ': 1000}
            cities_quantity = self.session.method('database.getCities', values=search_values)['count']

            if not cities_quantity:
                continue
            elif cities_quantity > 1000:
                queries = cities_quantity // 1000 + 1
                values = {'country_id': region['fields']['country_id'], 'region_id': region['fields']['id'],
                          'offset': 0, 'need_all': 1, 'count ': 1000}
                for query in tqdm(range(queries), desc=f"Обходим города в регионе {region['fields']['title']}"):
                    time.sleep(0.3)
                    values['offset'] = 1000 * query
                    cities_list = self.session.method('database.getCities', values=values)['items']
                    if cities_list:
                        for city in cities_list:
                            city.update({'region_id': region['fields']['id']})
                            new_dic = {'model': 'city', 'fields': city}
                            cities.append(new_dic)
                    else:
                        continue
            else:
                time.sleep(0.3)
                cities_list = self.session.method('database.getCities', values=search_values)['items']
                if cities_list:
                    for city in cities_list:
                        city.update({'region_id': region['fields']['id']})
                        new_dic = {'model': 'city', 'fields': city}
                        cities.append(new_dic)
                else:
                    continue
        with open('../DB/Fixtures/cities.json', 'w', encoding='utf-8') as f:
            json.dump(cities, f)
        return cities


class VKUser(VKAuth):

    def get_self_name(self, user_id: str = '427195814') -> str:
        return self.session.method('users.get', values={'user_id': user_id})[0]['first_name']

    def get_self_info(self, user_id: str = '427195814') -> List[Dict[str, Any]]:
        search_values = {
            'user_id': user_id,
            'fields': ['birth_year', 'city', 'sex']
        }
        return self.session.method('users.get', values=search_values)

    def search_users(self, values: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if values:
            search_values = values
        else:
            search_values = {
                'count': 1000,
                'city': 1,
                'sex': 1,
                'age_from': 33,
                'age_to': 43,
                'has_photo': 1,
                'status': 6,
                'sort': 1,
                'is_closed': 0,
                'can_access_closed': 1,
                'fields': ['id', 'verified', 'bdate', 'domain', 'city', 'status']
            }
        users_list = self.session.method('users.search', values=search_values)['items']
        return users_list


class DatingUser(VKAuth):
    def __init__(self, user_id: int, first_name: str, last_name: str, birthday: str, vk_link: str):
        super(VKAuth, self).__init__()
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday
        self.link = vk_link

    def get_photo(self):
        search_values = {'owner_id': self.id, 'album_id': 'profile', 'count': 1000, 'extended': 1,
                         'photo_sizes': 1}
        response = self.session.method('photos.get', values=search_values)
        count_likes = [likes['likes']['count'] for likes in response['items']]
        link_photos = [photo['sizes'][-1]['url'] for photo in response['items']]
        top3_photos = sorted(zip(count_likes, link_photos), reverse=True)[:3]
        return top3_photos


if __name__ == '__main__':
    user = VKUser()
    # print(user.get_self_name())
    # print(user.get_self_info())
    # print(user.search_users())
    # user._get_countries()
    now = datetime.now()
    # user._get_countries()
    # user._get_regions()
    user._get_cities()

    print(datetime.now() - now)
    # with open('cities.json', 'r', encoding='utf-8') as f:
    #     all_cities = json.load(f)
    # for city in all_cities:
    #     if "Ростов" in city['title']:
    #         print(city)
    #
    # dating = DatingUser(427195814, 'Ярослава', 'Викторианская', '7.7', 'https://vk.com/id427195814')
    # print(dating.get_photo())
