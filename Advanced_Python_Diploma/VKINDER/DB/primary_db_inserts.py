import json

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from DB.database import Sex, Status, Sort, Country, City, Region

Base = declarative_base()
engine = create_engine(f'postgresql+psycopg2://vkinder:12345@localhost:5432/vkinder')
Session = sessionmaker(bind=engine)
session = Session()

# если файлов с топонимами нет, то нужно запустить из VK_SCOPE/vk_scope методы
# _get_countries, _get_regions, _get_cities
# сбор данных займёт минимум 1 час
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


def insert_basics():
    for file in files:
        with open(file) as f:
            data = json.load(f)

        for entity_dict in data:
            Model = table_to_model_mapping[entity_dict['model']]
            fields = entity_dict['fields']
            result = session.query(Model).filter(Model.id == fields['id'])
            if not result.first():
                entity = Model(**fields)
                print(entity)
                session.add(entity)
                session.commit()
            else:
                continue
    print('All basics are inserted')


if __name__ == '__main__':
    insert_basics()
