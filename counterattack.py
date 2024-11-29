import requests
from bs4 import BeautifulSoup
from ebooklib import epub
import time  # Импортируем модуль для работы с паузами

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
    book.set_identifier('id100001')
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

# Начальный URL
start_url = 'https://wuxiaworld.ru/imperator-syanvu/kontrataka-izgnannogo-uchenika-glava-1-uchenik-sekty/'

# Извлечение данных и создание списка глав
chapters = []
current_url = start_url
chapter_count = 0
max_chapters = 1#3365  # Ограничение на количество первых глав

while current_url and chapter_count < max_chapters:
    try:
        html_content = fetch_webpage_content(current_url)
        soup = BeautifulSoup(html_content, 'html.parser')

        # Извлечение заголовка и текста главы
        chapter_title = soup.find('h1').text if soup.find('h1') else 'Без названия'
        chapter_body_tag = soup.find('div', class_='entry-content')

        if chapter_body_tag:
            for unwanted in chapter_body_tag.find_all(['a', 'script', 'style', 'iframe', 'ins']):
                unwanted.decompose()

            for unwanted_text in ['Редактируется Читателями!',
                                  'Читать»', 'Автор: Six Circles three',
                                  'Перевод: Artificial_Intelligence',
                                  #'Нет главы и т.п. - пиши в Комменты. Читать без рекламы !',
                                  'Нет главы и т.п.',
                                  'BANISHED DISCIPLE’S COUNTERATTACK']:
                for unwanted in chapter_body_tag.find_all(string=lambda text: unwanted_text in text):
                    unwanted.extract()

            chapter_body = ''.join(str(tag) for tag in chapter_body_tag.find_all(['p', 'h2', 'h3', 'br']))
            chapter_body = chapter_body.replace('\n', '').strip()

            chapters.append((chapter_title, chapter_body))
            print(f'Глава "{chapter_title}" успешно добавлена.')
            print(chapter_body)
            chapter_count += 1
        else:
            print(f'Текст главы не найден для {current_url}')

        # Найти URL следующей главы (кнопка с rel="Вперед")
        next_button = soup.find('a', rel='Вперед')
        if next_button:
            current_url = next_button['href']
        else:
            print('Ссылка на следующую главу не найдена. Парсинг завершен.')
            break

        # Пауза перед следующим запросом
        time.sleep(2)  # Пауза в 5 секунд (можно увеличить при необходимости)

    except requests.exceptions.HTTPError as e:
        print(f'HTTP ошибка при обработке {current_url}: {e}')
        print('Ожидание перед повтором...')
        time.sleep(30)  # Пауза в 30 секунд при возникновении ошибки 503
        continue  # Повторить попытку
    except Exception as e:
        print(f'Произошла ошибка при обработке {current_url}: {e}')
        break

# Создание EPUB файла
if chapters:
    create_epub('Контратака изгнанного ученика', chapters, 'Counterattack_full.epub')
