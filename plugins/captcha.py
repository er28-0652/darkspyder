import io
import pickle
from datetime import datetime
from slackbot.bot import respond_to
from .setting import target_markets

clients = {}

def send_captcha_rawdata(message, image_data, image_id):
    channels = message._body['channel']
    channels = ','.join(channels) if isinstance(channels, (tuple, list)) else channels
    data = {
        'initial_comment': 'なにこれ？ #{0}'.format(image_id),
        'channels': channels
    }
    message._client.webapi.files.post(
        'files.upload',
        data=data,
        files={'file': io.BytesIO(image_data)}
    )

@respond_to(r'^働け！')
def start_scraping(message):
    message.send('ダーーーク！スクレイッピングッッッ！！！')

    for target in target_markets:
        market = target['class']
        url = target['url']
        message.send('アクセス中 -> {0}'.format(url))
        client = market(url, target['username'], target['password'])
        client.start()
        cap_token, image_data = client.get_captcha()

        send_captcha_rawdata(message, image_data, cap_token)

        global clients
        clients[cap_token] = client

@respond_to(r'^#(.*) (.*)')
def break_captcha(message, cap_token, answer):
    client = clients[cap_token]
    ok = client.login(cap_token, answer)
    if ok and client.is_login:
        totals = client.parse()
        message.send(''.join(['{0}: {1}\n'.format(category, number) for category, number in totals.items()]))
        message.send('いっぱいちゅき❤️')
    else:
        cap_token, image_data = client.get_captcha()
        send_captcha_rawdata(message, image_data, cap_token)
        clients[cap_token] = client
        
@respond_to(r'^たまには休め')
def take_break(message):
    global clients
    clients = {}