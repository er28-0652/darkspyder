from slackbot.bot import respond_to

def send_captcha(access_token, channel_id, image_name):
    files = {'file': open(image_name, 'rb')}
    param = {'token': access_token, 'channels': channel_id}
    res = requests.post(url="https://slack.com/api/files.upload", params=param, files=files)
    if res.json()['ok']:
        return res.json()['file']


@respond_to(r'^ダークスクレイピング\s+\S.*')
def start_scraping(message):
    message.send('scraping...')
    msg = message.body['text']
    url = text.split(None, 1)[1]
    wsm = WallStMarket(url)
    image_path = wsm.save_captcha_image()
    message.send_webapi()


@respond_to(r'.+')
def read_captcha_answer(message):
    answer = message.body['text']
    print(answer)
    print(message.channel)
    message.reply('thank you')

