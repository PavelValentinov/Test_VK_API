import hashlib
import json

from requests import get

URL = "https://en.wikipedia.org/w/api.php"
PARAMS = {
    "action": "opensearch",
    "namespace": "0",
    "limit": "1",
    "format": "json"
}


class MyIter:
    def __init__(self, filename: json):
        with open(filename, 'r', encoding="UTF-8") as f:
            self.countries = [dic['name']['common'] for dic in json.load(f)]
        self.counter = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.counter < len(self.countries):
            country = self.countries[self.counter]
            PARAMS.update({"search": country})
            response = get(url=URL, params=PARAMS).json()
            link = response[-1][0]
            string = f'{country} - {link}\n'
            with open("countries.txt", 'a', encoding='UTF-8') as f:
                f.write(string)
            self.counter += 1
            return string
        else:
            # # если нужно сделать итератор многоразовым - обнуляем счётчик
            #     self.counter = 0
            raise StopIteration

    @staticmethod
    def hash_gen():
        with open("countries.txt", 'rb') as f:
            for line in f:
                yield hashlib.md5(line).hexdigest()


if __name__ == '__main__':
    my_iter = MyIter('countries.json')
    md5 = my_iter.hash_gen()
    # for i in range(len(my_iter.countries)):
    #     print(next(my_iter), end='\t')
    #     print(next(md5))
    #     print()
    for item in my_iter:
        print(item, end='')
        print(next(md5))
        print()
