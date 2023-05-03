from datetime import datetime

import vk_api
import requests

from config import user_token

class VkTools():
    def __init__(self, user_token):
        self.api = vk_api.VkApi(token=user_token)

    def get_profile_info(self, user_id):
        info, = self.api.method('users.get',
                                {'user_id': user_id,
                                 'fields': 'city,bdate,sex,relation,home_town'
                                 }
                                )
        user_info = {'name': info['first_name'] + ' ' + info['last_name'],
                     'id': info['id'],
                     'bdate': info['bdate'] if 'bdate' in info else None,
                     'home_town': info['home_town'],
                     'sex': info['sex'],
                     'city': info['city']['id']
                     }
        return user_info

    def check_city(self, params):
       for i in params:
           if 'city' in i:
               return params['city']
       return False

    def find_city(seelf, city_name):
      url = url = f'https://api.vk.com/method/database.getCities'
      params = {'access_token': user_token,
                      'country_id': 1,
                      'q': f'{city_name}',
                      'need_all': 0,
                      'count': 1000,
                      'v': '5.131'}
      repl = requests.get(url, params=params)
      response = repl.json()
      information_list = response['response']
      list_cities = information_list['items']
      for i in list_cities:
        found_city_name = i.get('title')
        if found_city_name.lower() == city_name.lower():
           found_city_id = i.get('id')
           return int(found_city_id)

    def serch_users(self, params, offset):
        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        curent_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = curent_year - user_year
        age_from = age - 5
        age_to = age + 5
        users = self.api.method('users.search',
                                {'count': 10,
                                 'offset': offset,
                                 'fields': 'bdate, city',
                                 'age_from': age_from,
                                 'age_to': age_to,
                                 'sex': sex,
                                 'city': city,
                                 'status': 6,
                                 'is_closed': False
                                 }
                                )
        try:
            users = users['items']
        except KeyError:
            return []

        res = []
        for user in users:
            if user['is_closed'] == False:
                res.append({'id': user['id'],
                            'name': user['first_name'] + ' ' + user['last_name'],
                            'bdate': user['bdate']
                            }
                           )

        return res

    def get_photos(self, user_id):
        photos = self.api.method('photos.get',
                                 {'user_id': user_id,
                                  'album_id': 'profile',
                                  'extended': 1
                                  }
                                 )
        try:
            photos = photos['items']
        except KeyError:
            return []

        res = []
        for photo in photos:
            res.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        }
                       )

        res.sort(key=lambda x: x['likes'] + x['comments'] * 10, reverse=True)
        return res
