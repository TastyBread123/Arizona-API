from bs4 import BeautifulSoup
from requests import Response
from re import compile
from typing import TYPE_CHECKING

from arz_api.consts import MAIN_URL
from arz_api.exceptions import ThisIsYouError

if TYPE_CHECKING:
    from arz_api.api import ArizonaAPI


class Member:
    API: 'ArizonaAPI'  # Объект ArizonaAPI

    id: int
    username: str
    user_title: str
    avatar: str
    
    messages_count: int
    reactions_count: int
    trophies_count: int

    def __init__(self, API, id: int, username: str, user_title: str, avatar: str, messages_count: int, reactions_count: int, trophies_count: int) -> None:
        self.API = API
        self.id = id
        self.username = username
        self.user_title = user_title
        self.avatar = avatar

        self.messages_count = messages_count
        self.reactions_count = reactions_count
        self.trophies_count = trophies_count

    def follow(self) -> Response:
        """Изменить статус подписки на пользователя"""

        if self.id == self.API.current_member.id: raise ThisIsYouError(self.id)

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/members/{self.id}/follow", {'_xfToken': token})
    
    def ignore(self) -> Response:
        """Изменить статус игнора пользователя"""

        if self.id == self.API.current_member.id: raise ThisIsYouError(self.id)

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/members/{self.id}/ignore", {'_xfToken': token})
    
    def add_message(self, message_html: str) -> Response:
        """Отправить сообщение на стенку пользователя
        :param message_html - текст сообщения. Рекомендуется использование HTML"""

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/members/{self.id}/post", {'_xfToken': token, 'message_html': message_html})
    
    def get_profile_messages(self, page: int = 1) -> list:
        """Возвращает ID всех сообщений со стенки пользователя
        :param page - (необяз.) страница для поиска. По умолчанию 1"""

        soup = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/members/{self.id}/page-{page}").content, "lxml")
        return [int(post['id'].strip('js-profilePost-')) for post in soup.find_all('article', {'id': compile('js-profilePost-*')})]


class CurrentMember(Member):
    follow = property(doc='Forbidden method for Current Member object')
    ignore = property(doc='Forbidden method for Current Member object')

    def edit_avatar(self, upload_photo: str):
        """Изменить аватарку пользователя
        :param upload_photo - относительный или полный путь до фото"""

        with open(upload_photo, 'rb') as image:
            file_dict = {'upload': (upload_photo, image.read())}
        
        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        data = {
            "avatar_crop_x": 0, 
            "avatar_crop_y": 0,
            "_xfToken": token, 
            "use_custom": 1,
        }
        return self.API.session.post(f"{MAIN_URL}/account/avatar", files=file_dict, data=data)
    

    def delete_avatar(self):
        """Удалить автарку пользователя"""
        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        file_dict = {'upload': ("", "")}
        data = {
            "avatar_crop_x": 0, 
            "avatar_crop_y": 0,
            "_xfToken": token, 
            "use_custom": 1,
            "delete_avatar": 1
        }
        return self.API.session.post(f"{MAIN_URL}/account/avatar", files=file_dict, data=data)


    # TODO:
    #def get_last_notifications(self, time_offset: int = 86400, limit: int = 100), change_avatar(), change_banner()
