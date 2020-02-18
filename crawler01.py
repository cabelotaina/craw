import requests    
import re    
from urllib.parse import urlparse 
import time
import calendar

   

class PyCrawler(object): 
    
    def __init__(self, starting_url):    
        self.starting_url = starting_url    
        self.visited = set()
        ts = calendar.timegm(time.gmtime())
        self.out = open("link"+str(ts)+".txt" ,"w")  

    def get_html(self, url):    
        try:    
            html = requests.get(url)    
        except Exception as e:    
            print(e)    
            return ""    
        return html.content.decode('latin-1')    

    def get_links(self, url):    
        html = self.get_html(url)    
        parsed = urlparse(url)    
        base = f"{parsed.scheme}://{parsed.netloc}"    
        links = re.findall('''<a\s+(?:[^>]*?\s+)?href="([^"]*)"''', html)    
        for i, link in enumerate(links):    
            if not urlparse(link).netloc:    
                link_with_base = base + link    
                links[i] = link_with_base       

        return set(filter(lambda x: 'mailto' not in x, links))    

    def extract_info(self, url):                                
        html = self.get_html(url)                               
        return None                  

    def crawl(self, url):                   
        
        for link in self.get_links(url):    
            if link in self.visited:        
                continue                    
            print(link)
            
            self.out.write(link+"\n")          
            self.visited.add(link)            
            info = self.extract_info(link)    
            self.crawl(link)                  

    def start(self):                     
        self.crawl(self.starting_url)  
        
          

if __name__ == "__main__":                           
    crawler = PyCrawler("https://www.google.com/search?q=learning+analytics&rlz=1C1CHBF_esES880ES880&oq=learn&aqs=chrome.1.69i57j35i39j0l6.2092j0j8&sourceid=chrome&ie=UTF-8")        
    crawler.start()