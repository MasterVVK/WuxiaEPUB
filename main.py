import requests
from bs4 import BeautifulSoup
from ebooklib import epub

# Функция для получения содержимого веб-страницы с заголовком User-Agent
def fetch_webpage_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

# Функция для создания EPUB файла
def create_epub(title, chapters, filename='output.epub'):
    book = epub.EpubBook()

    # Настройка метаданных
    book.set_identifier('id123456')
    book.set_title(title)
    book.set_language('ru')

    # Добавление глав
    chapter_list = []
    for idx, (chapter_title, chapter_content) in enumerate(chapters):
        chapter = epub.EpubHtml(title=chapter_title, file_name=f'chap_{idx + 1}.xhtml', lang='ru')
        chapter.content = chapter_content
        book.add_item(chapter)
        chapter_list.append(chapter)

    # Определение содержания и порядка
    book.toc = tuple(chapter_list)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Добавление стандартного стиля
    style = 'BODY { font-family: Times, serif; }'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # Установка порядка
    book.spine = ['nav'] + chapter_list

    # Сохранение файла
    epub.write_epub(filename, book)
    print(f'EPUB файл "{filename}" успешно создан!')

# Список ссылок на главы
base_url = 'https://wuxiaworld.ru/mir-bessmertnyh/mir-bessmertnyh-glava-'
num_chapters = 3  # Укажите количество глав, которые хотите спарсить

urls = [f'{base_url}{i}-razrushit-pustotu/' for i in range(1, num_chapters + 1)]

# Извлечение данных и создание списка глав
chapters = []
for url in urls:
    try:
        html_content = fetch_webpage_content(url)
        soup = BeautifulSoup(html_content, 'html.parser')

        # Извлечение заголовка и текста главы
        chapter_title = soup.find('h1').text if soup.find('h1') else 'Без названия'
        chapter_body_tag = soup.find('div', class_='entry-content')

        if chapter_body_tag:
            for unwanted in chapter_body_tag.find_all(['a', 'script', 'style', 'iframe', 'ins']):
                unwanted.decompose()

            chapter_body = ''.join(str(tag) for tag in chapter_body_tag.find_all(['p', 'h2', 'h3', 'br']))
            chapter_body = chapter_body.replace('\n', '').strip()

            chapters.append((chapter_title, chapter_body))
            print(f'Глава "{chapter_title}" успешно добавлена.')
        else:
            print(f'Текст главы не найден для {url}')
    except requests.exceptions.HTTPError as e:
        print(f'HTTP ошибка при обработке {url}: {e}')
    except Exception as e:
        print(f'Произошла ошибка при обработке {url}: {e}')

# Создание EPUB файла
if chapters:
    create_epub('Мир Бессмертных', chapters, 'mir_bessmertnyh_full.epub')
