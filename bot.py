# -*- coding: utf-8 -*-

import requests
import time
import urllib3
import pickle
import keys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://api.telegram.org/bot" + keys.bot_token + "/"

participants_by_chat = dict()

def save(dict_to_save, file):
    with open(file, 'wb') as handle:
        pickle.dump(dict_to_save, handle)

def read(file):
    with open(file, 'rb') as handle:
        return pickle.loads(handle.read())

def get_last_update_id(updates):
    if len(updates) == 0:
        return 0
    return updates[len(updates) - 1]['update_id']

def get_updates_json(request, offset, timeout):
    params = {'timeout': timeout, 'offset': offset}

    response = requests.get(request + 'getUpdates', data=params, verify=False)
    reponseJson = response.json()
    print(reponseJson)
    return reponseJson['result']

def get_chat_id(update):
    chat_id = update['message']['chat']['id']
    return chat_id

def send_mess(chat, text):
    params = {'chat_id': chat, 'text': text}
    response = requests.post(url + 'sendMessage', data=params)
    return response

def get_user_name(update):
    return update['message']['from']['username']

def get_message_text(update):
    return update['message']['text']

# returns all chat_id in unpdates and fills participants_by_chat dictinary with set of participants
def process_results(results):
    chat_ids = set()
    for result in results:

        if result.get('message') == None:
            continue

        participant = get_user_name(result)
        message = get_message_text(result)
        chat_id = get_chat_id(result)
        chat_ids.add(chat_id)

        participants_set = participants_by_chat.get(chat_id)

        if participants_set == None:
            participants_set = set()

        if '/clear' in message:
            participants_set.clear()
        if message == '+':
            participants_set.add(participant)
        if message == '-':
            participants_set.discard(participant)

        participants_by_chat[chat_id] = participants_set
    return chat_ids

def create_participants_message(chat_id):
    message = "Кто записался:\n"
    for participant in participants_by_chat[chat_id]:
        message += "@" + participant + "\n"
    message += "Всего человек: " + str(len(participants_by_chat[chat_id]))
    return message

def main():
    last_message_for_chat = dict()
    offset = get_last_update_id(get_updates_json(url, 0, 0)) + 1

    while True:
        updates = get_updates_json(url, offset, 100)
        print(updates)
        if len(updates) != 0:
            offset = get_last_update_id(updates) + 1
            for chat_id in process_results(updates):
                new_message = create_participants_message(chat_id=chat_id)
                if new_message != last_message_for_chat.get(chat_id):
                    send_mess(chat_id, new_message)
                    last_message_for_chat[chat_id] = new_message
        save(participants_by_chat, 'participants.txt')
        time.sleep(1)

if __name__ == '__main__':
    main()
