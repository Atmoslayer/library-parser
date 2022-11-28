import argparse
import requests
import os
import logging
from requests.exceptions import HTTPError
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


def parse_book(soup):
    header_tag_text = soup.find('h1').text
    book_name, author = header_tag_text.split('::')
    book_name = book_name.strip()
    author = author.strip()

    image_url = soup.find('div', class_='bookimage').find('img')['src']

    comments_tags = soup.find_all('div', class_='texts')
    comments = [comment_tag.find('span', class_='black').text for comment_tag in comments_tags if comments_tags]

    genre_tags = soup.find('span', class_='d_book').find_all('a')
    genres = [genre_tag.text for genre_tag in genre_tags if genre_tags]

    book = {
        'book_name': book_name,
        'author': author,
        'comments': comments,
        'image_url': image_url,
        'genres': genres
    }

    return book


def check_for_redirect(response, book_id):
    if response.history:
        raise HTTPError(f'No book with id {book_id}')


def download_image(image_url, book_id, folder):
    image_url_elements = os.path.splitext(image_url)
    image_type = image_url_elements[1]
    file_dir = f'{folder}/{book_id}{image_type}'
    image_link = f'https://tululu.org{image_url}'
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
    parser.add_argument('--images_path', help='Enter path to save books', type=str, default='images')
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

            book = parse_book(soup)
            download_txt(book_id, book, books_path)
            download_image(book['image_url'], book_id, images_path)
        except HTTPError as http_error:
            logging.info(f'HTTP error occurred: {http_error}')






