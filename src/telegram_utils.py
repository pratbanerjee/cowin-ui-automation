import requests
import json

base_url = f"https://api.telegram.org/bot"


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(TOKEN):
    url = f'{base_url}{TOKEN}/getUpdates'
    js = get_json_from_url(url)
    if not js['ok']:
        print('Error: Invalid telegram token!')
        exit(0)
    return js


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    if num_updates == 0:
        print('Error: Please send a message to the bot to initialize!')
        exit(0)

    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    msg_timestamp = updates["result"][last_update]["message"]["date"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]

    return text, msg_timestamp, chat_id


def send_message(TOKEN, text, chat_id):
    url = f'{base_url}{TOKEN}/sendMessage?text={text}&chat_id={chat_id}'
    resp = json.loads(get_url(url))
    if not resp['ok']:
        print('Error: Invalid telegram chat_id! Please delete cached.')
        exit(0)


def initialize_bot(TOKEN):

    get_updates(TOKEN)  # ensure token is valid

    # in case the bot doesn't have a recent incoming message, cached will prevent failing
    try:
        f_cached = open('cached', 'rt')
    except FileNotFoundError:
        _, _, chat_id = get_last_chat_id_and_text(get_updates(TOKEN))
        with open('cached', 'wt') as f_cached:
            json.dump({'chat_id': chat_id}, f_cached)
    else:
        chat_id = json.load(f_cached)['chat_id']

    send_message(TOKEN, 'Bot initialized.', chat_id)  # ensure chat_id is valid

    return chat_id
