import argparse
import logging
import math
import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from livereload import Server, shell
from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked


def parse_json(json_path, books_path, images_path):
    file_dir = f'{json_path}/books'

    with open(f'{file_dir}.json', 'r', encoding='utf-8') as data:
        books_attributes = json.load(data)
        for book in books_attributes:
            purified_image_url = book['image_url'].replace('/shots/', '').replace('/images/', '')
            if 'nopic' in purified_image_url:
                purified_image_url = None
            book['image_url'] = purified_image_url
            book['book_path'] = books_path
            book['image_path'] = images_path

        return books_attributes


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

    os.makedirs(pages_path, exist_ok=True)

    splitted_books_attributes = list(chunked(books_attributes, books_quantity))

    for page_number, part_of_books_attributes in enumerate(splitted_books_attributes):

        templates_dir = f'{pages_path}/index{page_number + 1}'

        books_per_col = math.ceil(len(part_of_books_attributes) / 2)
        divided_books_attributes = list(chunked(part_of_books_attributes, books_per_col))
        books_attributes_col_1 = divided_books_attributes[0]
        books_attributes_col_2 = divided_books_attributes[1]
        page_dir = f'{templates_dir}.html'
        rendered_page = template.render(
            books_attributes_col_1=books_attributes_col_1,
            books_attributes_col_2=books_attributes_col_2,
            pages_path=pages_path,
            page_index=page_number + 1,
            pages_quantity=len(splitted_books_attributes)
        )

        with open(page_dir, 'w', encoding="utf8") as file:
            file.write(rendered_page)


    server = Server()
    server.watch(f'{pages_path}/index.html', shell('make html', cwd='docs'))
    logging.info('Starting development server at http://127.0.0.1:5500/')
    server.serve()
