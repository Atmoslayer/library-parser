import argparse
import requests
import os
import logging
from requests.exceptions import HTTPError
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)


def parse_book(book_id):
    url = 'https://tululu.org/'
    response = requests.get(f'{url}b{book_id}/')
    check_for_redirect(response, book_id)
    soup = BeautifulSoup(response.text, 'lxml')

    header_tag_text = soup.find('h1').text
    book_name, author = header_tag_text.split('::')
    book_name = book_name.strip()
    author = author.strip()

    image_url = soup.find('div', class_='bookimage').find('img')['src']

    comments_tags = soup.find_all('div', class_='texts')
    comments = []
    if comments_tags:
        for comment_tag in comments_tags:
            comments.append(comment_tag.find('span', class_='black').text)

    genres = []
    genre_tags = soup.find('span', class_='d_book').find_all('a')
    for genre_tag in genre_tags:
        genres.append(genre_tag.text)

    book_data = {
        'book_name': book_name,
        'author': author,
        'comments': comments,
        'image_url': image_url,
        'genres': genres
    }

    return book_data


def check_for_redirect(response, book_id):
    if response.history:
        raise HTTPError(f'No book with id {book_id}')


def download_image(image_url, book_id, folder='images'):
    image_url_elements = os.path.splitext(image_url)
    image_type = image_url_elements[1]
    file_dir = f'{folder}/{book_id}{image_type}'
    image_link = f'https://tululu.org{image_url}'
    response = requests.get(image_link)

    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(f'{file_dir}', 'ab') as image:
        image.write(response.content)


def download_txt(book_id, book, folder='books'):
    book_name = book['book_name']
    url = 'https://tululu.org/txt.php'
    params = {'id': book_id}
    response = requests.get(url, params=params)
    check_for_redirect(response, book_id)

    pure_filename = sanitize_filename(f'{book_id}.{book_name}')
    if not os.path.exists(folder):
        os.makedirs(folder)

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
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_id', help='Start book id', default=1, type=int)
    parser.add_argument('--end_id', help='End book id', default=10, type=int)
    arguments = parser.parse_args()
    start_id = arguments.start_id
    end_id = arguments.end_id
    for book_id in range(start_id, end_id + 1):
        try:
            book_data = parse_book(book_id)
            download_txt(book_id, book_data)
            download_image(book_data['image_url'], book_id)
        except HTTPError as http_error:
            print(f'HTTP error occurred: {http_error}')






