# -*- coding: utf-8 -*-

import sys
import os
import json
import string
import operator
from collections import Counter, OrderedDict

import nltk
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


def tokenize(text):
    punctuations = string.punctuation + '»«„“–…—×→←↓↑↺'
    translatetable = {ord(c): " " for c in punctuations}
    #translatetable[ord("\xad")] = None
    #print(translatetable)
    tokens = nltk.word_tokenize(text.translate(translatetable))
    stop_words = set(stopwords.words('english'))
    tokens = [w.lower() for w in tokens if not w.lower() in stop_words]
    stemmer = PorterStemmer()
    stems = []
    for item in tokens:
        if not item.isdigit():
            stems.append(stemmer.stem(item))
    return stems


class ExplainXkcdCrawlerPipeline(object):
    def process_item(self, item, spider):
        print('Processing item {}: {} ...'.format(str(item['id']),
                                                  item['title']))
        return item


class TidyUpPipeline(object):
    def process_item(self, item, spider):
        item['explanation_html'] = item.get('explanation_html', '').strip()
        item['explanation_text'] = item.get('explanation_text', '').strip()
        item['transcript_html'] = item.get('transcript_html', '').strip()
        item['transcript_text'] = item.get('transcript_text', '').strip()
        item['trivia_html'] = item.get('trivia_html', '').strip()
        item['trivia_text'] = item.get('trivia_text', '').strip()
        item['img_url'] = 'https://www.explainxkcd.com' + item.get('img_url')
        return item


class TokenizePipeline(object):
    def process_item(self, item, spider):
        item['explanation_tokens'] = self.tokenize_count_order(
            item.get('explanation_text', ''))
        item['transcript_tokens'] = self.tokenize_count_order(
            item.get('transcript_text', ''))
        item['trivia_tokens'] = self.tokenize_count_order(
            item.get('trivia_text', ''))
        return item

    def tokenize_count_order(self, text):
        if not text:
            return None
        counted = Counter(tokenize(text))
        if len(counted) < 1:
            return None
        return OrderedDict(
            sorted(counted.items(), key=lambda kv: kv[1], reverse=True))


class CreateCorpusPipeline(object):
    corpus = []
    ids = []
    minid = sys.maxsize
    maxid = 0
    docsim = None

    def __init__(self, json_files_dir="/tmp"):
        self.json_files_dir = json_files_dir

    def process_item(self, item, spider):
        id = int(item.get("id", "0"))
        text = item.get("explanation_text", "") + " " + item.get(
            "transcript_text", "") + " " + item.get(
                "title", "") + " " + item.get("titletext", "")
        self.corpus.append({"id": id, "text": text})
        self.ids.append(id)
        self.minid = min(self.minid, id)
        self.maxid = max(self.maxid, id)
        return item

    def close_spider(self, spider):
        print("Calculating item similarity ...")
        self.corpus = sorted(self.corpus, key=lambda k: k["id"])

        tfidf_vect = TfidfVectorizer(tokenizer=tokenize, stop_words=None)
        tfidf = tfidf_vect.fit_transform([x["text"] for x in self.corpus])
        self.docsim = linear_kernel(tfidf, tfidf).tolist()
        self.docsim = {
            self.ids[i]:
            {self.ids[j]: self.docsim[i][j]
             for j in range(len(self.ids))}
            for i in range(len(self.ids))
        }

        for id in self.ids:
            print(".", end="")
            data = {}
            with open(os.path.join(self.json_files_dir,
                                   str(id) + '.json')) as file:
                data = json.load(file)
            simitems = self.docsim[id]
            del simitems[id]
            # data["similar"] = OrderedDict(
            #     sorted(simitems.items(), key=lambda kv: kv[1], reverse=True))
            simitems = sorted(simitems.items(),
                              key=lambda kv: kv[1],
                              reverse=True)
            data["similar"] = simitems
            self.write_file(str(id) + '.json', data)

        info = {}
        info["ids"] = self.ids
        info["maxid"] = self.maxid
        info["minid"] = self.minid
        info["size"] = len(self.ids)
        self.write_file("info.json", info)

        print("\nDone.")

    def write_file(self, filename, content):
        with open(os.path.join(self.json_files_dir, filename), 'w') as file:
            file.write(json.dumps(content, indent=4, default=str))

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings.get('JSON_FILES_DIR'))


class WriteSeperateJsonFilePipeline(object):
    def __init__(self, json_files_dir="/tmp"):
        self.json_files_dir = json_files_dir
        if not os.path.exists(self.json_files_dir):
            try:
                os.makedirs(self.json_files_dir)
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

    def process_item(self, item, spider):
        with open(os.path.join(self.json_files_dir,
                               item.get('id') + '.json'), 'w') as file:
            file.write(json.dumps(dict(item), indent=4, default=str))
        return item

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings.get('JSON_FILES_DIR'))
