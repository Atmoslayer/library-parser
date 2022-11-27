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
    image_url = soup.find('div', class_='bookimage').find('img')['src']
    author = author.strip()
    comments_tags = soup.find_all('div', class_='texts')
    comments = []
    if comments_tags:
        for comment in comments_tags:
            comments.append(comment.find('span', class_='black').text)

    book_data = {
        'book_name': book_name,
        'author': author,
        'comments': comments,
        'image_url': image_url,
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
        file.write(response.text)
        file.write('\n\nКомментарии:\n')
        for comment in book['comments']:
            file.write('%s\n' % comment)

    return os.path.join(file_dir)


if __name__ == "__main__":
    for book_id in range(1, 11):
        try:
            book_data = parse_book(book_id)
            print(download_txt(book_id, book_data))
            download_image(book_data['image_url'], book_id)
        except HTTPError as http_error:
            print(f'HTTP error occurred: {http_error}')






