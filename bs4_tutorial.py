import math

from bs4 import BeautifulSoup
import requests
from more_itertools import chunked


if __name__ == "__main__":
    url = 'https://tululu.org/b1/'
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'lxml')

    header_tag_text = soup.find('h1').text
    name, header = header_tag_text.split('::')

    name = name.strip()
    header = header.strip()
    print(f'Автор: {name}', f'Заголовок: {header}', sep='\n')

    test_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
    elements_quantity = math.ceil(len(test_list) / 2)
    print(elements_quantity)
    list_1 = list(chunked(test_list, elements_quantity))
    print(list_1)

