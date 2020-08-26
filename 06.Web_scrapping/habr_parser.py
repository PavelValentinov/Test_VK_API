"""
Парсер для создания дайджеста новостей Хабра по ключевым словам.
Новости собираются за 2 последних дня (сегодня и вчера).
В случае совпадения по искомым словам могут быть захвачены несколько статей трёхдневной давности.
"""

from datetime import date, timedelta
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from requests import get
from tqdm import tqdm

KEYWORDS = ('дизайн', 'фото', 'web', 'python')
URL = "https://habr.com/ru/all/"
TODAY = date.today()


def parse_habr(url) -> tuple:
    """Функция принимает URL новостей Хабра и парсит новости за 2 последних дня (вчера и сегодня)"""

    def parse_page_by_page(url) -> None:
        """ Рекурсивная функция, разбирающая код каждой страницы на отдельные блоки со статьями.
        Рекурсия продолжает выполняться до тех пор, пока дата размещения последней статьи на странице не будет
        позже вчерашнего дня. """

        print(f'Парсим страницу {url}')
        html = get(url).text
        soup = BeautifulSoup(html, 'html5lib')
        next_url = soup.find('a', class_='arrows-pagination__item-link arrows-pagination__item-link_next').get('href')
        next_page = urljoin(URL, next_url)
        first_date_on_page = soup.findAll('span', class_='post__time')[0].text.lower().split()[0]
        last_date_on_page = soup.findAll('span', class_='post__time')[-1].text.lower().split()[0]

        if first_date_on_page == 'сегодня' or first_date_on_page == 'вчера' \
                and last_date_on_page == 'сегодня' or last_date_on_page == 'вчера':
            posts_on_page = soup.findAll('article', class_='post post_preview')
            topics.extend(posts_on_page)
            parse_page_by_page(next_page)
        return

    topics = []
    parse_page_by_page(url)
    return tuple(topics)


def text_processing(posts) -> tuple:
    """Функция парсит новости на странице по ключевым словам"""
    articles = []
    topics = []

    for post in posts:
        link = post.find('a', class_='post__title_link').get('href')
        title = post.find('a', class_='post__title_link').text
        date = _convert_to_date(post)
        for word in KEYWORDS:
            if word.lower() in post.text.lower():
                articles.append((date, title, link))
            else:
                if (date, title, link) not in articles or topics:
                    topics.append((date, title, link))
    topics = set(topics) - set(articles)
    print(f'\nПо заголовкам, тегам или описанию найдено {len(articles)} подходящих статей\n')

    for date, title, link in tqdm(topics, desc=f'Просматриваем полное содержимое оставшихся статей'):
        topic_soup = BeautifulSoup(get(link).text, 'html5lib').find('div',
                                                                    class_='post__text post__text-html post__text_v1')
        for word in KEYWORDS:
            if word.lower() in topic_soup.text.lower():
                articles.append((date, title, link))
    articles = set(articles)
    print(f'\nВсего за вчера и сегодня по ключевым словам "{", ".join(KEYWORDS)}" найдено {len(articles)} '
          f'подходящих статей:\n')
    return tuple(sorted(articles, reverse=True))


def _convert_to_date(post) -> str:
    """Функция приводит временные теги Хабра к формату даты"""
    tag_text = post.find('span', class_='post__time').text.lower().split()[0]
    if tag_text == 'сегодня':
        return str(TODAY)
    elif tag_text == 'вчера':
        return str(TODAY - timedelta(1))
    else:
        return str(tag_text)


def main() -> None:
    """ Основная функция модуля """
    print()
    strings = text_processing(parse_habr(URL))
    for date, title, link in strings:
        print(f'{date} - {title} - {link}')


if __name__ == '__main__':
    main()
