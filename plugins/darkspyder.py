import base64
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

class TorClient:
    def __init__(self, host='127.0.0.1', port=9050):
        self.session = requests.session()
        self.session.proxies = {
            'http':  'socks5h://{0}:{1}'.format(host, port),
            'https': 'socks5h://{0}:{1}'.format(host, port)
        }
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0'}
    
    def _request(self, method, url, *args, **kwargs):
        res = self.session.request(method, url, headers=self.headers, *args, **kwargs)
        res.raise_for_status()
        return res
    
    def get(self, url, *args, **kwargs):
        return self._request('GET', url, *args, **kwargs)
    
    def post(self, url, *args, **kwargs):
        return self._request('POST', url, *args, **kwargs)


class DarkSpyder:
    def __init__(self, url):
        self.url = url
        self.client = TorClient()
    
    def get_captcha(self):
        raise NotImplementedError
    
    def login(self, username, password):
        raise NotImplementedError


class WallStMarket(DarkSpyder):
    def __init__(self, url, username, password):
        super().__init__(url)
        self.current_page = ""
        self.username = username
        self.password = password
        self.cap_data_ptn = re.compile(r'<img class="captcha_image" id="[^"]+" src="data:image/jpeg;base64,([^"]+)"')
        self.cap_token_ptn = re.compile(r'<input type="hidden" id="form__token" name="form\[_token\]" value="([^"]+)" />')
        self.is_pass_security = False
        self.token = ''

    def start(self):
        self.current_page = self.client.get(self.url+'/index').text

    def get_captcha(self):
        m_data = self.cap_data_ptn.search(self.current_page)
        m_token = self.cap_token_ptn.search(self.current_page)

        if m_data and m_token:
            cap_b64= m_data.groups()[0]
            cap_image_data = base64.b64decode(cap_b64)
            cap_token = m_token.groups()[0]
            return cap_token, cap_image_data
    
    def _pass_security_check(self, cap_token, cap_word):
        payload = {'form[_token]': cap_token, 'form[captcha]': cap_word}
        html = self.client.post(self.url+'/index', data=payload).text
        self.current_page = html

        if self._is_login_page:
            self.is_pass_security = True
            return True
        return False
        
    def login(self, cap_token, cap_word):
        if self.is_pass_security is False:
            return self._pass_security_check(cap_token, cap_word)

        payload = {
            'form[_token]': cap_token,
            'form[username]': self.username,
            'form[password]': self.password,
            'form[captcha]': cap_word,
            'form[sessionLength]': '1200',
            'form[language]': 'en',
            'form[pictureQuality]': '1'
        }
        html = self.client.post(self.url+'/login', data=payload).text
        self.current_page = html
        if self.is_login:
            self.token = cap_token
            return True
        return False

    def _read_page(self, category, page):
        payload = {
            'form[_token]': self.token,
            'form[catT]': category,
            'form[catM]':'0',
            'form[catB]':'0',
            'form[searchTerm]':'',
            'menuCatT': category,
            'form[limit]':'90',
            'form[rating]':'0',
            'form[vendorLevel]':'1',
            'form[vendoractivity]':'0',
            'form[quantity]':'0',
            'form[maxpricepunit]':'0',
            'form[shipsfrom]':'0',
            'form[shipsto]':'0',
            'form[sort]':'pop_week_desc',
            'form[page': page
        }
        return self.client.post(self.url+'/index', data=payload).text

    @staticmethod
    def _read_table(page):
        df = pd.read_html(page)[1]
        df['Level'] = df['Vendor'].apply(lambda vendor: vendor.split()[-1])
        df['Vendor'] = df['Vendor'].apply(lambda vendor: vendor.split()[0])
        df['Price'] = df['Price'].apply(lambda price: price.split()[-1].split('/')[0])
        return df.drop('#', axis=1)

    def parse(self):
        soup = BeautifulSoup(self.current_page, 'lxml')
        categories = soup.find_all('button', {'name':'menuCatT'})

        for cat in categories:
            category_id = cat.get('value')
            texts = cat.get_text().split()
            category = ' '.join(texts[:-1])
            # currently Software & Malware is only supported
            if category == 'Software & Malware':
                number = texts[-1]
                result = pd.DataFrame()
                # read each page
                for page in range(1, int(int(number)/90)+2):
                    page_html = self._read_page(category_id, str(page))
                    pruduct_table = self._read_table(page_html)
                    result = result.append(pruduct_table, ignore_index=True)
                return result

    @property
    def is_login(self):
        soup = BeautifulSoup(self.current_page, 'lxml')
        nav = soup.select('span.nav-link')
        return len(nav) != 0
    
    @property
    def _is_login_page(self):
        login_title = '<h3 class="wms_captcha_field wsm_pbc_headmod">Log In</h3>'
        return login_title in self.current_page
