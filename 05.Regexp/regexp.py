# читаем адресную книгу в формате CSV в список contacts_list
import csv
from collections import OrderedDict
import re


def get_full_name(line):
    for name in line:
        print(name)
    regex = re.compile(r'^(?P<lastname>\S+)\s*((?P<firstname>\S+)\s*)?((?P<surname>\S+))?$')
    full_names_list = [f'{name[0].strip()} {name[1].strip()} {name[2].strip()}' for name in line]
    print(full_names_list)





#
# def get_organization():
#     for _, _, _, organization, _, _, _, in contacts_list[1:]:
#         pass
#
#
# def get_position():
#     for _, _, _, _, position, _, _ in contacts_list[1:]:
#         pass
#
#
# def get_phone():
#     for _, _, _, _, _, phone, _ in contacts_list[1:]:
#         pass
#
#
# def get_email():
#     for _, _, _, _, _, _, email in contacts_list[1:]:
#         pass


with open("phonebook_raw.csv", 'r', encoding='utf-8') as f:
    rows = csv.reader(f, delimiter=",")
    contacts_list = list(rows)

# contacts = OrderedDict()
for contact in contacts_list:
    get_full_name(contact)
# print(contacts)

# TODO 1: выполните пункты 1-3 ДЗ
# ваш код

# TODO 2: сохраните получившиеся данные в другой файл
# код для записи файла в формате CSV
# with open("phonebook.csv", "w") as f:
#   datawriter = csv.writer(f, delimiter=',')
#   # Вместо contacts_list подставьте свой список
#   datawriter.writerows(contacts_list)
