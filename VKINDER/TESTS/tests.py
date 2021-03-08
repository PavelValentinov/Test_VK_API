from unittest.mock import patch

import pytest

from DB.database import City, Region, Connect, User, Query, DatingUser
from VK_SCOPE.bot import Bot
from VK_SCOPE.vk_scope import VKAuth, VKUser, VKDatingUser


@pytest.fixture()
def auth():
    return VKAuth()


@pytest.fixture()
def user(bot, db):
    user = bot.create_user(1)
    user.insert_self_to_db()
    yield user
    db.delete_from_db(User, User.id == user.user_id)


@pytest.fixture()
def datinguser(user, db):
    values = {
        'db_id': 0,
        'vk_id': user.user_id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'vk_link': user.link
    }
    d_user = VKDatingUser(**values)
    yield d_user
    db.delete_from_db(DatingUser, DatingUser.id == 0)


@pytest.fixture()
def bot():
    return Bot()


@pytest.fixture()
def db():
    return Connect()


def test_check_city_and_region(bot, db, user):
    assert bot._check_city_and_region(user) is None

    city, region = bot._get_city(1, "Краснодар")
    check_city = db.select_from_db(City.id, City.id == city['id']).first()[0]
    check_region = db.select_from_db(Region.id, Region.id == region['id']).first()[0]
    assert check_region == 1040652
    assert check_city == 72

    city, region = bot._get_city(1, "Москва")
    check_city = db.select_from_db(City.id, City.id == city['id']).first()[0]
    assert region is None
    assert check_city == 1

    city, region = bot._get_city(2, "Кроснодор")
    assert city is None
    assert region is None


def test_get_region(bot):
    result = bot._get_region(1, 'Владимирская')
    assert result == {'count': 1, 'items': [{'id': 1124833, 'title': 'Владимирская область'}]}

    result = bot._get_region(9, 'Alabama')
    assert result == {'count': 1, 'items': [{'id': 5022370, 'title': 'Alabama'}]}

    result = bot._get_region(456, 'Москва')
    assert result == {'count': 0, 'items': []}


def test_get_city(bot, db):
    city, region = bot._get_city(1, "Краснодар")
    check_city = db.select_from_db(City.id, City.id == city['id']).first()[0]
    check_region = db.select_from_db(Region.id, Region.id == region['id']).first()[0]
    assert check_region == 1040652
    assert check_city == 72

    city, region = bot._get_city(1, "Москва")
    check_city = db.select_from_db(City.id, City.id == city['id']).first()[0]
    assert region is None
    assert check_city == 1

    city, region = bot._get_city(2, "Кроснодор")
    assert city is None
    assert region is None


def test_check_user_city(bot, user):
    assert bot.check_user_city(user) == 2


def test_create_user(bot, user):
    assert isinstance(user, VKUser)
    assert user.user_id == 1
    assert user.welcomed is False
    assert user.user_id in bot.users


def test_insert_query(bot, db, user):
    query_values = {
        'sex': 1,
        'city': 1,
        'age_from': 20,
        'age_to': 30,
        'status': 6,
        'sort': 1,
    }

    query_id = bot.insert_query(1, query_values)
    db_query = db.select_from_db(Query, Query.user_id == user.user_id).first()
    try:
        assert query_id == db_query.id
        assert db_query.sex_id == query_values['sex']
        assert db_query.city_id == query_values['city']
        assert db_query.age_from == query_values['age_from']
        assert db_query.age_to == query_values['age_to']
        assert db_query.status_id == query_values['status']
        assert db_query.sort_id == query_values['sort']
        assert db_query.user_id == user.user_id
    finally:
        db.delete_from_db(Query, Query.user_id == user.user_id)


def test_search_users(bot, db, user):
    query_values = {
        'sex': 1,
        'city': 456,
        'age_from': 7,
        'age_to': 10,
        'status': 1,
        'sort': 1,
    }
    dusers, query_id = bot.search_users(user)
    try:
        assert dusers > 0
        assert bot.search_users(user, query_values) is None
    finally:
        db.delete_from_db(DatingUser, DatingUser.query_id == query_id)
        db.delete_from_db(Query, Query.user_id == user.user_id)


def test_welcome_user(user, bot):
    assert user.welcomed is False
    with patch("VK_SCOPE.bot.Bot.write_msg"):
        bot.welcome_user(user)
        assert user.welcomed is True


def test_insert_self_to_db(db, bot, user):
    db_user = db.select_from_db(User, User.id == user.user_id).first()
    assert db_user.id == user.user_id
    assert db_user.sex_id == user.sex
    assert db_user.city_id == user.city['id']


def test_get_self_info(user):
    result = user.get_self_info(user.user_id)
    assert isinstance(result, list)
    assert result[0].get('sex') == 2
    assert result[0].get('city').get('id') == 2


def test_get_photo(datinguser, db):
    result = datinguser.get_photo()
    assert len(result) <= 3
    assert isinstance(result, list)
    for id, owner_id in result:
        assert isinstance(id, int)
        assert isinstance(owner_id, int)
        assert owner_id == datinguser.id


@pytest.mark.parametrize(
    ("sex_title", "expected_sex_id"), [("мужской", 2), ("женский", 1), ("пол не указан", 0)]
)
def test_get_sex(bot, user, sex_title, expected_sex_id):
    with patch("VK_SCOPE.bot.Bot.write_msg") as write_msg_mock:
        with patch("VK_SCOPE.bot.Bot.listen_msg", return_value=(sex_title, user)) as listen_msg_mock:
            sex = bot.get_sex(user)
            assert sex == expected_sex_id
    write_msg_mock.assert_called_once()
    listen_msg_mock.assert_called_once()


@pytest.mark.parametrize(
    ("city_title", "expected_city_id"), [("Canbolat", 3273662), ("Санкт-Петербург", 2)]
)
def test_get_unique_city(bot, user, city_title, expected_city_id):
    with patch("VK_SCOPE.bot.Bot.write_msg") as write_msg_mock:
        with patch("VK_SCOPE.bot.Bot.listen_msg", return_value=(city_title, user)) as listen_msg_mock:
            city = bot.get_city(user)
            assert city == expected_city_id
    write_msg_mock.assert_called_once()
    listen_msg_mock.assert_called_once()


@pytest.mark.parametrize(
    ("city_title", "city_order", "expected_city_id"), [
        ("Москва", "1", 1), ("Омск", "1", 104)]
)
def test_get_not_unique_city(bot, user, city_title, city_order, expected_city_id):
    with patch("VK_SCOPE.bot.Bot.write_msg") as write_msg_mock:
        with patch("VK_SCOPE.bot.Bot.listen_msg",
                   side_effect=[(city_title, user), (city_order, user)]) as listen_msg_mock:
            city = bot.get_city(user)
            assert city == expected_city_id
    write_msg_mock.assert_called()
    listen_msg_mock.assert_called()


@pytest.mark.parametrize(
    ("age_from", "expected_age"), [("18", 18), ("51", 51)]
)
def test_get_age_from(bot, user, age_from, expected_age):
    with patch("VK_SCOPE.bot.Bot.write_msg") as write_msg_mock:
        with patch("VK_SCOPE.bot.Bot.listen_msg", return_value=(age_from, user)) as listen_msg_mock:
            age = bot.get_age_from(user)
            assert age == expected_age
    write_msg_mock.assert_called_once()
    listen_msg_mock.assert_called_once()


@pytest.mark.parametrize(
    ("age_to", "expected_age"), [("18", 18), ("0", 100)]
)
def test_get_age_to(bot, user, age_to, expected_age):
    with patch("VK_SCOPE.bot.Bot.write_msg") as write_msg_mock:
        with patch("VK_SCOPE.bot.Bot.listen_msg", return_value=(age_to, user)) as listen_msg_mock:
            age = bot.get_age_to(user)
            assert age == expected_age
    write_msg_mock.assert_called_once()
    listen_msg_mock.assert_called_once()


@pytest.mark.parametrize(
    ("status", "expected_status_id"), [("не женат (не замужем)", 1),
                                       ("встречается", 2),
                                       ("помолвлен(-а)", 3),
                                       ("женат (замужем)", 4),
                                       ("всё сложно", 5),
                                       ("в активном поиске", 6),
                                       ("влюблен(-а)", 7),
                                       ("в гражданском браке", 8)]
)
def test_get_status(bot, user, status, expected_status_id):
    with patch("VK_SCOPE.bot.Bot.write_msg") as write_msg_mock:
        with patch("VK_SCOPE.bot.Bot.listen_msg", return_value=(status, user)) as listen_msg_mock:
            status = bot.get_status(user)
            assert status == expected_status_id
    write_msg_mock.assert_called_once()
    listen_msg_mock.assert_called_once()


@pytest.mark.parametrize(
    ("sort", "expected_sort_id"), [("по популярности", 0),
                                   ("по дате регистрации", 1)
                                   ]
)
def test_sort(bot, user, sort, expected_sort_id):
    with patch("VK_SCOPE.bot.Bot.write_msg") as write_msg_mock:
        with patch("VK_SCOPE.bot.Bot.listen_msg", return_value=(sort, user)) as listen_msg_mock:
            sort = bot.get_sort(user)
            assert sort == expected_sort_id
    write_msg_mock.assert_called_once()
    listen_msg_mock.assert_called_once()


if __name__ == '__main__':
    pytest.main()
