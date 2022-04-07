from __future__ import unicode_literals
import json
from parsivar import *
from hazm import Normalizer as Hazm_Normalizer
from collections import OrderedDict
import re

# TODO for 1-2:
# user query: only "" phrase left

punctuations = [".", "،", "»", "«", "؛", ":", "؟", "!", ",", "(", ")", "-", "_", "…", "[", "]"]

stop_words = ["هر", "بر", "تا", "به", "در", "از", "که", "را", "این", "آن", "و", "با", "هم", "برای", "پس"]

docs_title = []
docs_content = []
docs_url = []

inverted_index = {}  # {"term": {"doc_id": [positions]}}


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
    hazm_normalizer = Hazm_Normalizer()
    hazmed = hazm_normalizer.normalize(string)
    tokens = tokenize(_normalizer.normalize(hazmed))
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
    global inverted_index
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


def process_query(query):
    not_docs = []
    if "!" in query:
        not_terms = preprocess(query.split("!")[1])
        for not_term in not_terms:
            not_docs.extend(inverted_index[not_term])
        not_docs = set(not_docs)

    if "\"" in query:
        find_phrases(query)

    docs_ranks = {}
    preprocessed_query = preprocess(query)
    for term in preprocessed_query:
        if term in inverted_index:
            for doc_id in inverted_index[term]:
                if doc_id not in not_docs:
                    if doc_id not in docs_ranks:
                        docs_ranks[doc_id] = len(inverted_index[term][doc_id])
                    else:
                        docs_ranks[doc_id] = docs_ranks[doc_id] + len(inverted_index[term][doc_id])
        else:
            return "Invalid term in query!"
    docs_ranks = dict(OrderedDict(sorted(docs_ranks.items())))
    return docs_ranks


def find_phrases(query):
    phrase_docs = {}
    phrases = re.search('"(.*)"', query).group(1).split('"')
    for phrase in phrases:
        if phrase.isspace() or not phrase:
            continue
        terms = phrase.split(" ")
        intersection_docs = []
        pairs = 0
        for i in range(0, len(terms)):
            for j in range(1, len(terms)):
                if terms[i] != terms[j]:
                    intersection_docs.extend(list(set(inverted_index[terms[i]]) & set(inverted_index[terms[j]])))
                    pairs += 1
        temp = -1
        for doc in intersection_docs:
            if intersection_docs.count(doc) == pairs and temp != doc:
                temp = doc
                print(phrase)
                print(inverted_index[terms[0]][doc])
                if phrase in phrase_docs:
                    for term in terms:
                        if phrase_docs[phrase][term] in phrase_docs[phrase]:
                            phrase_docs[phrase][term].update({doc: inverted_index[term][doc]})

                else:
                    for term in terms:
                        phrase_docs[phrase] = {term: {doc: inverted_index[term][doc]}}
    print(phrase_docs)


def docs_info(doc_id):
    return docs_title[doc_id], docs_url[doc_id]


def term_frequency(term):
    frequency = {}
    if term in inverted_index:
        for doc_id in inverted_index[term]:
            frequency[str(doc_id)] = len(inverted_index[term][doc_id])
    else:
        return "There is no such term in the inverted index."

    frequency["all"] = sum(frequency.values())

    return frequency


if __name__ == '__main__':
    a = "این یک جمله می‌باشد. این سمینار جمله هم ویرگول، نیست!"
    b = "به گزارش ایسنا سمینار شیمی آلی از امروز ۱۱ شهریور ۱۳۹۶ در دانشگاه جمله علم و صنعت ایران آغاز به کار کرد. این " \
        "سمینار تا ۱۳ شهریور ادامه می یابد. "
    s = "ایران تحریم هسته‌ای سمینار آمریکا سمینار جمله ایران"

    x = [a, b, s]
    inverted_index_construction(x)
    # print(json.dumps(inverted_index, indent=4, ensure_ascii=False))
    find_phrases('ایران "تحریم هسته‌ای" "سمینار جمله ایران" ! ویرگول')
