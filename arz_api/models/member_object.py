from bs4 import BeautifulSoup
from requests import Response
from re import compile
from typing import TYPE_CHECKING

from arz_api.consts import MAIN_URL

if TYPE_CHECKING:
    from arz_api.api import ArizonaAPI


class Member:
    API: 'ArizonaAPI'  # Объект ArizonaAPI

    id: int
    username: str
    user_title: str
    avatar: str
    roles: list
    
    messages_count: int
    reactions_count: int
    trophies_count: int

    def __init__(self, API, id: int, username: str, user_title: str, avatar: str, roles: list, messages_count: int, reactions_count: int, trophies_count: int) -> None:
        self.API = API
        self.id = id
        """**ID пользователя**"""
        self.username = username
        """**Имя пользователя**"""
        self.user_title = user_title
        """**Звание пользователя**"""
        self.avatar = avatar
        """**Ссылка на аватарку пользователя**"""
        self.roles = roles
        """Роль пользователя на форуме ('покраска')"""

        self.messages_count = messages_count
        """**Количество сообщений в счетчике**"""
        self.reactions_count = reactions_count
        """**Количество реакций в счетчике**"""
        self.trophies_count = trophies_count
        """**Количество баллов в счетчике**"""

    def follow(self) -> Response:
        """Изменить статус подписки на пользователя
        
        Returns:
            Объект Response модуля requests
        """

        return self.API.follow_member(self.id)
    
    def ignore(self) -> Response:
        """Изменить статус игнорирования пользователя
        
        Returns:
            Объект Response модуля requests
        """

        return self.API.ignore_member(self.id)
    
    def add_message(self, message_html: str) -> Response:
        """Отправить сообщение на стенку пользователя

        Attributes:
            message_html (str): Текст сообщения. Рекомендуется использование HTML
            
        Returns:
            Объект Response модуля requests
        """

        return self.API.answer_thread(self.id, message_html)
    
    def get_profile_messages(self, page: int = 1) -> list:
        """Возвращает ID всех сообщений со стенки пользователя на странице

        Attributes:
            page (int): Страница для поиска. По умолчанию 1 (необяз.)
            
        Returns:
            Cписок (list) с ID всех сообщений профиля
        """

        return self.API.get_profile_messages(self.id, page)
    
    def get_url(self) -> str:
        """Получить ссылку на объект
        
        Returns:
            Ссылку в формате https://forum.arizona-rp.com/members/x/"""
        
        return f"https://forum.arizona-rp.com/members/{self.id}/"


class CurrentMember(Member):
    follow = property(doc='Forbidden method for Current Member object')
    ignore = property(doc='Forbidden method for Current Member object')

    def edit_avatar(self, upload_photo: str) -> Response:
        """Изменить аватарку пользователя

        Attributes:
            upload_photo (str): Относительный или полный путь до изображения
        
        Returns:
            Объект Response модуля requests
        """

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
    

    def delete_avatar(self) -> Response:
        """Удалить автарку пользователя
        
        Returns:
            Объект Response модуля requests
        """
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
