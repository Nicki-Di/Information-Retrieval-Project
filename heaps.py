from __future__ import unicode_literals
import json

import numpy as np
from parsivar import *
from hazm import Normalizer as Hazm_Normalizer
import matplotlib.pyplot as plt
import math

punctuations = [".", "،", "»", "«", "؛", ":", "؟", "!", ",", "(", ")", "-", "_", "…", "[", "]"]

stop_words = ["هر", "بر", "تا", "به", "در", "از", "که", "را", "این", "آن", "و", "با", "هم", "برای", "پس"]

docs_content = []

inverted_index = {}  # {"term": {"doc_id": [positions]}}


# reads news from data.json and extract needed data
def read_file(collection_size):
    global docs_content
    f = open('data.json', encoding='utf8')
    data = json.load(f)
    counter = 0
    for i in data:
        if counter < collection_size:
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
    # before stemming ******************************************
    # normal_tokens = tokens

    # after stemming *******************************************
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


def heaps():
    M = len(inverted_index)
    frequency = []
    for term in inverted_index:
        frequency.append(term_frequency(term)["all"])
    T = sum(frequency)

    log10_M = math.log10(M)
    log10_T = math.log10(T)
    return [log10_T, log10_M]


def plot_diagram(x, y, additional_title):
    # plotting the points
    plt.plot(x, y)

    # plotting the heaps' law line
    [b, log10_k] = np.polyfit(x, y, 1)
    bx = [b * xi for xi in x]
    plt.plot(x, bx + log10_k)

    plt.xlabel('log10 T')
    plt.ylabel('log10 M')

    plt.title(f'Heaps\' law : {additional_title}')
    # plt.axis([5, 8, 3, 6])
    plt.grid(True)
    plt.show()
    return [b, log10_k]


def actual(b, log10_k):
    read_inverted_index_from_cache()
    print(f"All tokens: {pow(10, heaps()[0])}")
    print(f"Predicted Vocabulary size: {pow(10, ((b * heaps()[0]) + log10_k))}")
    print(f"k = {pow(10, log10_k)}")
    print(f"b = {b}")
    print(f"Vocabulary size: {pow(10, heaps()[1])}")


if __name__ == '__main__':
    log10_T = []
    log10_M = []
    for i in range(500, 2001, 500):
        read_file(i)
        inverted_index_construction(docs_content)
        log10_T.append(heaps()[0])
        log10_M.append(heaps()[1])
        docs_content = []
        inverted_index = {}
    [b, log10_k] = plot_diagram(log10_T, log10_M, "After stemming")
    actual(b, log10_k)
