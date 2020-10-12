import pytest

from DB.database import City, Region, Connect, User, Query, DatingUser
from VK_SCOPE.bot import Bot
from VK_SCOPE.vk_scope import VKAuth, VKUser, VKDatingUser


@pytest.fixture()
def auth():
    return VKAuth()


@pytest.fixture()
def user(id=None):
    if id:
        return VKUser(id)
    return VKUser(604152544)


@pytest.fixture()
def datinguser(user):
    values = {
        'db_id': 0,
        'vk_id': user.user_id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'vk_link': user.link
    }
    return VKDatingUser(**values)


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
    assert bot.check_user_city(user) == 1


def test_create_user(bot, db):
    new_user = bot.create_user(1)
    assert isinstance(new_user, VKUser)
    assert new_user.user_id == 1
    assert new_user.welcomed is False
    assert new_user.user_id in bot.users


def test_insert_query(bot, db):
    query_values = {
        'sex': 1,
        'city': 1,
        'age_from': 20,
        'age_to': 30,
        'status': 6,
        'sort': 1,
    }

    new_user = bot.create_user(1)
    new_user.insert_self_to_db()
    query_id = bot.insert_query(1, query_values)
    db_query = db.select_from_db(Query, Query.user_id == new_user.user_id).first()
    assert query_id == db_query.id
    assert db_query.sex_id == query_values['sex']
    assert db_query.city_id == query_values['city']
    assert db_query.age_from == query_values['age_from']
    assert db_query.age_to == query_values['age_to']
    assert db_query.status_id == query_values['status']
    assert db_query.sort_id == query_values['sort']
    assert db_query.user_id == new_user.user_id

    db.delete_from_db(Query, Query.user_id == new_user.user_id)
    db.delete_from_db(User, User.id == new_user.user_id)


def test_search_users(bot, db):
    query_values = {
        'sex': 1,
        'city': 456,
        'age_from': 7,
        'age_to': 10,
        'status': 1,
        'sort': 1,
    }
    new_user = bot.create_user(1)
    new_user.insert_self_to_db()
    dusers, query_id = bot.search_users(new_user)
    assert dusers > 0
    assert bot.search_users(new_user, query_values) is None
    db.delete_from_db(DatingUser, DatingUser.query_id == query_id)
    db.delete_from_db(Query, Query.user_id == new_user.user_id)
    db.delete_from_db(User, User.id == new_user.user_id)


def test_welcome_user(user, bot):
    assert user.welcomed is False
    bot.welcome_user(user)
    assert user.welcomed is True
    user.welcomed = False
    assert user.welcomed is False


def test_insert_self_to_db(db, bot):
    new_user = bot.create_user(1)
    new_user.insert_self_to_db()
    db_user = db.select_from_db(User, User.id == new_user.user_id).first()
    assert db_user.id == new_user.user_id
    assert db_user.sex_id == new_user.sex
    assert db_user.city_id == new_user.city['id']
    db.delete_from_db(User, User.id == new_user.user_id)


def test_get_self_info(user):
    result = user.get_self_info(user.user_id)
    assert isinstance(result, list)
    assert result[0].get('sex') == 2
    assert result[0].get('city').get('id') == 1


def test_get_photo(datinguser, db):
    result = datinguser.get_photo()
    assert len(result) <= 3
    assert isinstance(result, list)
    for id, owner_id in result:
        assert isinstance(id, int)
        assert isinstance(owner_id, int)
        assert owner_id == datinguser.id
    db.delete_from_db(DatingUser, DatingUser.id == 0)


if __name__ == '__main__':
    pytest.main()
