from datetime import date, timedelta

from bs4 import BeautifulSoup
from requests import get
from tqdm import tqdm

KEYWORDS = ('дизайн', 'фото', 'web', "python")
URL = "https://habr.com/ru/all/"
TODAY = date.today()


def parser():
    def _convert_to_date(post) -> str:
        tag_text = post.find('span', class_='post__time').text.lower().split()[0]
        if tag_text == "сегодня":
            return str(TODAY)
        elif tag_text == "вчера":
            return str(TODAY - timedelta(1))
        else:
            return str(tag_text)

    posts = []
    topics = []

    print(f'Парсим страницу {URL}')
    html = get(URL).text
    soup = BeautifulSoup(html, 'html5lib')
    articles = soup.findAll('article', class_="post post_preview")

    for article in articles:
        link = article.find('a', class_='post__title_link').get('href')
        title = article.find('a', class_='post__title_link').text
        date = _convert_to_date(article)
        for word in KEYWORDS:
            if word in article.text.lower():
                posts.append((date, title, link))
            else:
                if (date, title, link) not in posts:
                    if (date, title, link) not in topics:
                        topics.append((date, title, link))
    topics = set(topics) - set(posts)
    print(f'По заголовкам, тегам или описанию на странице найдено {len(posts)} подходящих статей')

    for date, title, link in tqdm(topics, desc=f'Просматриваем полное сожержимое оставшихся статей {URL}'):
        topic_soup = BeautifulSoup(get(link).text, 'html5lib').find('div',
                                                                    class_='post__text post__text-html post__text_v1')
        for word in KEYWORDS:
            if word in topic_soup.text.lower():
                posts.append((date, title, link))
    posts = tuple(set(posts))
    print(f'Всего найдено {len(posts)} подходящих статей')
    return posts


if __name__ == '__main__':
    strings = parser()
    for date, title, link in strings:
        print(f'{date} - {title} - {link}')
