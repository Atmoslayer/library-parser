import requests
import os
import logging
from requests.exceptions import HTTPError
logging.basicConfig(level=logging.INFO)


def check_for_redirect(response, book_id):
    if response.history:
        raise HTTPError(f'No book with id {book_id}')


def save_book(book_id, folder_name):
    url = 'https://tululu.org/txt.php'
    params = {'id': book_id}
    response = requests.get(url, params=params)
    check_for_redirect(response, book_id)
    filename = f'book{book_id}.txt'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    with open(f'{folder_name}/{filename}', 'w') as file:
        file.write(response.text)


if __name__ == "__main__":
    for book_id in range(1, 11):
        try:
            save_book(book_id, 'Books')
        except HTTPError as http_error:
            print(f'HTTP error occurred: {http_error}')






