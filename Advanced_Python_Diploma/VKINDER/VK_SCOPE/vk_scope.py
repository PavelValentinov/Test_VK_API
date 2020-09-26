import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Tuple

import vk_api
from tqdm import tqdm

from DB.database import Connect, User, City, Region, Query, DatingUser


class VKAuth:
    # FIXME: если нет токена, то нужно закомментировать строку 17, а строки 19-26 раскомментировать
    #        и указать свои данные для авторизации
    vk_session = vk_api.VkApi(token=os.getenv("VK_USER_TOKEN"))

    # username: str = os.getenv("VK1_USER_LOGIN")  # FIXME: укажите свой логин вместо os.getenv("VK_USER_LOGIN")
    # password: str = os.getenv("VK_USER_PASS")  # FIXME: укажите свой пароль вместо os.getenv("VK_USER_PASS")
    # scope = 'users,notify,friends,photos,status,notifications,offline,wall,audio,video'
    # vk_session = vk_api.VkApi(username, password, scope=scope, api_version='5.124')
    # try:
    #     vk_session.auth(token_only=True)
    # except vk_api.AuthError as error_msg:
    #     print(error_msg)

    def __init__(self):
        pass

    def _get_countries(self) -> List[Dict[str, Any]]:
        """Служебный метод для сбора всех стран.
        Используется для заполнения БД."""

        print('Страны')
        countries = []
        countries_query = self.vk_session.method('database.getCountries',
                                                 values={'need_all': 1, 'count': 1000})['items']

        for country in countries_query:
            new_dic = {'model': 'country', 'fields': country}
            countries.append(new_dic)

        with open('../DB/Fixtures/countries.json', 'w', encoding='utf-8') as f:
            json.dump(countries, f)
        return countries_query

    def _get_regions(self, countries: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Служебный метод для сбора всех регионов во всех странах.
        Используется для заполнения БД.
        По факту ВК отдаёт не все регионы."""

        print('Регионы')
        regions = [{'model': 'region', 'fields': {"id": 1, "title": "Москва город", "country_id": 1}},
                   {'model': 'region', 'fields': {"id": 2, "title": "Санкт-Петербург город", "country_id": 1}}]

        if not countries:
            try:
                with open('../DB/Fixtures/countries.json', 'r', encoding='utf-8') as f:
                    countries = json.load(f)
            except (FileNotFoundError, FileExistsError):
                countries = self._get_countries()
        for country in countries:
            print(".", end='')
            time.sleep(0.3)
            regions_quantity = \
                self.vk_session.method('database.getRegions', values={'country_id': country['fields']['id'],
                                                                      'count': 100})['count']
            if not regions_quantity:
                continue
            else:
                time.sleep(0.3)
                search_values = {'country_id': country['fields']['id'], 'count': 100}
                regions_quantity = self.vk_session.method('database.getRegions', values=search_values)['count']
                if regions_quantity > 100:
                    queries = regions_quantity // 100 + 1
                    values = {'country_id': country['fields']['id'], 'count': 100, 'offset': 0}
                    for query in tqdm(range(queries), desc=f"Обходим города в стране {country['fields']['title']}"):
                        time.sleep(0.3)
                        values['offset'] = 100 * query
                        regions_list = self.vk_session.method('database.getRegions', values=values)['items']
                        if regions_list:
                            for region in regions_list:
                                region.update({'country_id': country['fields']['id']})
                                new_dic = {'model': 'region', 'fields': region}
                                regions.append(new_dic)
                        else:
                            continue



                else:
                    regions_list = self.vk_session.method('database.getRegions', values=search_values)['items']
                    if regions_list:
                        for region in regions_list:
                            region.update({'country_id': country['fields']['id']})
                            new_dic = {'model': 'region', 'fields': region}
                            regions.append(new_dic)
                    else:
                        continue

        with open('../DB/Fixtures/regions.json', 'w', encoding='utf-8') as f:
            json.dump(regions, f)
        return regions

    def _get_cities(self, countries: List[Dict[str, Any]] = None,
                    regions: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Служебный метод для сбора всех городов во всех странах.
        Используется для заполнения БД.
        По факту ВК отдаёт не все города. Уроды."""

        print('Города')
        cities = []
        # if not countries:
        #     try:
        #         with open('../DB/Fixtures/countries.json', 'r', encoding='utf-8') as f:
        #             countries = json.load(f)
        #     except (FileNotFoundError, FileExistsError):
        #         countries = self._get_regions()
        # for country in countries:
        #     print(".", end='')
        #     time.sleep(0.3)
        #     search_values = {'country_id': country['fields']['id'], 'need_all': 1, 'count ': 1000}
        #     cities_quantity = self.vk_session.method('database.getCities', values=search_values)['count']
        #
        #     if not cities_quantity:
        #         continue
        #     elif cities_quantity > 1000:
        #         queries = cities_quantity // 1000 + 1
        #         values = {'country_id': country['fields']['id'], 'offset': 0, 'need_all': 1, 'count ': 1000}
        #         for query in tqdm(range(queries), desc=f"Обходим города в стране {country['fields']['title']}"):
        #             time.sleep(0.3)
        #             values['offset'] = 1000 * query
        #             cities_list = self.vk_session.method('database.getCities', values=values)['items']
        #             if cities_list:
        #                 for city in cities_list:
        #                     city.update({'region_id': None})
        #                     new_dic = {'model': 'city', 'fields': city}
        #                     cities.append(new_dic)
        #             else:
        #                 continue
        #     else:
        #         time.sleep(0.3)
        #         cities_list = self.vk_session.method('database.getCities', values=search_values)['items']
        #         if cities_list:
        #             for city in cities_list:
        #                 city.update({'region_id': None})
        #                 new_dic = {'model': 'city', 'fields': city}
        #                 cities.append(new_dic)
        #         else:
        #             continue

        if not regions:
            try:
                with open('../DB/Fixtures/regions.json', 'r', encoding='utf-8') as f:
                    regions = json.load(f)
            except (FileNotFoundError, FileExistsError):
                regions = self._get_regions()
        for region in regions:
            print(".", end='')
            time.sleep(0.3)
            search_values = {'country_id': region['fields']['country_id'], 'region_id': region['fields']['id'],
                             'need_all': 1, 'count ': 100}
            cities_quantity = self.vk_session.method('database.getCities', values=search_values)['count']

            if not cities_quantity:
                continue
            elif cities_quantity > 100:
                queries = cities_quantity // 100 + 1
                values = {'country_id': region['fields']['country_id'], 'region_id': region['fields']['id'],
                          'offset': 0, 'need_all': 1, 'count ': 100}
                for query in tqdm(range(queries), desc=f"Обходим города в регионе {region['fields']['title']}"):
                    time.sleep(0.3)
                    values['offset'] = 100 * query
                    cities_list = self.vk_session.method('database.getCities', values=values)['items']
                    if cities_list:
                        for city in cities_list:
                            city.update({'region_id': region['fields']['id']})
                            new_dic = {'model': 'city', 'fields': city}
                            cities.append(new_dic)
                    else:
                        continue
            else:
                time.sleep(0.3)
                cities_list = self.vk_session.method('database.getCities', values=search_values)['items']
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

    def get_city(self, country_id: int, city_title: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:

        def get_region(country_id: int, region_title: str) -> Dict[str, Any]:
            search_values = {'country_id': country_id, 'q': region_title}
            return self.vk_session.method('database.getRegions', values=search_values)

        search_values = {'country_id': country_id, 'q': city_title, 'need_all': 1}
        city = self.vk_session.method('database.getCities', values=search_values)
        city_items = city['items'][0]
        region_title = city_items['region'].split()[0]
        region = get_region(country_id, region_title)
        region_items = region['items'][0]
        region_items.update({'country_id': country_id})
        city_items['region_id'] = region_items['id']
        return city_items, region_items


# noinspection SpellCheckingInspection
class VKUser(VKAuth, Connect):
    def __init__(self, id: int):
        self.user_id = id
        info = self.get_self_info(self.user_id)
        # print(info)
        self.first_name = info[0].get('first_name')
        self.last_name = info[0].get('last_name')
        self.sex = info[0].get('sex')
        self.city = info[0].get('city')
        self.country = info[0].get('country')
        self.birthday = info[0].get('bdate')
        self.link = 'https://vk.com/' + str(info[0].get('domain'))
        self.insert_self_to_db()

    def get_self_info(self, user_id: int) -> List[Dict[str, Any]]:
        """Метод получения всей необходимой информации о юзере в чате"""
        search_values = {
            'user_id': user_id,
            'fields': 'bdate, city, country, sex, domain, home_town',
            'name_case': 'Nom'
        }
        return self.vk_session.method('users.get', values=search_values)

    def check_city_and_region(self) -> None:
        """Метод проверки наличия города и региона в БД. При отсутствии - собираем и дописываем"""
        if self.select_from_db(City.id, City.id == self.city['id']).first() is None:
            city, region = self.get_city(self.country['id'], self.city['title'])
            if self.select_from_db(Region.id, Region.id == region['id']).first() is None:
                self.insert_to_db(Region, region)
            self.insert_to_db(City, city)

    def insert_self_to_db(self) -> None:
        """ Метод записи в БД информации о юзере из чата """
        fields = {
            'id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.birthday,
            'sex_id': self.sex,
            'city_id': self.city['id'],
            'link': self.link
        }
        # если нового города юзера вдруг нет в БД
        self.check_city_and_region()
        # проверяем юзера на наличие в БД
        if self.select_from_db(User.id, User.id == self.user_id).first() is None:
            self.insert_to_db(User, fields)
        else:
            # проверяем не поменялся ли у юзера его город
            user_db_city = self.select_from_db(User.city_id, User.id == self.user_id).first()[0]
            if user_db_city != self.city['id']:
                self.check_city_and_region()  # если нового города юзера вдруг нет в БД
                self.update_data(User.id, User.id == self.user_id, {User.city_id: self.city['id']})

    def insert_query(self, user_id, search_values) -> int:
        fields = {
            # 'id': start_id,
            'datetime': datetime.utcnow(),
            'sex_id': search_values['sex'],
            'city_id': search_values['city'],
            'age_from': search_values['age_from'],
            'age_to': search_values['age_to'],
            'status_id': search_values['status'],
            'sort_id': search_values['sort'],
            'user_id': user_id
        }
        self.insert_to_db(Query, fields)

        return self.select_from_db(Query.id, Query.id == Query.id).all()[-1][0]

    def search_users(self, vk_user, values: Dict[str, Any] = None) -> int or None:
        """ Метод поиска подходящих пользователей по запросу юзера"""

        search_values = {
            'city': 1,
            'sex': 1,
            'age_from': 33,
            'age_to': 43,
            'status': 6,
            'sort': 1,
            'count': 1000,
            'has_photo': 1,
            'is_closed': 0,
            'can_access_closed': 1,
            'fields': 'id, verified, domain'
        }

        if values:
            search_values.update(values)
        else:
            pass

        users_list = self.vk_session.method('users.search', values=search_values)['items']

        if not users_list:
            return
        query_id = self.insert_query(vk_user.user_id, search_values)
        # pprint(users_list)
        for user in users_list:
            user['vk_id'] = user['id']
            user['city_id'] = search_values['city']
            user['city_title'] = self.select_from_db(City.title, City.id == search_values['city']).first()[0]
            user['link'] = 'https://vk.com/' + user.get('domain')
            user['verified'] = user.get('verified')
            user['user_id'] = vk_user.user_id
            user['query_id'] = query_id

            user.pop('is_closed')
            user.pop('can_access_closed')
            user.pop('track_code')
            user.pop('domain')
            user.pop('id')

            self.insert_to_db(DatingUser, user)
        return len(users_list)


class Dating_User(VKAuth, Connect):
    def __init__(self, user_id: int, first_name: str, last_name: str, birthday: str, vk_link: str, city: str,
                 verified: str):
        super(VKAuth, self).__init__()
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday
        self.link = vk_link
        self.city = city
        self.verified = verified

    def get_photo(self):
        search_values = {'owner_id': self.id, 'album_id': 'profile', 'count': 1000, 'extended': 1,
                         'photo_sizes': 1}
        response = self.vk_session.method('photos.get', values=search_values)
        count_likes = [likes['likes']['count'] for likes in response['items']]
        link_photos = [photo['sizes'][-1]['url'] for photo in response['items']]
        top3_photos = sorted(zip(count_likes, link_photos), reverse=True)[:3]
        return top3_photos


if __name__ == '__main__':
    auth = VKAuth()
    # now = datetime.now()
    # print(now)
    # auth._get_countries()
    # auth._get_regions()
    # auth._get_cities()
    # print(datetime.now() - now)

    # print(user.get_self_info())
    # auth.insert_self_to_db()

    # print(user.search_users())

    # dating = DatingUser(427195814, 'Ярослава', 'Викторианская', '7.7', 'https://vk.com/id427195814')
    # print(dating.get_photo())
