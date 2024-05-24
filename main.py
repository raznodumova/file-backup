import json
import requests
from tqdm import tqdm
import configparser



picture_dict = {}
photo_json = {}
photo_json_list = []


user_id = str(input('Введите id пользователя VK: '))
TOKEN_YA = str(input('Токен Яндекс.Диска: '))
folder_name = str(input('Введите название папки: '))
counter = int(input('Количество фотографий: '))


class VKAPI:

    BASE_URL = 'https://api.vk.ru/method/'

    def __init__(self, token_vk):
        self.token = token_vk

    def get_photos(self):
        params = {
            'access_token': self.token,
            'v': '5.199',
            'user_ids': user_id,
            'album_id': 'profile',
            'extended': '1',
            'count': counter
        }
        response = requests.get(f'{self.BASE_URL}/photos.get', params=params).json()
        photos_items = response['response']['items']
        for item in photos_items:
            max_height = 0
            sizes = item['sizes']
            likes = item['likes']['count']
            date = item['date']
            for size in sizes:
                if size['height'] > max_height:
                    max_height = size['height']
                    if likes not in picture_dict.keys() and max_height == size['height']:
                        picture_dict[f'{likes}_{date}'] = size['url']
                        photo_json['file_name'] = f'{likes}_{date}.jpg'
                        photo_json['size'] = size['type']
                        photo_json_list.append(photo_json)


def create_json():
    with open('vk_image.json', 'w') as file:
        file.write(json.dumps(photo_json_list, ensure_ascii=True, indent=4))


class YDisk:

    BASE_URL = 'https://cloud-api.yandex.net'

    def __init__(self, token):
        self.token = token

    def create_folder(self):
        params = {
            'path': folder_name,
            'overwrite': 'false'
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }
        response = requests.put(f'{self.BASE_URL}/v1/disk/resources/', params=params, headers=headers)

    def upload_photo(self):
        for key, value in tqdm(picture_dict.items()):
            filename = key
            file_path = value
            params = {
                'path': f"{folder_name}/{filename}",
                'url': file_path
            }
            headers = {
                'Accept': 'application/json',
                'Authorization': f'OAuth {self.token}'
            }
            response = requests.post(f'{self.BASE_URL}/v1/disk/resources/upload', headers=headers, params=params)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    token_vk = config['VK']['token']
    vkclient = VKAPI(token_vk)
    vkclient.get_photos()
    create_json()
    yaclient = YDisk(TOKEN_YA)
    yaclient.create_folder()
    yaclient.upload_photo()
