import json
import os
import time
# from pprint import pprint
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
        countries = self.session.method('database.getCountries', values={'need_all': 1, 'count': 1000})['items']
        with open('countries.json', 'w', encoding='utf-8') as f:
            json.dump(countries, f)
        return countries

    def _get_regions(self, countries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Служебный метод для сбора всех регионов во всех странах.
        Используется для заполнения БД."""

        print('Регионы')
        regions = []
        for country in countries:
            print(".", end='')
            time.sleep(0.3)
            regions_quantity = self.session.method('database.getRegions', values={'country_id': country['id'],
                                                                                  'count': 1000})['count']
            if not regions_quantity:
                continue
            else:
                time.sleep(0.3)
                region_list = self.session.method('database.getRegions', values={'country_id': country['id'],
                                                                                 'count': 1000})['items']
                if region_list:
                    for region in region_list:
                        region.update({'country_id': country['id']})
                        regions.append(region)
                else:
                    continue
        with open('regions.json', 'w', encoding='utf-8') as f:
            json.dump(regions, f)
        return regions

    def _get_cities(self, countries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Служебный метод для сбора всех городов во всех странах.
        Используется для заполнения БД."""

        print('Города')
        cities = []
        for country in countries:
            print(".", end='')
            time.sleep(0.3)
            search_values = {'country_id': country['id'], 'need_all': 1, 'count ': 1000}
            cities_quantity = self.session.method('database.getCities', values=search_values)['count']

            if not cities_quantity:
                continue
            elif cities_quantity > 1000:
                queries = cities_quantity // 1000 + 1
                values = {'country_id': country['id'], 'offset': 0, 'need_all': 1, 'count ': 1000}
                for query in tqdm(range(queries), desc=f"Обходим города в стране {country['title']}"):
                    time.sleep(0.3)
                    values['offset'] = 1000 * query
                    cities_list = self.session.method('database.getCities', values=values)['items']
                    if cities_list:
                        for city in cities_list:
                            cities.append(city)
                    else:
                        continue
            else:
                time.sleep(0.3)
                cities_list = self.session.method('database.getCities', values=search_values)['items']
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
        return self.session.method('users.get', values={'user_id': user_id})[0]['first_name']

    def get_self_info(self, user_id: str = '427195814') -> List[Dict[str, Any]]:
        search_values = {
            'user_id': user_id,
            'fields': ['bdate', 'city', 'sex']
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
    print(user.get_self_name())
    # print(user.get_self_info())
    # print(user.search_users())
    # user._get_regions(user._get_countries())
    # user._get_cities(user._get_countries())
    # with open('cities.json', 'r', encoding='utf-8') as f:
    #     all_cities = json.load(f)
    # for city in all_cities:
    #     if "Ростов" in city['title']:
    #         print(city)

    dating = DatingUser(427195814, 'Ярослава', 'Викторианская', '7.7', 'https://vk.com/id427195814')
    print(dating.get_photo())
