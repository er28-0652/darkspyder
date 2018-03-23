import requests
from slackbot.bot import Bot

def send_captcha(access_token, channel_id, image_name)
    files = {'file': open(image_name, 'rb')}
    param = {'token': access_token, 'channels': channel_id}
    res = requests.post(url="https://slack.com/api/files.upload", params=param, files=files)
    if res.json()['ok']:
        return res.json()['file']

def main():
    bot = Bot()
    bot.run()

if __name__ == "__main__":
    print('start slackbot')
    main()