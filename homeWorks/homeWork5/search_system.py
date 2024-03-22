import json
import math
import os
from typing import Dict, List

from nltk import word_tokenize


# Функция для загрузки обратного индекса из файла
def get_inverted_index():
    lemmas = {}
    with open(INVERTED_INDEX_FILE, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            res = json.loads(line)
            lemmas[res['word']] = res['inverted_array']
    return lemmas


# Функция для загрузки лемм из файла
def get_lemma_tokens() -> Dict[str, str]:
    lemmas = {}
    with open(LEMMA_TOKENS_FILE, encoding='utf-8') as lemma_file:
        lines = lemma_file.readlines()
        for line in lines:
            line = line.rstrip('\n')
            words = line.split(' ')
            words[0] = words[0][:-1]
            for word in words:
                lemmas[word] = words[0]
    return lemmas


# Функция для загрузки TF-IDF относительно документа из файлов
def get_doc_to_lemma_tf_idf() -> Dict[str, Dict[str, float]]:
    result = {}
    for file_name in os.listdir(LEMMAS_TFIDF):
        with open(LEMMAS_TFIDF_PATH + file_name, encoding='utf-8') as tf_idf_file:
            lines = tf_idf_file.readlines()
            result[file_name] = {data[0]: float(data[2]) for data in [line.rstrip('\n').split(' ') for line in lines]}
    return result


# Функция для загрузки TF-IDF относительно леммы из файлов
def get_lemma_to_doc_tf_idf() -> Dict[str, Dict[str, float]]:
    result = {}
    for file_name in os.listdir(LEMMAS_TFIDF):
        with open(LEMMAS_TFIDF_PATH + file_name, encoding='utf-8') as tf_idf_file:
            lines = tf_idf_file.readlines()
            for line in lines:
                data = line.rstrip('\n').split(' ')
                lemma_to_docs_tf_idf = result.get(data[0], {})
                lemma_to_docs_tf_idf[file_name] = float(data[2])
                result[data[0]] = lemma_to_docs_tf_idf
    return result


# Функция для вычисления длины вектора документа
def calculate_doc_vector_length(doc_to_words: Dict[str, float]):
    return math.sqrt(sum(i ** 2 for i in doc_to_words.values()))


# Функция для умножения векторов запроса и документа
def multiply_vectors(query_vector: List[str], doc_vector: Dict[str, float], doc_vector_len: float):
    return sum(doc_vector.get(token, 0) for token in query_vector) / len(query_vector) / doc_vector_len


# Функция для объединения двух множеств с помощью операции объединения
def merge_or(set1, set2):
    return set1.union(set2)


# Функция для обработки пользовательского запроса
def process_query(query: str):
    tokens = word_tokenize(query, language='russian')
    lemmas = [token_to_lemma[token] for token in tokens if token in token_to_lemma]
    doc_set = set()
    for lemma in lemmas:
        doc_set = merge_or(doc_set, reverse_index.get(lemma, set()))
    results = {doc: multiply_vectors(lemmas, doc_to_lemma[f'page_{doc}.txt'], doc_lengths[f'page_{doc}.txt']) for doc in
               doc_set}
    return dict(sorted(results.items(), key=lambda r: r[1], reverse=True))


# Пути и файлы
LEMMAS_TFIDF = '../homeWork4/lemmas'
LEMMAS_TFIDF_PATH = '../homeWork4/lemmas/'
LEMMA_TOKENS_FILE = '../homeWork2/output/lemmas.txt'
INVERTED_INDEX_FILE = '../homeWork3/inverted_index.txt'

# Предварительная обработка данных
docs_list = os.listdir(LEMMAS_TFIDF)
doc_to_lemma = get_doc_to_lemma_tf_idf()
lemma_to_doc = get_lemma_to_doc_tf_idf()
doc_lengths = {doc: calculate_doc_vector_length(doc_to_lemma[doc]) for doc in docs_list}
token_to_lemma = get_lemma_tokens()
reverse_index = get_inverted_index()

# Основной цикл для запросов
if __name__ == '__main__':
    while True:
        search_input = input("Enter query (print . for exit): ")
        if search_input.lower() == '.':
            exit()
        try:
            result = process_query(search_input)
            if len(result) == 0:
                print("No results")
            else:
                print(process_query(search_input))
        except Exception as e:
            print(f"Error: {e}")
