from flask import Flask, render_template, request

from homeWork5.search_system import process_query

INDEX_FILE = '..//homeWork1/index.txt'
app = Flask(__name__, template_folder='web_templates', static_url_path='/static')


def read_index():
    links = {}
    with open(INDEX_FILE, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            links[line.split(": ")[0].replace("page_", "")] = line.split(": ")[1].replace("\n", "")
    return links


def get_link_results(search_result, links):
    if search_result is not None and search_result:
        responses = []
        for item in search_result:
            responses.append(links[str(item)])
        return responses
    else:
        return None


@app.route('/', methods=['GET', 'POST'])
def start():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def index():
    links = read_index()
    if request.method == 'POST':
        input_value = request.form['input_value']
        result = process_query(input_value)
        links_result = get_link_results(result, links)
        if links_result:
            return render_template('search_results.html', input_value=input_value, result=links_result[:10])
        else:
            return render_template('search_results.html', input_value=input_value,
                                   error_message="По вашему запросу ничего не найдено")
    return render_template('search_results.html')


if __name__ == '__main__':
    app.run()
