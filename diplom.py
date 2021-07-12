import requests
import json
import time
from tqdm import tqdm

iden = None
count = 5
ya_token = ' '
token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'

class VkUser:
    url = 'http://api.vk.com/method/'
    name_list = []
    json_data = []
    my_list = []

    def __init__(self, token, ya_token, version):
        self.token = token
        self.ya_token = ya_token
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}
        self.owner_id = requests.get(self.url + 'users.get', self.params).json()['response'][0]['id']

    def folder(self):
        res = requests.put('https://cloud-api.yandex.net/v1/disk/resources?', params={'path': 'vk_photos'},
                           headers={'Authorization': f'OAuth {self.ya_token}'})
        return 201

    def upload(self, name):
        response = requests.get('https://cloud-api.yandex.net/v1/disk/resources/upload?',
                                params={'path': f'vk_photos/{name}'},
                                headers={'Authorization': f'OAuth {self.ya_token}'})
        href = response.json()['href']

        with open(f'{name}.jpg', 'rb') as f:
            requests.put(href, files={'file': f})
        return 201

    def get_upload_photos(self, iden):
        if iden is None:
            iden = self.owner_id
        photos_params = {'owner_id': iden, 'album_id': 'profile', 'rev': '1',
                         'extended': '1', 'count': count, 'photo_sizes': '1'}
        params = {**self.params, **photos_params}

        res = requests.get(self.url + 'photos.get', params).json()['response']['items']
        i = 0
        for items in res:
            if items['likes']['count'] in self.name_list:
                name = str(items['likes']['count']) + '_' + str(items['date'])
            else:
                name = items['likes']['count']
            r = requests.get(items['sizes'][-1]['url'])
            s = items['sizes'][-1]['type']
            inf = {'file_name': f'{name}.jpg', 'size': s}
            self.json_data.append(inf)
            with open(f'{name}.jpg', 'wb') as f:
                f.write(r.content)
            self.name_list.append(name)
            self.upload(name)
            time.sleep(0.33)
            i += 1
            self.my_list.append(i)

        with open(f'json_file_{iden}.json', "w") as f:
            json.dump(self.json_data, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    vk_client = VkUser(token, ya_token, '5.131')
    vk_client.folder()
    vk_client.get_upload_photos(iden)

    for i in tqdm(vk_client.my_list):
        time.sleep(1)
