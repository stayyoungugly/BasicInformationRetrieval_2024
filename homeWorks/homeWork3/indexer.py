import nltk
import json
import os
from bs4 import BeautifulSoup
from pymorphy3 import MorphAnalyzer
from pyparsing import Word, Suppress, Group, Forward, srange, CaselessLiteral, ZeroOrMore


# Функция для чтения лемм из файла и создания словаря лемма: токены
def parse_lemmas_from_file(file_path):
    lemmas_dict = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            lemma, tokens_str = line.strip().split(': ')
            tokens = tokens_str.split()
            for token in tokens:
                lemmas_dict[token] = lemma
    return lemmas_dict


# Функция для построения обратного индекса из HTML-файлов
def create_html_index(html_files_dir, lemmas_dir):
    index = {}
    for doc_i in range(1, 192):
        file_path = os.path.join(html_files_dir, f'page_{doc_i}.html')
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                text = soup.get_text()
                words = [token.lower() for token in nltk.word_tokenize(text)]
                for word in words:
                    lemma = lemmas_dir.get(word)
                    if lemma:
                        if lemma not in index:
                            index[lemma] = {'count': 0, 'inverted_array': []}
                        if doc_i not in index[lemma]['inverted_array']:
                            index[lemma]['inverted_array'].append(doc_i)
                            index[lemma]['count'] += 1
        except FileNotFoundError:
            print(f'Файл page_{doc_i}.html не найден')
    return index


# Функция для сохранения индекса в файл
def write_index_to_file(index, index_file_name):
    with open(index_file_name, 'w', encoding='utf-8') as file:
        for key, value in index.items():
            count = value['count']
            array = value['inverted_array']
            file.write(f'{{"word":"{key}", "count":{count},"inverted_array":{array}}}\n')


# Функция для создания индекса
def build_index(index_file_name, html_dir, lemma_file_name):
    lemmas_dir = parse_lemmas_from_file(lemma_file_name)
    index = create_html_index(html_dir, lemmas_dir)
    write_index_to_file(index, index_file_name)


# Функция для выполнения булева поиска
def boolean_search(index, query, lemmatizer):
    AND, OR, NOT = map(CaselessLiteral, ["AND", "OR", "NOT"])
    term = Word(srange("[а-яА-Я]"))

    expr = Forward()
    atom = (NOT + term | term | NOT + Group(Suppress("(") + expr + Suppress(")")) | Group(
        Suppress("(") + expr + Suppress(")")))
    clause = Group(atom + ZeroOrMore(AND + atom | OR + atom))
    expr <<= clause

    def analyze_expression(query, index):
        if isinstance(query, str):
            token = lemmatizer.parse(query.lower())[0].normal_form
            return index.get(token)
        elif query[0] == "NOT":
            not_docs = analyze_expression(query[1], index)
            all_docs = set(range(1, len(index) + 1))
            return list(all_docs - set(not_docs))
        else:
            result = analyze_expression(query[0], index)
            for op, term in zip(query[1::2], query[2::2]):
                term_docs = analyze_expression(term, index)
                if op == "AND":
                    result = list(set(result) & set(term_docs))
                elif op == "OR":
                    result = list(set(result) | set(term_docs))
            return result

    parsed_query = expr.parseString(query)[0]
    return analyze_expression(parsed_query, index)


# Функция для получения индекса из файла
def read_index_from_file(index_file_name):
    index = {}
    with open(index_file_name, 'r', encoding='utf-8') as file:
        for line in file:
            data = json.loads(line)
            word = data['word']
            index[word] = data['inverted_array']
    return index


# Пути к нужным файлам
index_file_name = 'inverted_index.txt'
lemma_file_name = '../homeWork2/output/lemmas.txt'
html_dir = '../homeWork1/temp_gorky_pages'


def main():
    # Создание файла с индексами
    build_index(index_file_name, html_dir, lemma_file_name)

    # Получение индексов
    index = read_index_from_file(index_file_name)
    lemmatizer = MorphAnalyzer()

    # Запуск поиска
    while True:
        try:
            query = input("Введите поисковый запрос: ")
            results = boolean_search(index, query, lemmatizer)
            if not results:
                print("Страницы не найдены")
            else:
                print("Найдены страницы:", results)
        except Exception:
            print("Страницы не найдены")


if __name__ == "__main__":
    main()
