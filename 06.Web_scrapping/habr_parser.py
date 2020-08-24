from datetime import date, timedelta

from bs4 import BeautifulSoup
from requests import get
from tqdm import tqdm

KEYWORDS = ('дизайн', 'фото', 'web', "python")
URL = "https://habr.com/ru/all/"
TODAY = date.today()


def parse_habr() -> tuple:
    """Функция-парсер новостей Хабра по ключевым словам"""

    def _convert_to_date(post) -> str:
        """Функция приводит временные теги Хабра к формату даты"""
        tag_text = post.find('span', class_='post__time').text.lower().split()[0]
        if tag_text == "сегодня":
            return str(TODAY)
        elif tag_text == "вчера":
            return str(TODAY - timedelta(1))
        else:
            return str(tag_text)

    articles = []
    topics = []

    print(f'Парсим страницу {URL}')
    html = get(URL).text
    soup = BeautifulSoup(html, 'html5lib')
    posts = soup.findAll('article', class_="post post_preview")

    for post in posts:
        link = post.find('a', class_='post__title_link').get('href')
        title = post.find('a', class_='post__title_link').text
        date = _convert_to_date(post)
        for word in KEYWORDS:
            if word in post.text.lower():
                articles.append((date, title, link))
            else:
                if (date, title, link) not in articles:
                    if (date, title, link) not in topics:
                        topics.append((date, title, link))
    topics = set(topics) - set(articles)
    print(f'По заголовкам, тегам или описанию на странице найдено {len(articles)} подходящих статей')

    for date, title, link in tqdm(topics, desc=f'Просматриваем полное сожержимое оставшихся статей {URL}'):
        topic_soup = BeautifulSoup(get(link).text, 'html5lib').find('div',
                                                                    class_='post__text post__text-html post__text_v1')
        for word in KEYWORDS:
            if word in topic_soup.text.lower():
                articles.append((date, title, link))
    articles = tuple(set(articles))
    print(f'Всего найдено {len(articles)} подходящих статей')
    return articles


if __name__ == '__main__':
    strings = parse_habr()
    for date, title, link in strings:
        print(f'{date} - {title} - {link}')
