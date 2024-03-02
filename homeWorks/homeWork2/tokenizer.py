import os
import re
from bs4 import BeautifulSoup
import nltk
from stop_words import get_stop_words
from nltk.tokenize import word_tokenize
import stopwordsiso as stopwordsiso
from nltk.corpus import stopwords
import pymorphy3

# Загрузка русского языкового модуля nltk
nltk.download('punkt')
nltk.download('stopwords')

# Библиотека стоп-слов
stop_words = list(get_stop_words('ru'))
# Еще одна библиотека стоп-слов
nltk_words = list(stopwords.words('russian'))
# И еще одна (чтобы максимальное количество стоп-слов убрать)
stop_words_ru = list(stopwordsiso.stopwords("ru"))

stop_words.extend(nltk_words)
stop_words_ru.extend(stop_words)

# Создание объекта для лемматизации
lemmatizer = pymorphy3.MorphAnalyzer()

# Регулярное выражение для проверки, содержит ли строка только русские символы
russian_letters = re.compile('[а-яА-ЯёЁ]+')


# Функция для фильтрации токенов
def is_valid_token(token):
    # Исключаем стоп-слова, числа, мусорные слова и буквы
    return token.isalpha() and token not in stop_words_ru and russian_letters.fullmatch(token) and len(token) > 1


# Функция для обработки HTML-файла и извлечения токенов
def process_html_file(file_path, tokens_set, lemmas_dict):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        # Извлечение текста из HTML
        text = soup.get_text()
        # Токенизация текста
        tokens = word_tokenize(text)
        # Фильтрация и лемматизация токенов
        for token in tokens:
            token = token.lower()
            if is_valid_token(token):
                tokens_set.add(token)
                lemma = lemmatizer.parse(token)[0].normal_form
                if lemma not in lemmas_dict:
                    lemmas_dict[lemma] = set()
                lemmas_dict[lemma].add(token)


# Директория с HTML-файлами
html_files_dir = '../homeWork1/temp_gorky_pages'

tokens_set = set()
lemmas_dict = {}

# Обработка всех HTML-файлов в директории
for file_name in os.listdir(html_files_dir):
    if file_name.endswith('.html'):
        file_path = os.path.join(html_files_dir, file_name)
        process_html_file(file_path, tokens_set, lemmas_dict)

# Запись токенов в файл
with open('output/tokens.txt', 'w', encoding='utf-8') as tokens_file:
    for token in tokens_set:
        tokens_file.write(token + '\n')

# Запись лемм в файл
with open('output/lemmas.txt', 'w', encoding='utf-8') as lemmas_file:
    for lemma, tokens in lemmas_dict.items():
        lemmas_file.write(lemma + ': ' + ' '.join(tokens) + '\n')
