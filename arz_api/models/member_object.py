from typing import TYPE_CHECKING
from bs4 import BeautifulSoup
from arz_api.consts import MAIN_URL
from arz_api.exceptions import ThisIsYouError

if TYPE_CHECKING:
    from arz_api.api import ArizonaAPI


class Member:
    API: 'ArizonaAPI'  # объект ArizonaAPI

    id: int
    username: str
    user_title: str | None
    avatar: str | None
    
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

    def follow(self) -> bool:
        """Подписка на пользователя"""

        if self.id == self.API.current_member.id: raise ThisIsYouError(self.id)

        token = BeautifulSoup(self.API.session.get(MAIN_URL + f"/members/{self.id}/follow").content, 'lxml').find('input', {'name': '_xfToken'})['value']
        self.API.session.post(MAIN_URL + f"/members/{self.id}/follow", {'_xfToken': token})
        return True
    
    def add_message(self, message_html: str) -> bool:
        """Отправить сообщение на стенку пользователя"""

        token = BeautifulSoup(self.API.session.get(MAIN_URL + f"/members/{self.id}/post").content, 'lxml').find('input', {'name': '_xfToken'})['value']
        self.API.session.post(MAIN_URL + f"/members/{self.id}/post", {'_xfToken': token, 'message_html': message_html})
        return True


class CurrentMember(Member):
    follow = property(doc='Forbidden method for Current Member object')

    # TODO:
    #def get_last_notifications(self, time_offset: int = 86400, limit: int = 100) -> bool:
    #    return False
