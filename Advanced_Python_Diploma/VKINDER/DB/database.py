import json

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Connect:
    engine = create_engine(f'postgresql+psycopg2://vkinder:12345@localhost:5432/vkinder')
    Session = sessionmaker(bind=engine)
    session = Session()

    def _insert_basics(self):
        """ Метод для записи в БД первичных данных из файлов.
        Если файлов с топонимами нет, то нужно запустить из VK_SCOPE/vk_scope методы _get_countries,
        _get_regions, _get_citiesсбор данных займёт минимум 1 час"""

        files = [
            "../DB/Fixtures/primary_data.json",
            "../DB/Fixtures/countries.json",
            "../DB/Fixtures/regions.json",
            "../DB/Fixtures/cities.json"
        ]

        table_to_model_mapping = {
            "sex": Sex,
            "status": Status,
            "sort": Sort,
            "country": Country,
            "city": City,
            "region": Region
        }

        for file in files:
            with open(file) as f:
                data = json.load(f)

            for entity_dict in data:
                Model = table_to_model_mapping[entity_dict['model']]
                fields = entity_dict['fields']
                if not self.select_from_db(Model, Model.id == fields['id']).first():
                    entity = Model(**fields)
                    print(entity)
                    self.session.add(entity)
                    self.session.commit()
                else:
                    continue
        print('All basics are inserted')

    def select_from_db(self, model_fields, expression):
        """Метод проверки наличия записей в БД"""
        return self.session.query(model_fields).filter(expression)

    def update_data(self, model_field, filter_expression, fields):
        self.session.query(model_field).filter(filter_expression).update(fields)
        self.session.commit()
        print(f'{model_field} updated successfully ')

    def insert_user(self, model, fields):
        """Метод для записи в БД данных о пользователях"""
        entity = model(**fields)
        # print(entity)
        self.session.add(entity)
        self.session.commit()

    def insert_city(self, city):
        """Метод для записи в БД данных о городе"""
        entity = City(**city)
        # print(entity)
        self.session.add(entity)
        self.session.commit()

    def insert_region(self, region):
        """Метод для записи в БД данных о регионе"""
        entity = Region(**region)
        # print(entity)
        self.session.add(entity)
        self.session.commit()


# id из Вконтакте являются натуральными Primary key для любой таблицы, описывающей соответствующую сущность
# таблица всех стран
class Country(Base):
    __tablename__ = 'country'
    id = Column(Integer, primary_key=True, unique=True)
    title = Column(String)


# таблица всех регионов
class Region(Base):
    __tablename__ = 'region'
    id = Column(Integer, primary_key=True, unique=True)
    title = Column(String)
    country_id = Column(Integer, ForeignKey('country.id'))


# таблица всех городов
class City(Base):
    __tablename__ = 'city'
    id = Column(Integer, primary_key=True, unique=True)
    title = Column(String)
    important = Column(Integer, default=0)
    area = Column(String, default=None)
    region = Column(String)
    region_id = Column(Integer, ForeignKey('region.id'))


# таблица полов (бесполые/ж/м)
class Sex(Base):
    __tablename__ = 'sex'
    id = Column(Integer, primary_key=True, unique=True)
    title = Column(String)


# таблица всех вариантов семейного положения ВК
class Status(Base):
    __tablename__ = 'status'
    id = Column(Integer, primary_key=True, unique=True)
    title = Column(String)


# таблица вариантов сортировки поиска (по популярности/по дате регистрации)
class Sort(Base):
    __tablename__ = 'sort'
    id = Column(Integer, primary_key=True, unique=True)
    title = Column(String)


# таблица, хранящая информацию о юзере
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    date_of_birth = Column(String)
    city_id = Column(Integer, ForeignKey('city.id'))
    sex_id = Column(Integer, ForeignKey('sex.id'))
    link = Column(String)


# таблица, хранящая условия и дату поиска юзера
class Query(Base):
    __tablename__ = 'query'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    datetime = Column(DateTime)
    sex_id = Column(Integer, ForeignKey('sex.id'))
    age_from = Column(Integer)
    age_to = Column(Integer)
    city_id = Column(Integer, ForeignKey('city.id'))
    sort_id = Column(Integer, ForeignKey('sort.id'))
    status_id = Column(Integer, ForeignKey('status.id'))
    user_id = Column(Integer, ForeignKey('user.id'))


# таблица, хранящая информацию о результатах поиска
class DatingUser(Base):
    __tablename__ = 'datinguser'
    id = Column(Integer, primary_key=True, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    city_id = Column(Integer)
    city_title = Column(String)
    link = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))
    query_id = Column(Integer, ForeignKey('query.id'))
    viewed = Column(Boolean, default=False)
    black_list = Column(Boolean, nullable=True)


# таблица, хранящая информацию о фотографиях
class Photos(Base):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    DatingUser_id = Column(Integer, ForeignKey('datinguser.id'))
    link_photo = Column(String, nullable=False)
    count_likes = Column(Integer)


if __name__ == '__main__':
    Base.metadata.create_all(Connect.engine)
    print("All tables are created successfully")
    Connect()._insert_basics()
    print("Primary inserts done")
