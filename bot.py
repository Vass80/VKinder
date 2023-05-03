import vk_api
import datetime

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import comm_token, user_token
from core import VkTools
from database import *

class BotInterface():

    def __init__(self, comm_token, user_token):
        self.interface = vk_api.VkApi(token=comm_token)
        self.api = VkTools(user_token)
        self.params = None
        self.longpoll = VkLongPoll(self.interface)

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )

    def event_handler(self):
        offset = 0
        users = []
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                if self.params == None:
                    self.params = self.api.get_profile_info(event.user_id)
                    if self.api.check_city(self.params) == None:
                        self.message_send(event.user_id, f'Не хватает данных. Укажите ваш город:')
                        for event in self.longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                command_city = event.text.lower()
                                city = self.api.find_city(command_city)
                                if city == None:
                                   self.message_send(event.user_id, f'Введите существующий город')
                                else:
                                    self.params['city'] = city
                                    self.params['home_town'] = command_city
                                    break
                    if self.params['bdate'] == '':
                        self.message_send(event.user_id, f'Не хватает данных. Укажите ваш возраст:')
                        for event in self.longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                command_age = event.text.lower()
                                if int(command_age) <= 18 or int(command_age) >= 100:
                                   self.message_send(event.user_id, f'Введите реальный возраст')
                                else:
                                    self.params['bdate'] = '01.01.' + str(int(datetime.date.today().year) - int(command_age))
                                    break

                if command == 'привет':
                   self.message_send(event.user_id, f'здравствуй {self.params["name"]}')
                   self.message_send(event.user_id, f'Введите команду: Привет \ Начать \ Продолжить')
                elif command == 'начать':
                    drop_db()
                    offset = 0
                    users = self.api.serch_users(self.params, offset)
                    user = users.pop()
                    add_to_db(self.params['id'],user['id'])
                    photos_user = self.api.get_photos(user['id'])
                    self.message_send(event.user_id,
                                      f'{user["name"]}, Дата рождения: {user["bdate"]}',
                                      attachment=None
                                      )
                    attachment = ''
                    for num, photo in enumerate(photos_user):
                       attachment = f'photo{photo["owner_id"]}_{photo["id"]}'
                       self.message_send(event.user_id,
                                         None,
                                         attachment=attachment
                                         )
                       if num == 2:
                              break
                    self.message_send(event.user_id, f'Введите команду: Привет \ Начать \ Продолжить')
                elif command == 'продолжить':
                    if users == []:
                       users = self.api.serch_users(self.params, offset)
                    user = users.pop()
                    while read_from_db(self.params['id'],user['id']) != True:
                      if len(users) != 0:
                          user = users.pop()
                      else:
                          offset += 10
                          users = self.api.serch_users(self.params, offset)
                          user = users.pop()
                    photos_user = self.api.get_photos(user['id'])
                    self.message_send(event.user_id,
                                          f'{user["name"]}, Дата рождения: {user["bdate"]}',
                                          attachment=None
                                          )
                    attachment = ''
                    for num, photo in enumerate(photos_user):
                      attachment = f'photo{photo["owner_id"]}_{photo["id"]}'
                      self.message_send(event.user_id,
                                                  None,
                                                  attachment=attachment
                                                  )
                      if num == 2:
                                break
                    add_to_db(self.params['id'], user['id'])
                    self.message_send(event.user_id, f'Введите команду: Привет \ Начать \ Продолжить')
                else:
                   self.message_send(event.user_id, 'команда не опознана')


bot = BotInterface(comm_token, user_token)
# event = bot.longpoll.listen()
# bot.message_send(3843744,f'Начать, Продолжить, Выход')
bot.event_handler()
