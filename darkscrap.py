import base64
import io
from datetime import datetime
from urllib.parse import urlparse

from PIL import Image
from selenium import webdriver


class TorBrowser(webdriver.Firefox):
    def __init__(self, proxy='127.0.0.1', port=9050):
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference( "places.history.enabled", False )
        self.profile.set_preference( "privacy.clearOnShutdown.offlineApps", True )
        self.profile.set_preference( "privacy.clearOnShutdown.passwords", True )
        self.profile.set_preference( "privacy.clearOnShutdown.siteSettings", True )
        self.profile.set_preference( "privacy.sanitize.sanitizeOnShutdown", True )
        self.profile.set_preference( "signon.rememberSignons", False )
        self.profile.set_preference( "network.cookie.lifetimePolicy", 2 )
        self.profile.set_preference( "network.dns.disablePrefetch", True )
        self.profile.set_preference( "network.http.sendRefererHeader", 0 )

        self.profile.set_preference( "network.proxy.type", 1 )
        self.profile.set_preference( "network.proxy.socks_version", 5 )
        self.profile.set_preference( "network.proxy.socks", proxy )
        self.profile.set_preference( "network.proxy.socks_port", port)
        self.profile.set_preference( "network.proxy.socks_remote_dns", True )
        
        super().__init__(firefox_profile=self.profile)

    def __enter__(self. url):
        return self.driver().get(url)

    def __exit__(self, exc_type, value, traceback):
        self.quit()


class WallStMarket(TorBrowser):
    def __init__(self):
        super().__init__()
    
    def save_captcha_image(self):
        # read base64 encoded image data
        img_tag = self.find_element_by_tag_name("img")
        img_src = img_tag.get_attribute('src')
        img_data = base64.b64decode(img_src.split(',')[1])

        # read by PIL::Image
        image = Image.open(io.BytesIO(img_data))

        # save image data to file
        # filename rule is 'DOMAIN_NAME+CURRENT_TIME+.jpg' 
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        image_name = ''.join([urlparse(self.url).netloc, now, '.jpg'])
        image.save(image_name)
        return image_name
    
    def pass_security_check(self):
        image_path = save_captcha_image()
        # TODO send capctcha and read captcha word
        captcha_input = self.find_element_by_css_selector('#form_captcha')
        captcha_input(word)
        enter = self.find_element_by_css_selector('button.btn:nth-child(3)')
        enter.click()


def main():
    with TorBrowser() as tb:
        tb.get(sys.argv[1])
        tb.pass_security_check()

if __name__ == '__main__':
    main()