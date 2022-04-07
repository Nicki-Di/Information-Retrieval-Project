from __future__ import unicode_literals
import json
from parsivar import *

# TODO for 1-2:
# separate inverted index for each doc, then merge and sort them all
# posting size to be stored
# title and url
# user query
# position in posting!

punctuations = [".", "،", "»", "«", "؛", "\"", ":", "؟", "!", ",", "(", ")", "-", "_", "…", "[", "]"]

stop_words = ["هر", "بر", "تا", "به", "در", "از", "که", "را", "این", "آن", "و", "با", "هم", "برای", "پس"]


def read_file_content():
    f = open('../data.json', encoding='utf8')
    data = json.load(f)
    docs_content = []
    for i in data:
        docs_content.append(data[i]["content"])
    f.close()
    return docs_content


def tokenize(doc):
    _tokenizer = Tokenizer()
    return _tokenizer.tokenize_words(doc)


def stem(token):
    _stemmer = FindStems()
    return _stemmer.convert_to_stem(token)


def normalize(doc):
    _normalizer = Normalizer()
    tokens = tokenize(_normalizer.normalize(doc))
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


def preprocess(docs):
    preprocessed_terms = []  # {"a~1^90", "b~1^53", ... "a~3^0"} -> "term~docID^position"
    doc_id = 0
    for doc in docs:
        normal_tokens = normalize(doc)
        doc_terms = removal(removal(normal_tokens, stop_words), punctuations)
        for i, term in enumerate(doc_terms):
            preprocessed_terms.append(term + "~" + str(doc_id))
        #      + "^" + str(i)
        doc_id += 1
    return preprocessed_terms


def inverted_index_construction(preprocessed_terms):
    inverted_index = {}  # {"term": {"doc_id": [positions]}}
    preprocessed_terms.sort()
    for term in preprocessed_terms:
        extraction = term.split("~")
        extracted_term = extraction[0]
        extracted_doc_id = extraction[1]
        if extracted_term in inverted_index:  # position in doc
            if extracted_doc_id in inverted_index[extracted_term]:
                print(extracted_term)
            print(inverted_index[extracted_term][extracted_doc_id])
        else:
            inverted_index[extracted_term] = {extracted_doc_id: [0]}
    return inverted_index


if __name__ == '__main__':
    a = "این یک جمله می‌باشد. این جمله هم ویرگول، نیست!"
    b = "به گزارش ایسنا سمینار شیمی آلی از امروز ۱۱ شهریور ۱۳۹۶ در دانشگاه جمله علم و صنعت ایران آغاز به کار کرد. این " \
        "سمینار تا ۱۳ شهریور ادامه می یابد. "
    x = [a, b]
    # y = inverted_index_construction(read_file_content())
    y = preprocess(x)
    # print(y)
    z = inverted_index_construction(y)
    # print(z)
    print(json.dumps(z, indent=4, ensure_ascii=False))
