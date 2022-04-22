from __future__ import unicode_literals
import json
from parsivar import *
from hazm import Normalizer as Hazm_Normalizer
import matplotlib.pyplot as plt
import math

punctuations = [".", "،", "»", "«", "؛", ":", "؟", "!", ",", "(", ")", "-", "_", "…", "[", "]"]

stop_words = ["هر", "بر", "تا", "به", "در", "از", "که", "را", "این", "آن", "و", "با", "هم", "برای", "پس"]

docs_content = []

inverted_index = {}  # {"term": {"doc_id": [positions]}}


# reads news from data.json and extract needed data
def read_file():
    global docs_content
    f = open('data.json', encoding='utf8')
    data = json.load(f)
    counter = 0
    for i in data:
        if counter < 12210:
            docs_content.append(data[i]["content"])
            counter += 1
        else:
            break
    f.close()


# separating terms
def tokenize(string):
    _tokenizer = Tokenizer()
    return _tokenizer.tokenize_words(string)


# finding stems of verbs and nouns
def stem(token):
    _stemmer = FindStems()
    return _stemmer.convert_to_stem(token)


def normalize(string):
    _normalizer = Normalizer()
    hazm_normalizer = Hazm_Normalizer()
    hazmed = hazm_normalizer.normalize(string)  # because hazm supports half-space
    tokens = tokenize(_normalizer.normalize(hazmed))
    normal_tokens = []
    for token in tokens:
        temp = stem(token)
        if "&" in temp:
            temp = temp.split("&")[0]  # past and present stems seperated by &
        normal_tokens.append(temp)
    return normal_tokens


def removal(tokens, remove_list):
    for r in remove_list:
        if r in tokens:
            tokens = list(filter(r.__ne__, tokens))  # filter instead of remove, to remove all occurrences of a char
    return tokens


def preprocess(string):
    normal_tokens = normalize(string)
    # before removing stop_words ******************************************
    # preprocessed_terms = removal(normal_tokens, punctuations)

    # after removing stop_words ******************************************
    preprocessed_terms = removal(removal(normal_tokens, stop_words), punctuations)

    return preprocessed_terms


def inverted_index_construction(docs):
    global inverted_index
    for doc_id, doc in enumerate(docs):
        doc_terms = preprocess(doc)
        print(doc_id)
        for position, term in enumerate(doc_terms):
            if term in inverted_index:
                if doc_id in inverted_index[term]:
                    inverted_index[term][doc_id].append(position)
                else:
                    inverted_index[term][doc_id] = [position]
            else:
                inverted_index[term] = {doc_id: [position]}


def term_frequency(term):
    frequency = {}
    if term in inverted_index:
        for doc_id in inverted_index[term]:
            frequency[str(doc_id)] = len(inverted_index[term][doc_id])
    else:
        return "There is no such term in the inverted index."

    frequency["all"] = sum(frequency.values())

    return frequency


def read_inverted_index_from_cache():
    global inverted_index
    f = open('inverted_index.json', encoding='utf8')
    inverted_index = json.load(f)


def zipf():
    frequency = []
    for term in inverted_index:
        frequency.append(term_frequency(term)["all"])
    frequency.sort(reverse=True)
    log10_cf = [math.log10(freq) for freq in frequency]
    log10_rank = [math.log10(i) for i in range(1, len(frequency) + 1)]
    plot_diagram(log10_rank, log10_cf, "After removing stop_words")


def plot_diagram(x, y, additional_title):
    # plotting the line y = -x
    plt.plot([0, max(max(x), max(y))], [max(max(x), max(y)), 0])

    # plotting the points
    plt.plot(x, y)

    plt.xlabel('log10 rank')
    plt.ylabel('log10 cf')

    plt.title(f'Zipf\'s law : {additional_title}')
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    read_inverted_index_from_cache()
    zipf()
