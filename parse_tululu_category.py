import argparse
import requests
import os
import logging
import time
from urllib.parse import urljoin
from requests.exceptions import HTTPError, ConnectionError
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
import json
from main import *
from progress.bar import IncrementalBar


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Library category parser')
    parser.add_argument('--books_path', help='Enter path to save books', type=str, default='books')
    parser.add_argument('--images_path', help='Enter path to save books', type=str, default='images')
    parser.add_argument('--json_path', help='Enter path to save json file', type=str, default='json')
    parser.add_argument('--start_page', help='Enter start page number', default=1, type=int)
    parser.add_argument('--end_page', help='Enter end page number', default=10, type=int)

    arguments = parser.parse_args()
    books_path = arguments.books_path
    images_path = arguments.images_path
    json_path = arguments.json_path
    start_page = arguments.start_page
    end_page = arguments.end_page

    category_id = 'l55'
    url = 'https://tululu.org/'
    category_page_url = f'{url}{category_id}/'
    books_data = []

    for page_number in range(start_page, end_page + 1):

        try:
            category_page_response = requests.get(f'{category_page_url}/{page_number}')
            category_page_response.raise_for_status()
            category_page_soup = BeautifulSoup(category_page_response.text, 'lxml')
            book_ids_tags = category_page_soup.find_all('table', class_='d_book')
            bar = IncrementalBar(f'Books downloaded from page {page_number}', max=len(book_ids_tags))

            for book_id_tag in book_ids_tags:
                try:
                    book_id = book_id_tag.find('a')['href']
                    purified_book_id = book_id.replace('/', '').replace('b', '')
                    book_url = f'https://tululu.org/b{purified_book_id}'
                    book_response = requests.get(book_url)
                    book_response.raise_for_status()
                    book_soup = BeautifulSoup(book_response.text, 'lxml')
                    book = parse_book(book_soup)
                    books_data.append(book)

                    bar.next()
                    download_txt(purified_book_id, book, books_path)
                    download_image(book['image_url'], purified_book_id, images_path)

                except HTTPError as http_error:
                    logging.info(f'\nHTTP error occurred: {http_error}')

                except ConnectionError as connection_error:
                    logging.info(f'\nConnection error occurred: {connection_error}')
                    time.sleep(5)

        except HTTPError as http_error:
            logging.info(f'\nHTTP error occurred: {http_error}')

        except ConnectionError as connection_error:
            logging.info(f'\nConnection error occurred: {connection_error}')
            time.sleep(5)

    books_json = json.dumps(book)

    os.makedirs(json_path, exist_ok=True)
    file_dir = f'{json_path}/books'

    with open(f'{file_dir}.json', 'w', encoding='utf8') as file:

        json.dump(books_data, file, ensure_ascii=False, indent=3)