# -*- coding: utf-8 -*-

import sys
import http.server
import socketserver
import os
import nltk
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

PORT = 8080
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), 'public')


def crawl(start_id=None):
    nltk.download('punkt')
    nltk.download('stopwords')

    print("Let's go ...")
    settings = get_project_settings()
    settings['JSON_FILES_DIR'] = PUBLIC_DIR
    if start_id:
        print("Using start id: " + str(start_id))
        settings['START_ID'] = start_id
    process = CrawlerProcess(settings)
    process.crawl('explainxkcd')
    process.start()


def serv():
    os.chdir(PUBLIC_DIR)
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), Handler)
    print("Serving at port ", PORT, " ...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ['crawl', 'serv']:
        print("Usage: {} [crawl <startid = 1> | serv]".format(sys.argv[0]))
        exit(1)

    if (sys.argv[1] == 'crawl'):
        if len(sys.argv) >= 3:
            crawl(int(sys.argv[2]))
        else:
            crawl()
        exit(0)

    if (sys.argv[1] == 'serv'):
        serv()
        exit(0)


if __name__ == "__main__":
    main()
