import os
import re
from random import randrange

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from DB.database import User, City, Status, Sex, Sort, Query, DatingUser
from VK_SCOPE.vk_scope import VKUser


# noinspection SpellCheckingInspection
class Bot(VKUser):

    def __init__(self):
        """Инициализация бота"""
        # noinspection SpellCheckingInspection
        # FIXME: укажите Ваш токен сообщества (группы) Вконтакте вместо os.getenv("VKINDER_TOKEN")
        self.vk_bot = vk_api.VkApi(token=os.getenv("VKINDER_TOKEN"), api_version='5.124')
        # noinspection SpellCheckingInspection
        self.longpoll = VkLongPoll(self.vk_bot)
        self.empty_keyboard = VkKeyboard().get_empty_keyboard()
        self.users = {}

    def write_msg(self, user_id, message, attachment=None, keyboard=None):
        """Отправка сообщения пользователю"""
        values = {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)}
        if attachment:
            values['attachment'] = attachment
        if keyboard:
            values['keyboard'] = keyboard

        self.vk_bot.method('messages.send', values)

    def listen_msg(self, scan=True):
        """Ожидание сообщений от пользователя и их обработка"""

        def scan_request(event):
            """Разбор сообщений от пользователя c удалением знаков препинания, чисткой пробелов"""
            request = event.text.lower().strip()
            query = re.findall(r'([А-Яа-яЁёA-Za-z0-9]+)', request)
            if len(query) > 1:
                query = ' '.join(query)
            else:
                try:
                    query = query[0]
                except IndexError:
                    query = request
            return query

        for event in self.longpoll.listen():
            try:
                if event.user_id not in self.users:
                    self.users[event.user_id] = [VKUser(event.user_id)]
                    user = self.users[event.user_id][0]

                    keyboard = VkKeyboard(one_time=False)

                    check_user = user.select_from_db(User.id, User.id == user.user_id).first()

                    if check_user is None or not check_user:
                        user.insert_self_to_db()

                        keyboard.add_button("Привет", color=VkKeyboardColor.PRIMARY)
                        keyboard.add_button("Новый поиск", color=VkKeyboardColor.SECONDARY)

                        self.write_msg(user.user_id, f"&#128522; Привет, {user.first_name.capitalize()}!",
                                       keyboard=keyboard.get_keyboard())

                    else:
                        check_query = user.select_from_db(Query.id, Query.user_id == user.user_id).all()
                        if check_query is None or not check_query:

                            keyboard.add_button("Привет", color=VkKeyboardColor.PRIMARY)
                            keyboard.add_button("Новый поиск", color=VkKeyboardColor.SECONDARY)

                            self.write_msg(user.user_id,
                                           f"&#128522; Привет, {user.first_name.capitalize()}! Давно не виделись!",
                                           keyboard=keyboard.get_keyboard())
                        else:
                            keyboard.add_button("Привет", color=VkKeyboardColor.POSITIVE)
                            keyboard.add_button("Новый поиск", color=VkKeyboardColor.SECONDARY)
                            keyboard.add_line()
                            keyboard.add_button(f"Результаты последнего поиска", color=VkKeyboardColor.PRIMARY)
                            keyboard.add_line()
                            keyboard.add_button(f"Все лайкнутые", color=VkKeyboardColor.POSITIVE)
                            keyboard.add_button(f"Все непонравившиеся", color=VkKeyboardColor.NEGATIVE)
                            self.write_msg(user.user_id,
                                           f"&#128522; Привет, {user.first_name.capitalize()}! Давно не виделись!",
                                           keyboard=keyboard.get_keyboard())
                else:
                    user = self.users[event.user_id][0]
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        if scan is True:
                            return scan_request(event), user
                        else:
                            return event.text, user
            except AttributeError:
                pass

    def short_questionnaire(self, user, values):  # Smile =)
        search_values = values

        # город
        self.write_msg(user.user_id, f'В каком городе будем искать?\n\nНазвания зарубежных городов, таких как Лондон '
                                     f'или Париж, должны быть написаны латиницей и полностью.\n\nНа всякий случай: '
                                     f'тот самый Нью-Йорк, о котором все так много слышали, правильно пишется '
                                     f'New York City.',
                       keyboard=self.empty_keyboard)
        while True:
            answer = self.listen_msg(scan=False)[0].strip().lower()

            try:
                symbol = re.search(r'\W', answer)[0]
                words = re.split(symbol, answer)
                if len(words) < 3:
                    for word in words:
                        words[words.index(word)] = word.capitalize()
                    answer = symbol.join(words)
                else:
                    if '-' == symbol:
                        words[0] = words[0].capitalize()
                        words[-1] = words[-1].capitalize()
                        answer = symbol.join(words)
                    else:
                        answer = answer.title()
            except TypeError:
                answer = answer.lower().capitalize()

            try:
                city = user.select_from_db(City.id, City.title == answer).all()
                if city is None or not city:
                    self.write_msg(user.user_id, f'&#128530; Я пока не знаю такого города. '
                                                 f'Выбери другой или попробуй написать иначе. '
                                                 f'Пробелы и дефисы в названии играют большую роль.')
                else:
                    break
            except IndexError:
                city = user.select_from_db(City.id, City.title == answer).first()
                if city is None or not city:
                    self.write_msg(user.user_id, f'&#128530; Я пока не знаю такого города. '
                                                 f'Выбери другой или попробуй написать иначе. '
                                                 f'Пробелы и дефисы в названии играют большую роль.')
                else:
                    break
        if len(city) == 1:
            search_values['city'] = city[0][0]
        elif len(city) > 1:
            self.write_msg(user.user_id, f'Нужно уточнить, город в каком именно регионе ты имеешь в виду:')
            ids = sorted([city[0] for city in city])
            regions = {}
            message = ''
            for num, id in enumerate(ids, start=1):
                regions[str(num)] = id
                region_name = user.select_from_db(City.region, City.id == id).first()[0]
                area = user.select_from_db(City.area, City.id == id).first()[0]
                if area:
                    message += f'{num} - {region_name}, {area}\n'
                else:
                    message += f'{num} - {region_name}\n'
            self.write_msg(user.user_id, message)
            expected_answers = [str(i) for i in range(1, len(city) + 1)]
            answer = self.listen_msg()[0].strip()
            while answer not in expected_answers:
                self.write_msg(user.user_id, f'Мне нужен один из порядковых номеров, которые ты видишь чуть выше.')
                answer = self.listen_msg()[0].strip()
            else:
                search_values['city'] = regions[answer]

        # начальный возраст
        self.write_msg(user.user_id, f'Укажи минимальный возраст в цифрах.')
        while True:
            try:
                answer = int(self.listen_msg()[0].strip())
            except ValueError:
                self.write_msg(user.user_id, f'Укажи минимальный возраст в ЦИФРАХ.')
            else:
                search_values['age_from'] = abs(answer)
                break

        # конечный возраст
        self.write_msg(user.user_id, f'Укажи максимальный возраст в цифрах или отправь 0, если тебе это неважно.')
        while True:
            try:
                answer = int(self.listen_msg()[0].strip())
            except ValueError:
                self.write_msg(user.user_id,
                               f'Укажи максимальный возраст в ЦИФРАХ или отправь 0, если тебе это неважно.')
            else:
                if answer != 0:
                    search_values['age_to'] = abs(answer)
                else:
                    search_values['age_to'] = 100
                break

        # семейное положение
        statuses = [name[0] for name in user.select_from_db(Status.title, Status.id == Status.id).all()]

        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button(statuses[0], VkKeyboardColor.POSITIVE)
        keyboard.add_button(statuses[1], VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button(statuses[2], VkKeyboardColor.SECONDARY)
        keyboard.add_button(statuses[3], VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button(statuses[5], VkKeyboardColor.POSITIVE)
        keyboard.add_button(statuses[4], VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button(statuses[6], VkKeyboardColor.SECONDARY)
        keyboard.add_button(statuses[7], VkKeyboardColor.NEGATIVE)
        keyboard = keyboard.get_keyboard()

        self.write_msg(user.user_id, f'Какой из статусов тебя интересует?', keyboard=keyboard)

        answer = self.listen_msg(scan=False)[0].strip()

        while answer not in statuses:
            self.write_msg(user.user_id, '&#129300; Не понимаю... Используй кнопки. &#128071;')
            answer = self.listen_msg()[0].strip()
        else:
            search_values['status'] = statuses.index(answer) + 1

        # сортировка
        sort_names = [name[0] for name in user.select_from_db(Sort.title, Sort.id == Sort.id).all()]

        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button(sort_names[0], VkKeyboardColor.POSITIVE)
        keyboard.add_button(sort_names[1], VkKeyboardColor.PRIMARY)
        keyboard = keyboard.get_keyboard()
        self.write_msg(user.user_id, f'Как отсортировать пользователей?', keyboard=keyboard)

        answer = self.listen_msg()[0].strip()
        while answer not in sort_names:
            self.write_msg(user.user_id, '&#129300; Не понимаю... Используй кнопки. &#128071')
            answer = self.listen_msg()[0].strip()
        else:
            search_values['sort'] = sort_names.index(answer)
        return self.search_users(user, search_values)

    def full_questionnaire(self, user):

        search_values = {
            'city': None,
            'sex': None,
            'age_from': None,
            'age_to': None,
            'status': None,
            'sort': None,
        }

        # пол
        sex = [name[0] for name in user.select_from_db(Sex.title, Sex.id == Sex.id).all()]

        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button(sex[1], VkKeyboardColor.NEGATIVE)
        keyboard.add_button(sex[2], VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button(sex[0], VkKeyboardColor.SECONDARY)
        keyboard = keyboard.get_keyboard()

        self.write_msg(user.user_id, f'Людей какого пола мы будем искать?', keyboard=keyboard)

        expected_answers = sex
        answer = self.listen_msg()[0].strip()
        while answer not in expected_answers:
            self.write_msg(user.user_id, '&#129300; Не понимаю... Используй кнопки. &#128071')
            answer = self.listen_msg()[0].strip()
        else:
            search_values['sex'] = sex.index(answer)

        return self.short_questionnaire(user, search_values)

    def start(self):
        """Метод общения с юзером в целях получения его требований к поиску"""

        def initial_questionnaire():
            expected_answers = ['да', 'нет']
            answer = self.listen_msg()[0].strip()
            while answer not in expected_answers:
                self.write_msg(user.user_id, '&#129300; Не понимаю... Просто скажи "да" или "нет" '
                                             'или используй кнопки. &#128071;')
                answer = self.listen_msg()[0].strip()
            else:
                if answer == 'да':

                    keyboard = VkKeyboard(one_time=False)
                    keyboard.add_button("стандартный", VkKeyboardColor.PRIMARY)
                    keyboard.add_button("детализированный", VkKeyboardColor.SECONDARY)
                    keyboard = keyboard.get_keyboard()
                    self.write_msg(user.user_id, f"Какой вид поиска будем использовать? &#128071;", keyboard=keyboard)

                    expected_answers = ["стандартный", "детализированный"]
                    answer = self.listen_msg()[0].strip()
                    while answer not in expected_answers:
                        self.write_msg(user.user_id, '&#129300; Не понимаю... Используй кнопки. &#128071;')
                        answer = self.listen_msg()[0].strip()
                    else:
                        if answer == "стандартный":
                            self.write_msg(user.user_id, f"&#128077; Прекрасный выбор!")
                            return self.search_users(user, search_values)
                        elif answer == "детализированный":
                            self.write_msg(user.user_id,
                                           f"&#128076; Ок! Тогда тебе нужно будет ответить на несколько вопросов.")
                            return self.short_questionnaire(user, search_values)
                elif answer == 'нет':
                    return self.full_questionnaire(user)

        answer, user = self.listen_msg()

        search_values = {
            'city': user.city['id'],
            'sex': None,
            'age_from': 18,
            'age_to': 99,
            'status': 6,
            'sort': 0,
        }

        expected_answers = ['привет', 'новый поиск', "результаты последнего поиска",
                            "все лайкнутые", "все непонравившиеся"]
        while answer not in expected_answers:
            self.write_msg(user.user_id, "&#129300; Не понимаю... Используй кнопки. &#128071;")
            answer = self.listen_msg()[0]
        else:
            if answer == "привет":
                keyboard = VkKeyboard(one_time=False)
                keyboard.add_button("Да", VkKeyboardColor.POSITIVE)
                keyboard.add_button("Нет", VkKeyboardColor.NEGATIVE)

                if user.sex == 2:
                    search_values['sex'] = 1
                    self.write_msg(user.user_id, f"Хочешь найти девушку?", keyboard=keyboard.get_keyboard())
                    results = initial_questionnaire()
                elif user.sex == 1:
                    search_values['sex'] = 2
                    self.write_msg(user.user_id, f"Хочешь найти парня?", keyboard=keyboard.get_keyboard())
                    results = initial_questionnaire()
                else:
                    results = self.full_questionnaire(user)

                if not results:
                    self.write_msg(user.user_id,
                                   f'&#128530; Похоже, что в этом городе нет никого, кто отвечал бы таким '
                                   f'условиям поиска.\nПопробуй использовать детализированный поиск или '
                                   f'изменить условия запроса.', keyboard=self.empty_keyboard)
                    main()

                else:
                    self.show_results(user, results=results)
                    main()

            elif answer == "новый поиск":
                results = self.full_questionnaire(user)
                if not results:
                    self.write_msg(user.user_id,
                                   f'&#128530; Похоже, что в этом городе нет никого, кто отвечал бы таким '
                                   f'условиям поиска.\nПопробуй использовать детализированный поиск или '
                                   f'изменить условия запроса.', keyboard=self.empty_keyboard)
                    main()
                else:
                    self.show_results(user, results=results)
                    main()

            elif answer == "результаты последнего поиска":
                self.show_results(user)
                main()

            elif answer == "все лайкнутые":
                liked_users = self.get_datingusers_from_db(user.user_id, blacklist=False)
                message = ''
                for num, d_user in enumerate(liked_users, start=1):
                    message += f'{num}. {d_user}\n'
                self.write_msg(user.user_id, message)
                self.show_results(user, datingusers=liked_users)
                main()

            elif answer == "все непонравившиеся":
                blacklist = self.get_datingusers_from_db(user.user_id, blacklist=True)
                message = ''
                for num, d_user in enumerate(blacklist, start=1):
                    message += f'{num}. {d_user}\n'
                self.write_msg(user.user_id, message)

    def show_results(self, user, results=None, datingusers=None):
        if results and not datingusers:
            remainder = results[0] % 10
            if remainder == 0 or remainder >= 5 or (10 <= results[0] <= 19):
                var = 'вариантов'
            elif remainder == 1:
                var = 'вариант'
            else:
                var = 'варианта'
            self.write_msg(user.user_id, f'&#128515; Мы нашли {results[0]} {var}!!!')
            query_id = results[1]
            dating_users = self.get_datingusers_from_db(user.user_id, query_id)
        elif not results and not datingusers:
            dating_users = self.get_datingusers_from_db(user.user_id)
        else:
            dating_users = datingusers

        if dating_users:
            # получаем список юзеров из БД
            for d_user in dating_users:
                d_user.photos = d_user.get_photo()
                name = d_user.first_name + ' ' + d_user.last_name
                link = d_user.link
                if len(d_user.photos) > 1:
                    photos_list = []
                    for photo in d_user.photos:
                        photo_id, owner_id, _, _ = photo
                        photos_list.append(f'photo{owner_id}_{photo_id}')
                    photos = ','.join(photos_list)
                else:
                    photo_id, owner_id, _, _ = d_user.photos[0]
                    photos = f'photo{owner_id}_{photo_id}'
                message = f'{name} {link} \n '

                keyboard = VkKeyboard(one_time=False)
                keyboard.add_button("Да", color=VkKeyboardColor.POSITIVE)
                keyboard.add_button("Нет", color=VkKeyboardColor.NEGATIVE)
                keyboard.add_line()
                keyboard.add_button("Отмена", color=VkKeyboardColor.SECONDARY)
                keyboard = keyboard.get_keyboard()

                self.write_msg(user.user_id, message=message, attachment=photos)
                self.write_msg(user.user_id, message='Нравится?', keyboard=keyboard)
                expected_answers = ['да', 'нет', 'отмена']
                answer = self.listen_msg()[0]
                while answer not in expected_answers:
                    self.write_msg(user.user_id, "&#129300; Не понимаю... Используй кнопки. &#128071;",
                                   keyboard=keyboard)
                    answer = self.listen_msg()[0]
                else:
                    if answer == "да":
                        fields = {DatingUser.viewed: True, DatingUser.black_list: False}
                        self.update_data(DatingUser.id, DatingUser.id == d_user.db_id, fields=fields)
                        continue
                    elif answer == "нет":
                        fields = {DatingUser.viewed: True, DatingUser.black_list: True}
                        self.update_data(DatingUser.id, DatingUser.id == d_user.db_id, fields=fields)
                        continue
                    elif answer == "отмена":
                        self.write_msg(user.user_id, "Заходи ещё! &#128406;",
                                       keyboard=self.empty_keyboard)
                        return
        self.write_msg(user.user_id, "&#128579; Похоже, что ты уже всех посмотрел. Попробуй новый поиск! &#128373;",
                       keyboard=self.empty_keyboard)
        return


def main():
    bot = Bot()
    while True:
        bot.start()


if __name__ == '__main__':
    main()
