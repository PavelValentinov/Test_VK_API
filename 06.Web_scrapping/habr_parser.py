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
        html = get(url).text  # получаем HTML-код страницы
        soup = BeautifulSoup(html, 'html5lib')  # делаем суп

        # готовим ссылку следующей страницы для парсинга
        next_url = soup.find('a', class_='arrows-pagination__item-link arrows-pagination__item-link_next').get('href')
        next_page = urljoin(URL, next_url)

        # собираем инфу о дате разамещения первого и последнего поста на странице
        first_date_on_page = soup.findAll('span', class_='post__time')[0].text.lower().split()[0]
        last_date_on_page = soup.findAll('span', class_='post__time')[-1].text.lower().split()[0]

        # смотрим, чтобы дата первого и последнего поста на странице соответствовала "сегодня" или "вчера"
        if first_date_on_page == 'сегодня' or first_date_on_page == 'вчера' \
                and last_date_on_page == 'сегодня' or last_date_on_page == 'вчера':
            posts_on_page = soup.findAll('article', class_='post post_preview')
            posts.extend(posts_on_page)  # пока условие выполняется - собираем со страницы превью-код всех постов
            parse_page_by_page(next_page)  # пока условие выполняется - рекурсим функцию с url следующей страницы
        return

    posts = []  # список превью-кода всех постов на всех страницах
    parse_page_by_page(url)
    return tuple(posts)


def text_processing(posts) -> tuple:
    """Функция парсит новости на странице по ключевым словам"""

    articles = []  # список нужных нам статей
    topics = []  # список постов, содержание которых нужно просмотреть полностью

    print('Всего статей на всех страницах', len(posts))

    for post in posts:
        # разбираем каждый пост на составные части: дата, заголовок, ссылка
        date = _convert_to_date(post)
        title = post.find('a', class_='post__title_link').text
        link = post.find('a', class_='post__title_link').get('href')

        for word in KEYWORDS:
            # ищем ключевые слова в теле превью-кода всей статьи
            # если кортеж (дата, заголовок, ссылка) ещё не находится в списке нужных статей - добавляем его туда
            if (word.lower() in post.text.lower()) and ((date, title, link) not in articles):
                articles.append((date, title, link))

                # если такой же кортеж есть в списке статей, которые нужно просмотреть полностью - убираем его оттуда
                if (date, title, link) in topics:
                    topics.remove((date, title, link))

            else:
                # если ключевое слово не найдено в превью и кортеж (date, title, link) ранее не был внесён ни в один
                # из списков - добавляем его в список постов для полного просмотра
                if ((date, title, link) not in articles) and ((date, title, link) not in topics):
                    topics.append((date, title, link))

    print(f'\nПо заголовкам, тегам или описанию найдено {len(articles)} подходящих статей\n')

    # просматриваем полное содержимое текста постов, в превью которых ключевые слова не были найдены
    for date, title, link in tqdm(topics, desc=f'Просматриваем полное содержимое оставшихся статей'):
        topic_soup = BeautifulSoup(get(link).text, 'html5lib')
        text_blocks = topic_soup.find('div', class_='post__text post__text-html post__text_v1')
        try:
            topic_text = '\n'.join([i.text for i in [block for block in text_blocks.findAll('p')]])
        except AttributeError:
            pass

        for word in KEYWORDS:
            # если хотя бы одно слово найдено
            # и кортеж (date, title, link) ещё не находится в списке нужных статей - добавляем его туда
            if word.lower() in topic_text.lower() and ((date, title, link) not in articles):
                articles.append((date, title, link))

    print(f'\nВсего за вчера и сегодня по ключевым словам "{", ".join(KEYWORDS)}" найдено {len(articles)} '
          f'подходящих статей:\n')
    return tuple(sorted(articles, reverse=True))


def _convert_to_date(post) -> str:
    """Функция приводит временные теги Хабра к формату даты"""
    tag_text = post.find('span', class_='post__time').text.lower().split()[0]  # получаем текст тега даты размещения
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
