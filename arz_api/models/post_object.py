from bs4 import BeautifulSoup
from typing import TYPE_CHECKING

from arz_api.consts import MAIN_URL
if TYPE_CHECKING:
    from arz_api import ArizonaAPI
    from arz_api.models import Member, Thread


class Post:
    def __init__(self, API: 'ArizonaAPI', id: int, creator: 'Member', thread: 'Thread', create_date: int, bb_content: str, text_content: str) -> None:
        self.API = API
        self.id = id
        self.creator = creator
        self.thread = thread
        self.create_date = create_date
        self.bb_content = bb_content
        self.text_content = text_content

    def react(self, reaction_id: int) -> bool:
        """Поставить реакцию на пост"""

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        self.API.session.post(f'{MAIN_URL}/posts/{self.id}/react?reaction_id={reaction_id}', {'_xfToken': token})
        return True
    
    def edit(self, html_message: str):
        """Отредактировать пост"""

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        self.API.session.post(f"{MAIN_URL}/posts/{self.id}/edit", {"message_html": html_message, "message": html_message, "_xfToken": token})

    def delete(self, reason: str, hard_delete: int = 0) -> bool:
        """Удалить пост"""

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        self.API.session.post(f"{MAIN_URL}/posts/{self.id}/delete", {"reason": reason, "hard_delete": hard_delete, "_xfToken": token})
        return True


class ProfilePost:
    def __init__(self, API: 'ArizonaAPI', id: int, creator: 'Member', profile: 'Member', create_date: int, bb_content: str, text_content: str) -> None:
        self.API = API
        self.id = id
        self.creator = creator
        self.profile = profile
        self.create_date = create_date
        self.bb_content = bb_content
        self.text_content = text_content

    def react(self, reaction_id: int) -> bool:
        """Поставить реакцию на сообщение профиля"""

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        self.API.session.post(f'{MAIN_URL}/profile-posts/{self.id}/react?reaction_id={reaction_id}', {'_xfToken': token})
        return True

    def comment(self, message_html: str) -> bool:
        """Поставить комментарий на сообщение профиля"""

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        self.API.session.post(f"{MAIN_URL}/profile-posts/{self.id}/add-comment", {"message_html": message_html, "_xfToken": token})
        return True

    def delete(self, reason: str, hard_delete: int = 0) -> bool:
        """Удалить сообщение профиля"""

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        self.API.session.post(f"{MAIN_URL}/profile-posts/{self.id}/delete", {"reason": reason, "hard_delete": hard_delete, "_xfToken": token})
        return True
    
    def edit(self, html_message: str):
        """Отредактировать сообщение профиля"""

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        self.API.session.post(f"{MAIN_URL}/profile-posts/{self.id}/edit", {"message_html": html_message, "message": html_message, "_xfToken": token})
