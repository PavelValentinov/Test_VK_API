from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from auth import VKAPIAuth

# class User:
#     """Класс определяет методы работы с сервисами vk.com"""
#
#     def __init__(self, _id: int):
#         self.id = _id
#         self.URL = 'https://vk.com/id'
#         self.API_URL = 'https://api.vk.com/method/'
#         self.params = {
#             'access_token': VKAPIAuth.ACCESS_TOKEN,
#             'v': '5.120'
#         }
#         self.methods = {
#             'users': {'get': 'users.get?'},
#             'friends': {'get': 'friends.get?',
#                         'areFriends': 'friends.areFriends?',
#                         'getMutual': 'friends.getMutual?',
#                         },
#             'photos': {'get': 'photos.get?',
#                        'get_albums': 'photos.getAlbums?'},
#         }
#         user_params = {"user_ids": self.id}
#         user_params.update(self.params)
#         # print(requests.get(self.API_URL + self.methods['users']['get'],
#         #              params=user_params).json())
#         resp = requests.get(self.API_URL + self.methods['users']['get'],
#                             params=user_params).json()['response'][0]
#         self.name = resp['first_name'] + ' ' + resp['last_name']
#         if not users_list:
#             users_list.append(self)
#         else:
#             id_list = {_user.id for _user in users_list}
#             if self.id not in id_list:
#                 users_list.append(self)
#
#     # noinspection Pylint
#     def __repr__(self):
#         return str(self.id)
#
#     # noinspection Pylint
#     def __str__(self):
#         return self.URL + str(self.id)
#
#     # noinspection Pylint
#     def __and__(self, other):
#         return self.mutual_friends(other.id)
#
    # def mutual_friends(self, friend):
    #     """Метод получает список общих друзей двух пользователей"""
    #     mutual_friends_params = {
    #         'source_uid': self.id,
    #         'target_uid': friend,
    #     }
    #     mutual_friends_params.update(self.params)
    #     ids_list = requests.get(self.API_URL + self.methods['friends']['getMutual'],
    #                             params=mutual_friends_params).json()['response']
    #     time.sleep(1)
    #     friends_list = tqdm((User(_id).name for _id in ids_list),
    #                         total=len(ids_list),
    #                         desc="Получение имён общих друзей")
    #     time.sleep(1)
    #     print(f'\n{self.name} и {User(friend).name} имеют {len(friends_list)} общих друзей:')
    #     print(*friends_list, sep=", ", end="\n\n")
    #
    # def get_photos(self):
    #     """Метод получает ссылки на 5 последних по дате загрузки фотографий из различных альбомов пользователя"""
    #
    #     def get_albums():
    #         param = {"owner_id": self.id}
    #         param.update(self.params)
    #         response = requests.get(self.API_URL + self.methods['photos']['get_albums'],
    #                                 params=param).json()['response']['items']
    #         albums = {num: {album["title"]: album["id"]} for num, album in enumerate(response, start=1)}
    #         try:
    #             last_key = max(albums.keys()) + 1
    #             albums[last_key] = {"Фото профиля": "profile"}
    #             return albums
    #         except ValueError:
    #             albums[0] = {"Фото профиля": "profile"}
    #             return albums
    #
    #     albums = get_albums()
    #
    #     print("Фото из какого альбома Вы хотите загрузить?")
    #     for keys, values in albums.items():
    #         for key in values.keys():
    #             print(f'{keys}: "{key}"')
    #     album_number = albums[int(input("Введите номер альбома: "))]
    #     album_id = (album_number[key] for key in album_number.keys())
    #
    #     param = {"album_id": album_id, "photo_sizes": "1", 'extended': 1, "owner_id": self.id}
    #     param.update(self.params)
    #     photos_list = requests.get(self.API_URL + self.methods['photos']['get'],
    #                                params=param).json()['response']['items'][-5:]
    #
    #     photos_info = []
    #     for photo in photos_list:
    #         info = {
    #             "file_name": str(photo['likes']['count']) + "_" + str(
    #                 datetime.fromtimestamp(photo['date']).date()) + ".jpg",
    #             "size": photo['sizes'][-1]['type']
    #         }
    #         photos_info.append(info)
    #     with open("downloaded_vk_photos.json", "w") as file:
    #         json.dump(photos_info, file)
    #
    #     url_list = [(photo['sizes'][-1]['url'], photo['likes']['count'], photo['date']) for photo in photos_list]
    #     return url_list, self.name
    #
    # @staticmethod
    # def download(urls_list):
    #     """Метод скачивает на жесткий диск фотографии пользователя"""
    #     tuples, name = urls_list
    #     target_folder = os.path.join('downloads', name)
    #     os.makedirs(target_folder, exist_ok=True)
    #     target_folder = os.path.abspath(target_folder)
    #     for url, likes, date in tqdm(tuples):
    #         file_to_download = requests.get(url)
    #         with open(os.path.join(target_folder, str(likes) + "_" + str(datetime.fromtimestamp(date).date()) + ".jpg"),
    #                   'wb') as file:
    #             file.write(file_to_download.content)
    #     return target_folder.split(os.path.sep)[-1]
username = 89645338731
password = 'zaxs83cdRYB'

# auth = VKAPIAuth(login=username, password=password)
token = '8cb65f702eb242863efc670e3ed795d3a93a0212fe09db811f6ea455d6f58247a2d1777a75eee26ab13e4'
# vk = vk_api.VkApi(token=auth.ACCESS_TOKEN)
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)


def write_msg(self, user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text

            if request == "привет":
                write_msg(event.user_id, f"Хай, {event.user_id}")
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")
