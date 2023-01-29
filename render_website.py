import argparse
import logging
import math

import json

from http.server import HTTPServer, SimpleHTTPRequestHandler
from livereload import Server, shell
from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Website render')
    parser.add_argument('--books_path', help='Enter path to access books', type=str, default='books')
    parser.add_argument('--images_path', help='Enter path to access images', type=str, default='images')
    parser.add_argument('--json_path', help='Enter path to save json file', type=str, default='json')

    arguments = parser.parse_args()
    books_path = arguments.books_path
    images_path = arguments.images_path
    json_path = arguments.json_path

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('index.html')

    file_dir = f'{json_path}/books'
    books_attributes = []

    with open(f'{file_dir}.json', 'r', encoding='utf-8') as data:
        books_json = json.load(data)
        for book in books_json:
            purified_image_url = book['image_url'].replace('/shots/', '').replace('/images/', '')
            if 'nopic' in purified_image_url:
                purified_image_url = None

            books_attributes.append(
                {
                    'book_name': book['book_name'],
                    'author': book['author'],
                    'comments': book['comments'],
                    'image_url': purified_image_url,
                    'genres': book['genres'],
                    'image_path': images_path,
                    'book_path': books_path,
                    'book_id': book['book_id']
                }
            )

    elements_quantity = math.ceil(len(books_attributes) / 2)
    divided_books_attributes = list(chunked(books_attributes, elements_quantity))
    books_attributes_col_1 = divided_books_attributes[0]
    books_attributes_col_2 = divided_books_attributes[1]

    rendered_page = template.render(
        books_attributes_col_1=books_attributes_col_1,
        books_attributes_col_2=books_attributes_col_2
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
    # HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)

    server = Server()
    server.watch('index.html', shell('make html', cwd='docs'))
    logging.info('Starting development server at http://127.0.0.1:8000/')
    server.serve()
