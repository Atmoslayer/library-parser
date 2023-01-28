import argparse
import logging

import json

from http.server import HTTPServer, SimpleHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader, select_autoescape

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
                    'book_id': book['book_id']
                }
            )
            print(purified_image_url)

    rendered_page = template.render(
        books_attributes=books_attributes
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    logging.info('Starting development server at http://127.0.0.1:8000/')
    server.serve_forever()
