from __future__ import unicode_literals
import json
from parsivar import *
from hazm import Normalizer as Hazm_Normalizer
from collections import OrderedDict
import re

punctuations = [".", "،", "»", "«", "؛", ":", "؟", "!", ",", "(", ")", "-", "_", "…", "[", "]"]

stop_words = ["هر", "بر", "تا", "به", "در", "از", "که", "را", "این", "آن", "و", "با", "هم", "برای", "پس"]

docs_title = ["x", "y", "z"]
docs_content = []
docs_url = ["x", "y", "z"]

inverted_index = {}  # {"term": {"doc_id": [positions]}}


# reads news from data.json and extract needed data
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


def process_query(query):
    not_docs = []
    docs_ranks = {}
    phrases_docs_ranks = {}
    ranks = {}
    exclude_terms = []
    clean_phrases = []
    docs_ranks_info = []

    if "!" in query:
        not_terms = preprocess(query.split("!")[1])
        for not_term in not_terms:
            clean_not_term = preprocess(not_term)
            if clean_not_term[0] in inverted_index:
                not_docs.extend(inverted_index[clean_not_term[0]])
            else:
                return "Invalid term in query!"

        not_docs = set(not_docs)
        query = query.split("!")[0]

    if "\"" in query:
        phrases = re.search('"(.*)"', query).group(1).split('"')
        for phrase in phrases:
            if phrase.isspace() or not phrase:
                continue
            clean_phrases.append(' '.join(preprocess(phrase)))

        phrases_docs_ranks = find_phrases_docs(clean_phrases, not_docs)
        if phrases_docs_ranks == "No match!":
            return "No match!"

        for phrases_docs_rank in phrases_docs_ranks:
            if phrases_docs_rank in not_docs:
                del phrases_docs_ranks[phrases_docs_rank]

    preprocessed_query = preprocess(query)
    for clean_phrase in clean_phrases:
        exclude_terms.append(clean_phrase.split())

    exclude_terms = [item for sublist in exclude_terms for item in sublist]
    preprocessed_query = [item for item in preprocessed_query if item not in exclude_terms]
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

        if phrases_docs_ranks:
            for doc_id in docs_ranks:
                if doc_id in phrases_docs_ranks:
                    docs_ranks[doc_id] += phrases_docs_ranks[doc_id]
                    ranks[doc_id] = docs_ranks[doc_id]

    ranks = dict(OrderedDict(sorted(ranks.items())))
    for doc_id in ranks:
        docs_ranks_info.append(f"#{doc_id} -> {docs_info(doc_id)} , rank: {ranks[doc_id]}")
    return docs_ranks_info if ranks else "No match!"


def find_phrases_docs(phrases, not_docs):
    phrases_docs = {}
    phrases_ranks = {}

    for phrase in phrases:
        terms = phrase.split(" ")
        intersection_docs = []
        pairs_count = 0
        temp = -1
        valid_docs = set()
        for i in range(0, len(terms)):
            for j in range(1, len(terms)):
                if terms[i] != terms[j]:
                    intersection_docs.extend(list(set(inverted_index[terms[i]]) & set(inverted_index[terms[j]])))
                    pairs_count += 1
        for intersection_doc in intersection_docs:
            if intersection_docs.count(intersection_doc) == pairs_count and temp != intersection_doc:
                temp = intersection_doc
                if temp not in not_docs:
                    valid_docs.add(intersection_doc)

        for valid_doc in valid_docs:
            if phrase in phrases_docs:
                phrases_docs[phrase].append({valid_doc: []})
            else:
                phrases_docs[phrase] = [{valid_doc: []}]

        if phrases_docs:
            for doc_dict in phrases_docs[phrase]:
                for doc_id in doc_dict:
                    for term in terms:
                        doc_dict[doc_id].append(inverted_index[term][doc_id])
        else:
            return "No match!"
        initial = iterate_positions(phrases_docs[phrase])
        if phrases_ranks:
            for doc_id in initial:
                if doc_id in phrases_ranks:
                    phrases_ranks[doc_id] += initial[doc_id]
                else:
                    phrases_ranks[doc_id] = initial[doc_id]
        else:
            phrases_ranks = initial

    return phrases_ranks


def iterate_positions(phrase_docs):
    phrase_docs_ranks = {}
    for doc_dict in phrase_docs:
        for doc_id in doc_dict:
            for i in range(0, len(doc_dict[doc_id]) - 1):
                for j in range(1, len(doc_dict[doc_id])):
                    doc_dict[doc_id][i] = list(
                        set(list(map(lambda t: t + 1, doc_dict[doc_id][i]))) & set(doc_dict[doc_id][j]))
                    doc_dict[doc_id][j] = doc_dict[doc_id][i]

            if [item for sublist in doc_dict[doc_id] for item in sublist]:
                phrase_docs_ranks[doc_id] = len(set([item for sublist in doc_dict[doc_id] for item in sublist]))

    phrase_docs_ranks = dict(OrderedDict(sorted(phrase_docs_ranks.items())))
    return phrase_docs_ranks


def docs_info(doc_id):
    return f"doc_title: {docs_title[doc_id]} , doc_url: {docs_url[doc_id]}"


def term_frequency(term):
    frequency = {}
    if term in inverted_index:
        for doc_id in inverted_index[term]:
            frequency[str(doc_id)] = len(inverted_index[term][doc_id])
    else:
        return "There is no such term in the inverted index."

    frequency["all"] = sum(frequency.values())

    return frequency


def cache_inverted_index():
    f = open("inverted_index.txt", "w", encoding='utf8')
    f.write(json.dumps(inverted_index))
    f.close()


if __name__ == '__main__':
    # read_file()
    # inverted_index_construction(docs_content)
    # cache_inverted_index()
    # print("\n".join(process_query('"تحریم هسته‌ای" آمریکا ! ایران')))
    a = "این یک جمله آمریکا می‌باشد. این سمینار جمله هم ویرگول، نیست!"
    b = "به گزارش ایسنا سمینار شیمی آلی از امروز ۱۱ شهریور ۱۳۹۶ در دانشگاه جمله علم و سمینار جمله ایران صنعت ایران آغاز به کار کرد. سمینار جمله ایران این " \
        "سمینار تا ویرگول ۱۳ شهریور می یابد. "
    s = "ایران سمینار جمله تحریم هسته‌ای سمینار آمریکا سمینار جمله ایران"

    x = [a, b, s]
    inverted_index_construction(x)
    result = process_query('ایران "سمینار جمله"')
    print(result) if type(result) == str else print("\n".join(result))
