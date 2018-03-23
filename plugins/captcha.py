from slackbot.bot import respond_to

@respond_to(r'.+')
def read_captcha_answer(message):
    answer = message.body['text']
    print(answer)
    message.reply('thank you')