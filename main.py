import argparse
import requests
import os
import logging
import time
from urllib.parse import urljoin
from requests.exceptions import HTTPError, ConnectionError
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


def parse_book(soup, book_id, books_path, images_path):
    header_selector = 'h1'
    header_tag_text = soup.select_one(header_selector).text
    book_name, author = header_tag_text.split('::')
    book_name = book_name.strip()
    author = author.strip()

    image_selector = '.bookimage img'
    image_url = soup.select_one(image_selector)['src']
    comments_selector = '.texts .black'
    comments_tags = soup.select(comments_selector)
    comments = [comment_tag.text for comment_tag in comments_tags if comments_tags]

    genres_selector = 'span.d_book a'
    genre_tags = soup.select(genres_selector)
    genres = [genre_tag.text for genre_tag in genre_tags if genre_tags]

    purified_book_name = book_name \
        .replace(':', '') \
        .replace('/', '') \
        .replace('?', '') \
        .replace('*', '') \
        .replace('|', '') \
        .replace('<', '') \
        .replace('>', '')

    book = {
        'book_name': purified_book_name,
        'author': author,
        'comments': comments,
        'image_url': image_url,
        'genres': genres,
        'book_id': book_id,
        'books_path': books_path,
        'images_path': images_path
    }

    return book


def check_for_redirect(response, book_id):
    if response.history:
        raise HTTPError(f'No book with id {book_id}')


def download_image(image_url, book_id, folder):
    image_url_elements = os.path.splitext(image_url)
    image_type = image_url_elements[1]
    file_dir = f'{folder}/{book_id}{image_type}'
    image_link = urljoin(f'https://tululu.org/b{book_id}', image_url)
    response = requests.get(image_link)
    response.raise_for_status()

    os.makedirs(folder, exist_ok=True)

    with open(f'{file_dir}', 'ab') as image:
        image.write(response.content)


def download_txt(book_id, book, folder):
    book_name = book['book_name']
    url = 'https://tululu.org/txt.php'
    params = {'id': book_id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response, book_id)

    pure_filename = sanitize_filename(f'{book_id}.{book_name}')

    os.makedirs(folder, exist_ok=True)

    file_dir = f'{folder}/{pure_filename}'

    with open(f'{file_dir}.txt', 'w') as file:

        file.write('Жанры: ')
        for genre in book['genres']:
            file.write('%s' % f'{genre} ')
            file.write(f'\n{response.text}')
            file.write('\n\nКомментарии:\n')
            for comment in book['comments']:
                file.write('%s\n' % comment)

    return os.path.join(file_dir)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Library parser')
    parser.add_argument('--books_path', help='Enter path to save books', type=str, default='books')
    parser.add_argument('--images_path', help='Enter path to save images', type=str, default='images')
    parser.add_argument('--start_id', help='Enter start book id', default=1, type=int)
    parser.add_argument('--end_id', help='Enter end book id', default=10, type=int)
    arguments = parser.parse_args()
    books_path = arguments.books_path
    images_path = arguments.images_path
    start_id = arguments.start_id
    end_id = arguments.end_id

    url = 'https://tululu.org/'

    for book_id in range(start_id, end_id + 1):
        try:
            response = requests.get(f'{url}b{book_id}/')
            response.raise_for_status()
            check_for_redirect(response, book_id)
            soup = BeautifulSoup(response.text, 'lxml')

            book = parse_book(soup, book_id, books_path, images_path)
            download_txt(book_id, book, books_path)
            download_image(book['image_url'], book_id, images_path)
        except HTTPError as http_error:
            logging.info(f'\nHTTP error occurred: {http_error}')

        except ConnectionError as connection_error:
            logging.info(f'\nConnection error occurred: {connection_error}')
            time.sleep(5)






