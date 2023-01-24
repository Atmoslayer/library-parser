# Парсер книг с сайта tululu.org
Проект позволяет скачивать книги и их обложки с сайта [tululu.org](https://tululu.org/) по их id, скачивать книги конкретного жанра -
[научная фантастика](https://tululu.org/l55).
При скачивании книг можно указывать диапазон парсинга, пути скачивания книг и их обложек. В файл книги добавляются её жанры и комментарии с сайта,
если они есть, обложки скачиваются в отдельную папку. В случае скачивания книг по жанру дополнительно можно указать путь к json файлу, в который записывается информация о книгах, 
можно запустить скрипт без скачивания книг и/или картинок. 

### Как установить
Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, если есть конфликт с Python2) для установки зависимостей:
```
>>>pip install -r requirements.txt
```
### Аргументы
Для запуска парсинга по id книг используется следующая команда:
```
>>>python3 main.py
```
При запуске можно указать диапазон парсинга для id книг (по умолчанию идёт от 1 до 10), для этого 
указываются значения аргументов `--start_id` и `--end_id`:
```
>>>python3 main.py --start_id 11 --end_id 15
```

Для запуска парсинга по указанному жанру используется следующая команда:
```
>>>python3 parse_tululu_category.py
```
При запуске можно указать диапазон страниц сайта для парсинга (по умолчанию идёт от 1 до 10), для этого 
указываются значения аргументов `--start_page` и `--end_page`:
```
>>>python3 parse_tululu_category.py --start_page 1 --end_page 2
```


Чтобы пропустить скачивание текста книг, используется `--skip_txt`:
```
>>>python3 parse_tululu_category.py --skip_txt
```

Чтобы пропустить скачивание обложек книг, используется `--skip_imgs`:
```
>>>python3 parse_tululu_category.py --skip_imgs
```

По умолчанию в папке проекта создадутся папки для скачивания книг и их обложек, в случае парсинга по жанру
создаётся папка для сохранения json файла с информацией о книгах. Свои директории можно указать 
с помощью аргументов `--books_path` , `--images_path` и `--json_path`:
```
>>>python3 main.py --books_path C:\Users\atmoslayer\Documents\books --images_path C:\Users\atmoslayer\Documents\images
>>>python3 parse_tululu_category.py --books_path C:\Users\atmoslayer\Documents\books --json_path C:\Users\atmoslayer\Documents\json
```
Если указанных директорий не существует, они будут созданы.

### Цель проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).