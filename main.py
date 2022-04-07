from __future__ import unicode_literals
import json
from parsivar import *

# TODO for 1-2:
# user query

punctuations = [".", "،", "»", "«", "؛", "\"", ":", "؟", "!", ",", "(", ")", "-", "_", "…", "[", "]"]

stop_words = ["هر", "بر", "تا", "به", "در", "از", "که", "را", "این", "آن", "و", "با", "هم", "برای", "پس"]

docs_title = []
docs_content = []
docs_url = []


def read_file():
    global docs_content
    global docs_title
    global docs_url

    f = open('../data.json', encoding='utf8')
    data = json.load(f)
    for i in data:
        docs_title.append(data[i]["title"])
        docs_content.append(data[i]["content"])
        docs_url.append(data[i]["url"])
    f.close()


def tokenize(string):
    _tokenizer = Tokenizer()
    return _tokenizer.tokenize_words(string)


def stem(token):
    _stemmer = FindStems()
    return _stemmer.convert_to_stem(token)


def normalize(string):
    _normalizer = Normalizer()
    tokens = tokenize(_normalizer.normalize(string))
    normal_tokens = []
    for token in tokens:
        temp = stem(token)
        if "&" in temp:
            temp = temp.split("&")[0]
        normal_tokens.append(temp)
    return normal_tokens


def removal(tokens, remove_list):
    for r in remove_list:
        if r in tokens:
            tokens = list(filter(r.__ne__, tokens))
    return tokens


def preprocess(string):
    normal_tokens = normalize(string)
    preprocessed_terms = removal(removal(normal_tokens, stop_words), punctuations)
    return preprocessed_terms


def inverted_index_construction(docs):
    inverted_index = {}  # {"term": {"doc_id": [positions]}}
    for doc_id, doc in enumerate(docs):
        doc_terms = preprocess(doc)
        for position, term in enumerate(doc_terms):
            if term in inverted_index:
                if doc_id in inverted_index[term]:
                    inverted_index[term][doc_id].append(position)
                else:
                    inverted_index[term][doc_id] = [position]
            else:
                inverted_index[term] = {doc_id: [position]}
    return inverted_index


def process_user_query(query):
    preprocessed_query = preprocess(query)
    print(preprocessed_query)


def docs_info(doc_id):
    return docs_title[doc_id], docs_url[doc_id]


if __name__ == '__main__':
    a = "این یک جمله می‌باشد. این جمله هم ویرگول، نیست!"
    b = "به گزارش ایسنا سمینار شیمی آلی از امروز ۱۱ شهریور ۱۳۹۶ در دانشگاه جمله علم و صنعت ایران آغاز به کار کرد. این " \
        "سمینار تا ۱۳ شهریور ادامه می یابد. "
    x = [a, b]
    # y = inverted_index_construction(docs_content)
    # y = inverted_index_construction(x)
    # print(json.dumps(y, indent=4, ensure_ascii=False))
    process_user_query("این یک جمله می‌باشد.")
