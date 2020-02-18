import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from urllib.parse import urlparse, urljoin
import datetime
import re
import time
import numpy as np

class PyCrawler(object):
    def __init__(self, starting_url = "https://google.com", topical = True, silence_mode = False, limit = 500, wait = False):
        self.limit = limit
        self.topical = topical
        self.starting_url = starting_url
        self.visited = set()
        self.links = open("links.txt", "w")
        self.silence_mode = silence_mode
        self.content_types = {"pdf", "jpg", "zip", "exe"} # Determine file types to skip unwanted files (e.g. .jpg, .zip, .exe)
        self.TENKB = 10*1024
        self.ONEHUNDREDKB = 100*1024
        self.loc_normal = 10
        self.wait = wait
        self.index = 0

    def get_content_type(self, link):
        # Can issue ‘HEAD’ HTTP commands to get Content-Type (MIME) headers, but may cause overhead of extra Internet requests
        headers = {'user-agent': "Some students from UAM", 'Accept-Encoding': 'gzip'}
        try:
            h = requests.head(link, verify=False, headers=headers)
            header = h.headers
            content_type = header.get('content-type')
            return str(content_type).lower()
        except Exception as e: # Do not stop if a download fails
            print(e)
            return False

    def get_next_wait(self):
        return np.abs(np.random.normal(size = 1, loc=self.loc_normal*3))[0]

    def get_next_timeout(self):
        return np.abs(np.random.normal(size = 1, loc=self.loc_normal))[0]

    def get_base(self, url):
        o = urlparse(url)
        base = ""
        if o.scheme:
            base = f"{o.scheme}://{o.netloc}"
        else:
            base = f"""http:{o.geturl()}"""

        return base

    def get_html(self, url): # Fetcher must be robust
        headers = {
                "Range": f"""bytes={str(self.TENKB)}-{str(self.ONEHUNDREDKB)}""", # Avoid reading too much data: typically get only the first 10-100 KB per page
                'user-agent': "Some students from UAM",
                'Accept-Encoding': 'gzip'
            }
        try:
            html = requests.get(url, verify=False, timeout=self.get_next_timeout(), headers=headers) # Use a timeout mechanism (10 sec?)
            # watch URL
            # print(f"""
            #     URL: {html.url}
            #     Size; {len(html.content)}
            #     Time: {html.elapsed.total_seconds()}
            #     History: {(
            #                 str([(l.status_code, l.url) for l in html.history])
            #             )}
            #     Headers: {str(html.headers.items())}
            #     Cookies: {str(html.cookies.items())}
            # """)
        except Exception as e: # Do not stop if a download fails
            print(e)
            # try the same web site with more time
            return ""
        return html.content.decode('latin-1')

    def get_links(self, url):
        html = self.get_html(url)

        # extract base URL

        base = self.get_base(url)

        links = re.findall('''<a\s+(?:[^>]*?\s+)?href="([^"]*)"''', html)
        for i, link in enumerate(links):
            if not urlparse(link).netloc:
                if link:
                    if link[0] == "/":
                        link_with_base = base + link
                    else:
                        link_with_base = base + "/" + link
                else:
                    link_with_base = base
                links[i] = link_with_base

        return set(filter(lambda x: 'mailto' not in x, links))

    def extract_info(self, url):
        html = self.get_html(url)
        meta = re.findall("<meta .*?name=[\"'](.*?)['\"].*?content=[\"'](.*?)['\"].*?>", html)
        return dict(meta)

    def url_canonization(self, url):
        # DOING: URLcanonization

        """ All of these URLs
        http://www.cnn.com/TECH
        http://WWW.CNN.COM/TECH/
        http://www.cnn.com:80/TECH/
        http://www.cnn.com/bogus/../TECH/
        are really equivalent to the following canonical form
        http://www.cnn.com/TECH/
        A crawler must define a set of transformation rules """

        o = urlparse(url)

        # resolve path of current or parent directory
        o = urlparse(urljoin(o.geturl(), o.path))

        # remove dafault number
        if o.port == 80:
            o._replace(netloc=o.netloc.replace(str(":"+str(o.port)), ""))

        # remove fragment
        o._replace(fragment="")

        # authority/netloc to lower
        # http://example.com/ == http://example.com
        netloc = o.netloc.lower()
        if netloc[len(netloc)-1] == "/":
            o._replace(netloc=o.netloc.lower())
        else:
            o._replace(netloc=o.netloc.lower()+"/")

        # http://example.com/data == http://example.com/data/
        path = o.path.lower()
        if path:
            if path[len(path)-1] == "/":
                o._replace(path=o.path.lower())
            else:
                o._replace(path=o.path.lower()+"/")

        # scheme to lower
        if o.scheme:
            o._replace(scheme=o.scheme.lower())
            url = o.geturl()
        else:
            url = f"""http:{o.geturl()}"""

        return url

    def crawl(self, url):
        for link in self.get_links(url):

            base = self.get_base(url)

            self.index += 1

            if (base != self.starting_url and self.topical):
                continue
                self.index -= 1

            if self.index == self.limit:
                break

            if (self.wait):
                time.sleep(self.get_next_wait())

            # print("Initial URL: "+url)
            link = self.url_canonization(link)
            # print("Before canonization: "+url)

            # Keep a lookup (hash) table of visited pages
            if link in self.visited: # Avoid fetching the same page twice
                continue
                self.index -= 1
            content_type = self.get_content_type(link)
            if content_type in self.content_types:
                continue
                self.index -= 1
            # TODO: save HTML
            info = self.extract_info(link+"\n")

            self.links.write(link+"\n")
            self.visited.add(link)
            if not self.silence_mode:
                print(f"""
                    Link: {link}
                    Description: {info.get('description')}
                    Keywords: {info.get('keywords')}
                """)

            self.crawl(link)

    def start(self):
        self.crawl(self.starting_url)

if __name__ == "__main__":
    crawler = PyCrawler("https://www.google.com", True, False, 500, False)
    crawler.start()
