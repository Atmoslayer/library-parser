import argparse
import logging
import math
import os
import urllib

import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from livereload import Server, shell
from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked


def parse_json(json_path, books_path, images_path):

    with open(f'{json_path}/books.json', 'r', encoding='utf-8') as data:
        books_attributes = json.load(data)
        for book in books_attributes:
            book_url = f'{books_path}/{book["book_id"]}.{book["book_name"]}.txt'
            if not os.path.exists(book_url):
                book['book_name'] = None
            else:
                purified_image_path = book['image_url'].replace('/shots/', '').replace('/images/', '')
                if 'nopic' in purified_image_path:
                    purified_image_path = f'{book["book_id"]}.gif'
                image_url = f'{images_path}/{purified_image_path}'
                book['image_url'] = urllib.parse.quote(image_url)
                book['book_url'] = urllib.parse.quote(book_url)

        purified_books_attributes = [book for book in books_attributes if book['book_name']]
        return purified_books_attributes


def render_pages(books_attributes, books_quantity, pages_path):

    splitted_books_attributes = list(chunked(books_attributes, books_quantity))

    for page_number, part_of_books_attributes in enumerate(splitted_books_attributes, start=1):

        pages_dir = f'{pages_path}/index{page_number}'

        books_cards_per_col = math.ceil(len(part_of_books_attributes) / 2)

        divided_books_attributes = list(chunked(part_of_books_attributes, books_cards_per_col))
        rendered_page = template.render(
            divided_books_attributes=divided_books_attributes,
            pages_path=pages_path,
            page_index=page_number,
            pages_quantity=len(splitted_books_attributes)
        )

        with open(f'{pages_dir}.html', 'w', encoding='utf8') as file:
            file.write(rendered_page)


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Website render')
    parser.add_argument('--books_path', help='Enter path to access books', type=str, default='media/books')
    parser.add_argument('--images_path', help='Enter path to access images', type=str, default='media/images')
    parser.add_argument('--json_path', help='Enter path to save json file', type=str, default='json')
    parser.add_argument('--pages_path', help='Enter path to save pages', type=str, default='pages')
    parser.add_argument('--books_quantity', help='Enter the number of books per page', type=int, default=20)

    arguments = parser.parse_args()
    books_path = arguments.books_path
    images_path = arguments.images_path
    json_path = arguments.json_path
    pages_path = arguments.pages_path
    books_quantity = arguments.books_quantity

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('/template.html')

    books_attributes = parse_json(json_path, books_path, images_path)
    render_pages(books_attributes, books_quantity, pages_path)

    os.makedirs(pages_path, exist_ok=True)

    server = Server()
    for page in os.listdir(pages_path):
        page = os.path.join(pages_path, page)
        server.watch(page, shell('make html', cwd='docs'))
    logging.info('Starting development server at http://127.0.0.1:5500/')
    server.serve()
