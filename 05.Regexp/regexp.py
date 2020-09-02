# читаем адресную книгу в формате CSV в список contacts_list
import csv
import re
from pprint import pprint


def get_full_name(lastname, firstname, surname):
    name = " ".join((lastname, firstname, surname)).strip()
    full_name = name.split()
    if len(full_name) < 3:
        full_name.append('')
    return tuple(full_name)


def get_phone(phone):
    if phone:
        regex = r'(?P<country>\d)(?P<code>\d{3})(?P<first>\d{3})?(?P<second>\d{2})(?P<third>\d{2})(доб)?(?P<add>\d+)?'
        digits = ''.join(re.findall(r'\d+|доб', phone))
        match = re.match(regex, digits)
        code = match.group('code')
        first = match.group('first')
        second = match.group('second')
        third = match.group('third')
        add = match.group('add')
        if add:
            return f'+7({code}){first}-{second}-{third} доб.{add}'
        else:
            return f'+7({code}){first}-{second}-{third}'
    return ''


def order(contacts_list):
    ordered_contacts = []

    for lastname, firstname, surname, organization, position, phone, email in contacts_list[1:]:
        ordered_contacts.append(
            {
                'lastname': lastname,
                'firstname': firstname,
                'surname': surname,
                'organization': organization,
                'position': position,
                'phone': phone,
                'email': email
            }
        )

    for dic in ordered_contacts:
        for _dic in ordered_contacts:
            if dic['firstname'] == _dic['firstname'] and dic['lastname'] == _dic['lastname']:
                for key in dic.keys():
                    if dic[key] == '' and _dic[key] != '':
                        dic[key] = _dic[key]

    for dic in ordered_contacts:
        while ordered_contacts.count(dic) > 1:
            ordered_contacts.remove(dic)

    return ordered_contacts


if __name__ == '__main__':
    with open("phonebook_raw.csv", encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=",")
        contacts_list = list(reader)
        fieldnames = contacts_list[0]

    for contact in contacts_list[1:]:
        if len(contact) > len(fieldnames):
            contact.pop()
    # pprint(contacts_list)

    # TODO 1: выполните пункты 1-3 ДЗ
    for contact in contacts_list[1:]:
        contact[0], contact[1], contact[2] = get_full_name(contact[0], contact[1], contact[2])
        contact[-2] = get_phone(contact[-2])

    ordered_contact_list = order(contacts_list)
    pprint(ordered_contact_list)

    # TODO 2: сохраните получившиеся данные в другой файл
    # код для записи файла в формате CSV
    with open("phonebook.csv", "w", encoding='utf-8') as f:
        datawriter = csv.DictWriter(f, delimiter=',', fieldnames=fieldnames)
        datawriter.writeheader()
        # Вместо contacts_list подставьте свой список
        datawriter.writerows(ordered_contact_list)
