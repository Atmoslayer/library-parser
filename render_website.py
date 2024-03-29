import argparse
import json
import logging
import math
import os
import urllib

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server, shell
from more_itertools import chunked


def get_books_attributes(json_path):

    with open(f'{json_path}/books.json', 'r', encoding='utf-8') as data:
        books_attributes = json.load(data)

        for book in books_attributes:
            book_url = f'{book["books_path"]}/{book["book_id"]}.{book["book_name"]}.txt'
            book_url = book_url.replace('\\', '/')

            if not os.path.exists(book_url):
                book['book_name'] = None
            else:
                purified_image_path = book['image_url'].replace('/shots/', '').replace('/images/', '')
                if 'nopic' in purified_image_path:
                    purified_image_path = f'{book["book_id"]}.gif'
                image_url = f'{book["images_path"]}/{purified_image_path}'
                book['image_url'] = image_url.replace('\\', '/')
                book['book_url'] = book_url

        purified_books_attributes = [book for book in books_attributes if book['book_name']]
        return purified_books_attributes


def render_pages():
    template = env.get_template('/template.html')
    splitted_books_attributes = list(chunked(books_attributes, books_quantity))

    for page_number, part_of_books_attributes in enumerate(splitted_books_attributes, start=1):

        books_cards_per_col = math.ceil(len(part_of_books_attributes) / 2)

        divided_books_attributes = list(chunked(part_of_books_attributes, books_cards_per_col))
        rendered_page = template.render(
            divided_books_attributes=divided_books_attributes,
            pages_path=pages_path,
            page_index=page_number,
            pages_quantity=len(splitted_books_attributes)
        )

        with open(f'{pages_path}/index{page_number}.html', 'w', encoding='utf8') as file:
            file.write(rendered_page)


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Website render')
    parser.add_argument('--json_path', help='Enter path to save json file', type=str, default='json')
    parser.add_argument('--pages_path', help='Enter path to save pages', type=str, default='pages')
    parser.add_argument('--books_quantity', help='Enter the number of books per page', type=int, default=20)

    arguments = parser.parse_args()
    json_path = arguments.json_path
    pages_path = arguments.pages_path
    books_quantity = arguments.books_quantity

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    books_attributes = get_books_attributes(json_path)
    render_pages()

    server = Server()
    server.watch('template.html', render_pages)
    logging.info('Starting development server at http://127.0.0.1:5500/')
    server.serve(root='.')

