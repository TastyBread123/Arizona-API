from requests import Response
from typing import TYPE_CHECKING

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

        return self.API.react_post(self.id, reaction_id)
    

    def edit(self, message_html: str) -> Response:
        """Отредактировать сообщение

        Attributes:
            message_html (str): Новое содержание сообщения. Рекомендуется использование HTML
        
        Returns:
            Объект Response модуля requests
        """

        return self.API.edit_post(self.id, message_html)


    def delete(self, reason: str, hard_delete: bool = False) -> Response:
        """Удалить сообщение

        Attributes:
            reason (str): Причина для удаления
            hard_delete (bool): Полное удаление сообщения. По умолчанию False (необяз.)
            
        Returns:
            Объект Response модуля requests
        """

        return self.API.delete_post(self.id, reason, hard_delete)
    
    
    def bookmark(self) -> Response:
        """Добавить сообщение в закладки
        
        Returns:
            Объект Response модуля requests"""
        return self.API.bookmark_post(self.id)
    

    def get_url(self) -> str:
        """Получить ссылку на объект
        
        Returns:
            Ссылку в формате https://forum.arizona-rp.com/posts/x/"""
        
        return f"https://forum.arizona-rp.com/posts/{self.id}/"


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

        return self.API.react_profile_post(self.id, reaction_id)


    def comment(self, message_html: str) -> Response:
        """Прокомментировать сообщение профиля

        Attributes:
            message_html (str): Текст комментария. Рекомендуется использование HTML
        
        Returns:
            Объект Response модуля requests
        """

        return self.API.comment_profile_post(self.id, message_html)


    def delete(self, reason: str, hard_delete: bool = False) -> Response:
        """Удалить сообщение

        Attributes:
            reason (str): Причина для удаления
            hard_delete (bool): Полное удаление сообщения. По умолчанию False (необяз.)
            
        Returns:
            Объект Response модуля requests
        """

        return self.API.delete_profile_post(self.id, reason, hard_delete)
    

    def edit(self, message_html: str) -> Response:
        """Отредактировать сообщение профиля

        Attributes:
            message_html (str): Новое содержание сообщения профиля. Рекомендуется использование HTML
        
        Returns:
            Объект Response модуля requests
        """

        return self.API.edit_profile_post(self.id, message_html)


    def get_url(self) -> str:
        """Получить ссылку на объект
        
        Returns:
            Ссылку в формате https://forum.arizona-rp.com/profile-posts/x/"""
        
        return f"https://forum.arizona-rp.com/profile-posts/{self.id}/"