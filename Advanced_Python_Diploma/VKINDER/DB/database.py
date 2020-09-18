from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine(f'postgresql+psycopg2://vkinder:12345@localhost:5432/vkinder')
Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_id = Column(Integer)
    first_name = Column(String)
    last_name = Column(String)
    date_of_birth = Column(String)
    age_from = Column(Integer, nullable=False)
    age_to = Column(Integer, nullable=False)
    city_id = Column(Integer)
    city_title = Column(String)


class DatingUser(Base):
    __tablename__ = 'datinguser'
    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_id = Column(Integer)
    first_name = Column(String)
    last_name = Column(String)
    city_id = Column(Integer)
    city_title = Column(String)
    id_User = Column(Integer, ForeignKey('user.id'))


class Photos(Base):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_DatingUser = Column(Integer, ForeignKey('datinguser.id'))
    link_photo = Column(String, nullable=False)
    count_likes = Column(Integer)


class BlackList(Base):
    __tablename__ = 'blacklist'
    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_id = Column(Integer)


class Country(Base):
    __tablename__ = 'country'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)


class Region(Base):
    __tablename__ = 'region'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    country_id = Column(String, ForeignKey('country.id'))


class City(Base):
    __tablename__ = 'city'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    region_title = Column(String, ForeignKey('region.title'))


if __name__ == '__main__':
    Base.metadata.create_all(engine)
