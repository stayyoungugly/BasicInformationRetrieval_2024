import requests
from bs4 import BeautifulSoup
import os
import shutil
import zipfile


# Функция для загрузки страницы и записи ее в файл
def download_page(url, folder_path, file_number):
    response = requests.get(url)
    if response.status_code == 200:
        with open(os.path.join(folder_path, f'page_{file_number}.html'), 'w', encoding='utf-8') as f:
            f.write(response.text)
        return True
    else:
        return False


# Функция для извлечения ссылок на страницы с Горький.ру
def extract_gorky_links(page_num):
    response = requests.get(f'https://gorky.media/reviews/page/{page_num}')
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', class_='mediaBlockInfo-link-block')
        return [link['href'] for link in links]
    else:
        return []


# Создаем временную папку для сохранения файлов
temp_folder = 'temp_gorky_pages'
if os.path.exists(temp_folder):
    shutil.rmtree(temp_folder)
os.makedirs(temp_folder)

# Скачиваем страницы и создаем файл index.txt
with open('index.txt', 'w', encoding='utf-8') as index_file:
    for page_number in range(1, 17):  # 16 страниц, по 12 ссылок на каждой
        gorky_links = extract_gorky_links(page_number)
        for i, link in enumerate(gorky_links, start=(page_number - 1) * 12 + 1):
            page_url = f'{link}'
            if download_page(page_url, temp_folder, i):
                index_file.write(f"page_{i}: {page_url}\n")
            else:
                print(f"Failed to download page {page_url}")

# Создаем ZIP-архив
with zipfile.ZipFile('gorky_pages.zip', 'w') as zipf:
    for root, dirs, files in os.walk(temp_folder):
        for file in files:
            zipf.write(os.path.join(root, file), arcname=os.path.join(root[len(temp_folder) + 1:], file))

print("Download complete.")
