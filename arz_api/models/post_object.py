from bs4 import BeautifulSoup
from requests import Response
from typing import TYPE_CHECKING

from arz_api.consts import MAIN_URL
if TYPE_CHECKING:
    from arz_api import ArizonaAPI
    from arz_api.models import Member, Thread


class Post:
    def __init__(self, API: 'ArizonaAPI', id: int, creator: 'Member', thread: 'Thread', create_date: int, bb_content: str, text_content: str) -> None:
        self.API = API
        self.id = id
        """**ID сообщения**"""
        self.creator = creator
        """**Объект Member отправителя сообщения**"""
        self.thread = thread
        """**Объект Thread темы, в которой оставлено сообщение**"""
        self.create_date = create_date
        """**Дата отправки сообщения в UNIX**"""
        self.bb_content = bb_content
        """**Сырое содержимое сообщения**"""
        self.text_content = text_content
        """**Текст из сообщения**"""

    def react(self, reaction_id: int = 1) -> Response:
        """Поставить реакцию на сообщение

        Attributes:
            reaction_id (int): ID реакции. По умолчанию 1 (необяз.)
            
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f'{MAIN_URL}/posts/{self.id}/react?reaction_id={reaction_id}', {'_xfToken': token})
    
    def edit(self, message_html: str) -> Response:
        """Отредактировать сообщение

        Attributes:
            message_html (str): Новое содержание сообщения. Рекомендуется использование HTML
        
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/posts/{self.id}/edit", {"message_html": message_html, "message": message_html, "_xfToken": token})

    def delete(self, reason: str, hard_delete: bool = False) -> Response:
        """Удалить сообщение

        Attributes:
            reason (str): Причина для удаления
            hard_delete (bool): Полное удаление сообщения. По умолчанию False (необяз.)
            
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/posts/{self.id}/delete", {"reason": reason, "hard_delete": int(hard_delete), "_xfToken": token})


class ProfilePost:
    def __init__(self, API: 'ArizonaAPI', id: int, creator: 'Member', profile: 'Member', create_date: int, bb_content: str, text_content: str) -> None:
        self.API = API
        self.id = id
        """**ID сообщения профиля**"""
        self.creator = creator
        """**Объект Member отправителя сообщения**"""
        self.profile = profile
        """**Объект Member профиля, в котором оставлено сообщение**"""
        self.create_date = create_date
        """**Дата отправки сообщения в UNIX**"""
        self.bb_content = bb_content
        """**Сырое содержимое сообщения**"""
        self.text_content = text_content
        """**Текст из сообщения**"""

    def react(self, reaction_id: int = 1) -> Response:
        """Поставить реакцию на сообщение профиля

        Attributes:
            reaction_id (int): ID реакции. По умолчанию 1 (необяз.)
            
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f'{MAIN_URL}/profile-posts/{self.id}/react?reaction_id={reaction_id}', {'_xfToken': token})

    def comment(self, message_html: str) -> Response:
        """Прокомментировать сообщение профиля

        Attributes:
            message_html (str): Текст комментария. Рекомендуется использование HTML
        
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/profile-posts/{self.id}/add-comment", {"message_html": message_html, "_xfToken": token})

    def delete(self, reason: str, hard_delete: bool = False) -> Response:
        """Удалить сообщение

        Attributes:
            reason (str): Причина для удаления
            hard_delete (bool): Полное удаление сообщения. По умолчанию False (необяз.)
            
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/profile-posts/{self.id}/delete", {"reason": reason, "hard_delete": int(hard_delete), "_xfToken": token})
    
    def edit(self, message_html: str) -> Response:
        """Отредактировать сообщение профиля

        Attributes:
            message_html (str): Новое содержание сообщения профиля. Рекомендуется использование HTML
        
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/profile-posts/{self.id}/edit", {"message_html": message_html, "message": message_html, "_xfToken": token})
