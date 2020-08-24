from requests import get
from bs4 import BeautifulSoup
import re

KEYWORDS = ('дизайн', 'фото', 'web', 'python')
URL = "https://habr.com/ru/all/"
html = get(URL).text
soup = BeautifulSoup(html, 'html5lib')
# print(soup.prettify())
articles = soup.select('article', _class="post post_preview")
