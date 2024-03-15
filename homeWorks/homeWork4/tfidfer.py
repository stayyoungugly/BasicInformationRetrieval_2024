import json
import math
import os
import re

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from pymorphy3 import MorphAnalyzer

# Устанавливаем парсер для BeautifulSoup
parser = 'html.parser'

# Инициализируем морфологический анализатор
morph = MorphAnalyzer()


# Функция для построения инвертированного индекса токенов из ZIP-файла
def get_inverted_index_tokens(pages_dir):
    index = {}

    # Получаем список файлов в папке
    files = os.listdir(pages_dir)

    for i, filename in enumerate(files):
        with open(os.path.join(pages_dir, filename), 'r', encoding='utf-8') as file:
            text = file.read()
            tokens = tokenize(text, True)

            print(filename)

            for token in tokens:
                if token in index:
                    index[token].add(i)
                else:
                    index[token] = {i}
    return index


# Функция для извлечения уникальных отфильтрованных токенов из списка и преобразования их в список
def get_unique_filtered_tokens(tokens, is_set):
    res = []
    for token in tokens:
        if token.lower() not in stopwords.words("russian") and re.compile("^[а-яё]+$").match(token.lower()):
            res.append(token.lower())
    if is_set:
        return list(res)
    else:
        return list(res)


# Функция для получения токенов из текста
def tokenize(text, is_set):
    tokens = word_tokenize(text.replace('.', ' '))
    return get_unique_filtered_tokens(tokens, is_set)


# Функция для чтения инвертированного индекса лемм из файла
def read_lemmas():
    lemmas = {}
    with open(inverted_index_file_dir, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            res = json.loads(line)
            lemmas[res['word']] = res['inverted_array']
    return lemmas


# Функция для вычисления TF (частоты термина)
def get_tf(q, tokens):
    return tokens.count(q) / float(len(tokens))


# Функция для вычисления IDF (обратной частоты документа)
def get_idf(q, index, docs_count=100):
    return math.log(docs_count / float(len(index[q])))


# Функция для лемматизации слова
def lemmatize(word):
    return morph.parse(word.replace("\n", ""))[0].normal_form


# Функция для вычисления TF-IDF и записи результатов в файлы
def get_tfidf(pages_dir, lemmas_index, tokens_index):
    # Получаем список файлов в папке
    files = os.listdir(pages_dir)

    for filename in files:
        with open(os.path.join(pages_dir, filename), 'r', encoding='utf-8') as file:
            text = file.read()

            tokens = tokenize(text, False)
            lemmas = list(map(lemmatize, tokens))

            res_tokens = []
            for token in set(tokens):
                if token in tokens_index:
                    tf = get_tf(token, tokens)
                    idf = get_idf(token, tokens_index)
                    res_tokens.append(f"{token} {idf} {tf * idf}")

            with open(f"{tokens_tfidf_dir}{filename.replace('.html', '')}.txt", "w", encoding='utf-8') as token_f:
                token_f.write("\n".join(res_tokens) + ',')

            res_lemmas = []
            for lemma in set(lemmas):
                if lemma in lemmas_index:
                    tf = get_tf(lemma, lemmas)
                    idf = get_idf(lemma, lemmas_index)
                    res_lemmas.append(f"{lemma} {idf} {tf * idf}")

            with open(f"{lemmas_tfidf_dir}{filename.replace('.html', '')}.txt", "w", encoding='utf-8') as lemma_f:
                lemma_f.write("\n".join(res_lemmas))


# Пути к нужным файлам
pages_dir = "../homeWork1/temp_gorky_pages/"
inverted_index_file_dir = '../homeWork3/inverted_index.txt'
tokens_tfidf_dir = 'tokens/'
lemmas_tfidf_dir = 'lemmas/'


# Основная функция
def main():
    # Загрузка необходимых ресурсов NLTK
    nltk.download('punkt')
    nltk.download('stopwords')

    # Получение инвертированного индекса токенов
    inverted_index_tokens = get_inverted_index_tokens(pages_dir)

    # Чтение инвертированного индекса лемм
    read_inverted_index = read_lemmas()

    # Вычисление TF-IDF и запись результатов в файлы
    get_tfidf(pages_dir, read_inverted_index, inverted_index_tokens)


# Запуск основной функции
if __name__ == '__main__':
    main()
