import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

content_types = {"pdf", "jpg", "zip", "exe"} # Determine file types to skip unwanted files (e.g. .jpg, .zip, .exe)

from urllib.parse import urlparse, urljoin
import re

TIMEOUT = 2
TENKB = 10*1024
ONEHUNDREDKB = 100*1024

class PyCrawler(object):
    def __init__(self, starting_url):
        self.starting_url = starting_url
        self.visited = set()

    def get_content_type(self, link):
        # Can issue ‘HEAD’ HTTP commands to get Content-Type (MIME) headers, but may cause overhead of extra Internet requests
        headers = {'user-agent': "Some students from UAM"}
        try:
            h = requests.head(link, verify=False, headers=headers)
            header = h.headers
            content_type = header.get('content-type')
            return str(content_type).lower()
        except Exception as e: # Do not stop if a download fails
            print(e)
            return False

    def get_html(self, url): # Fetcher must be robust
        headers = {
            "Range": f"""bytes={str(TENKB)}-{str(ONEHUNDREDKB)}""", # Avoid reading too much data: typically get only the first 10-100 KB per page
            'user-agent': "Some students from UAM"
            }
        try:
            html = requests.get(url, verify=False, timeout=TIMEOUT, headers=headers) # Use a timeout mechanism (10 sec?)
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
            return ""
        return html.content.decode('latin-1')

    def get_links(self, url):
        html = self.get_html(url)

        # extract base URL
        o = urlparse(url)
        if o.scheme:
            base = f"{o.scheme}://{o.netloc}"
        else:
            base = f"""http:{o.geturl()}"""

        links = re.findall('''<a\\s+(?:[^>]*?\s+)?href="([^"]*)"''', html)
        for i, link in enumerate(links):
            if not urlparse(link).netloc:
                if link:
                    if link[0] != "/":
                        link_with_base = base + "/" + link
                    else:
                        link_with_base = base + link
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

            # print("Initial URL: "+url)
            link = self.url_canonization(link)
            # print("Before canonization: "+url)

            # Keep a lookup (hash) table of visited pages
            if link in self.visited: # Avoid fetching the same page twice
                continue
            self.visited.add(link)
            content_type = self.get_content_type(link)
            if content_type in content_types:
                continue
            info = self.extract_info(link)

            print(f"""
                Link: {link}
                Description: {info.get('description')}
                Keywords: {info.get('keywords')}
            """)

            self.crawl(link)

    def start(self):
        self.crawl(self.starting_url)

if __name__ == "__main__":
    crawler = PyCrawler("https://google.com")
    crawler.start()


# bibliografy

# https://books.google.es/books?id=2gd5_ttNvEoC&pg=PA116&lpg=PA116&dq=canonical+form+transformation+crawler&source=bl&ots=3WL4TmvqOa&sig=ACfU3U0F1_tY10YhdyWOEBmcxG31bUxh1Q&hl=pt-BR&sa=X&ved=2ahUKEwil_ajhy6vnAhXPesAKHZbgBL4Q6AEwC3oECAcQAQ#v=onepage&q=canonical%20form%20transformation%20crawler&f=false
# https://books.google.es/books?id=jnCi0Cq1YVkC&pg=PA319&lpg=PA319&dq=crawler+canonical+form&source=bl&ots=SmcnnrQkke&sig=ACfU3U2Rqilml5Wy1GcvSGYXZCSWMqWwuQ&hl=pt-BR&sa=X&ved=2ahUKEwiZxuObyqvnAhUiVBUIHXrCAWsQ6AEwC3oECAkQAQ#v=onepage&q=crawler%20canonical%20form&f=false
# pg 320 canonization
# https://dev.to/fprime/how-to-create-a-web-crawler-from-scratch-in-python-2p46

# https://moz.com/learn/seo/canonicalization
# https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html


# https://posgrado.uam.es/pluginfile.php/1312943/mod_label/intro/wm1920-unit2.1-slides-WebCrawling.pdf

# libs

# https://docs.python.org/3/library/urllib.parse.html

# SVG
# https://github.com/fredwu/crawler/tree/master/lib/crawler/fetcher