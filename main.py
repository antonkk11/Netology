from config_reader import config
import requests
from datetime import datetime
from collections import Counter
import json

class VK:
    def __init__(self, access_token, user_id, version='5.199'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v':
        self.version}

    def users_info(self):
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params,
        **params})
        return response.json()

    def photos_info(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.id,
                  "album_id": "profile",
                  "extended": "1",
                  "photo_sizes": "1"}
        response = requests.get(url, params={**self.params,
        **params})
        return response.json()

class Yandex_disk:
    def __init__(self, token):
        self.token = token
        self.headers = {'Authorization': f'OAuth {self.token}'}
        self.folder = None

    def new_folder(self, folder_name):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/'
        params = {"path": f'/{folder_name}'}
        requests.put(url, headers=self.headers, params=params)
        self.folder = params['path']

    def upload_photo(self, name, link):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        params = {"path": f'{self.folder}/{name}',
                  'url': link}
        requests.post(url, headers= self.headers, params=params)

def backup(access_token, user_id, ya_token):
    # Получаем информацию с фотографиями у пользователя
    vk = VK(access_token, user_id)
    all_data = vk.photos_info()
    count = 0
    count_all = all_data['response']['count']
    photo_data = {}

    # Создаем словарь с ссылками на максимальный размер фото
    for photo in all_data['response']['items']:
        likes = str(photo['likes']['count'])
        temporary_dict= {}
        for size in photo['sizes']:
            number = photo['sizes'].index(size)
            temporary_dict[number] = size['height']
        max_key = max(temporary_dict, key=temporary_dict.get)
        url_photo = photo['sizes'][max_key]['url']
        size = photo['sizes'][max_key]['type']
        photo_date = datetime.utcfromtimestamp(photo['date']).strftime('%Y-%m-%d')
        photo_data[count] = {'name' : likes, 'date' : photo_date  ,'url' : url_photo, 'size' : size}
        count += 1

    # Считаем, количество фото с одинаковым количеством лайков
    name_list = [photo_data[name]['name'] for name in photo_data.keys()]
    name_counter = Counter(name_list)

    # Меняем название у файлов, добавляя дату, если количество лайков совпадает
    for number in photo_data:
        if name_counter[photo_data[number]['name']] > 1:
            photo_data[number] = {'name': f' {photo_data[number]['name']} ({photo_data[number]['date']}).jpeg',
                                  'date': photo_data[number]['date'],
                                  'url': photo_data[number]['url'],
                                  'size': photo_data[number]['size']}
        else:
            photo_data[number] = {'name': f' {photo_data[number]['name']}.jpeg',
                                      'date': photo_data[number]['date'],
                                      'url': photo_data[number]['url'],
                                      'size': photo_data[number]['size']}

    count = 0
    json_list = []

    # Создаем новую папку на Яндекс.Диск
    ya = Yandex_disk(ya_token)
    ya.new_folder('Фото VK')

    # Записываем данные на Яндекс.Диск
    for number in photo_data.keys():
        link = photo_data[number]['url']
        name = photo_data[number]['name']
        ya.upload_photo(name, link)
        json_item = {"file_name": name, "size": photo_data[number]['size']}
        json_list.append(json_item)
        count += 1
        print(f'Выполнено: {count} из {count_all}. {round((count / count_all), 2) * 100}%')

    # Сохраням данные в .json
    with open('data_photo.json', 'w') as f:
        json.dump(json_list, f)

access_token = config.access_token.get_secret_value()
user_id = config.user_id.get_secret_value()
ydisk_token = config.ydisk_token.get_secret_value()

backup(access_token, user_id, ydisk_token)