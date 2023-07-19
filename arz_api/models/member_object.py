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
        """Отправить сообщение на стенку пользователя"""

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/members/{self.id}/post", {'_xfToken': token, 'message_html': message_html})
    
    def get_profile_messages(self, page: int = 1) -> list:
        """Возвращает ID всех сообщений со стенки пользователя"""

        soup = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/members/{self.id}/page-{page}").content, "lxml")
        result = []
        for post in soup.find_all('article', {'id': compile('js-profilePost-*')}):
            result.append(int(post['id'].strip('js-profilePost-')))

        return result


class CurrentMember(Member):
    follow = property(doc='Forbidden method for Current Member object')
    ignore = property(doc='Forbidden method for Current Member object')

    # TODO:
    #def get_last_notifications(self, time_offset: int = 86400, limit: int = 100) -> bool:
    #    return False
