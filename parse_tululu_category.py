import json
from main import *
from progress.bar import IncrementalBar


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Library category parser')
    parser.add_argument('--books_path', help='Enter path to save books', type=str, default='books')
    parser.add_argument('--images_path', help='Enter path to save books', type=str, default='images')
    parser.add_argument('--json_path', help='Enter path to save json file', type=str, default='json')
    parser.add_argument('--start_page', help='Enter start page number', default=1, type=int)
    parser.add_argument('--end_page', help='Enter end page number', default=10, type=int)
    parser.add_argument(
        '--skip_txt',
        help='Enter "True" if you do not want to download books',
        action='store_true'
    )
    parser.add_argument(
        '--skip_imgs',
        help='Enter "True" if you do not want to download images',
        action='store_true'
    )

    arguments = parser.parse_args()
    books_path = arguments.books_path
    images_path = arguments.images_path
    json_path = arguments.json_path
    start_page = arguments.start_page
    end_page = arguments.end_page
    skip_txt = arguments.skip_txt
    skip_images = arguments.skip_imgs

    category_id = 'l55'
    url = 'https://tululu.org/'
    category_page_url = f'{url}{category_id}/'
    books_attributes = []

    for page_number in range(start_page, end_page + 1):

        try:
            category_page_response = requests.get(f'{category_page_url}/{page_number}')
            category_page_response.raise_for_status()
            check_for_redirect(category_page_response, page_number)
            category_page_soup = BeautifulSoup(category_page_response.text, 'lxml')
            book_selector = 'table.d_book'
            books_ids_tags = category_page_soup.select(book_selector)
            bar = IncrementalBar(f'Books downloaded from page {page_number}', max=len(books_ids_tags))

            for book_id_tag in books_ids_tags:
                try:
                    id_selector = 'a'
                    book_id = book_id_tag.select_one(id_selector)['href']
                    purified_book_id = book_id.replace('/', '').replace('b', '')
                    book_url = f'https://tululu.org/b{purified_book_id}/'
                    book_response = requests.get(book_url)
                    book_response.raise_for_status()
                    check_for_redirect(book_response, book_id)
                    book_soup = BeautifulSoup(book_response.text, 'lxml')
                    book = parse_book(book_soup)
                    books_attributes.append(book)

                    bar.next()
                    if not skip_txt:
                        try:
                            download_txt(purified_book_id, book, books_path)
                        except UnicodeEncodeError as unicode_error:
                            logging.info(f'\nUnicode encode error occurred: {unicode_error}')
                    if not skip_images:
                        download_image(book['image_url'], purified_book_id, images_path)

                except HTTPError as http_error:
                    logging.info(f'\nHTTP error occurred: {http_error}')

                except ConnectionError as connection_error:
                    logging.info(f'\nConnection error occurred: {connection_error}')
                    time.sleep(5)

        except HTTPError as http_error:
            logging.info(f'\nHTTP error occurred: {http_error}')

        except ConnectionError as connection_error:
            logging.info(f'\nConnection error occurred: {connection_error}')
            time.sleep(5)

    os.makedirs(json_path, exist_ok=True)
    file_dir = f'{json_path}/books'

    with open(f'{file_dir}.json', 'w', encoding='utf8') as file:

        json.dump(books_attributes, file, ensure_ascii=False, indent=3)