from bs4 import BeautifulSoup
from requests import Response
from re import compile
from typing import TYPE_CHECKING

from arz_api.consts import MAIN_URL
if TYPE_CHECKING:
    from arz_api.models.member_object import Member
    from arz_api.models.category_object import Category
    from arz_api import ArizonaAPI


class Thread:
    def __init__(self, API: 'ArizonaAPI', id: int, creator: 'Member', category: 'Category', create_date: int, title: str, prefix: str, content: str, html_content: str, pages_content: int, thread_post_id: int, is_closed: bool) -> None:
        self.API = API
        self.id = id
        """**ID темы**"""
        self.creator = creator
        """**Объект Member создателя темы**"""
        self.category = category
        """**Объект Category раздела, в котором создана тема**"""
        self.create_date = create_date
        """**Дата создания темы в UNIX**"""
        self.title = title
        """**Заголовок темы**"""
        self.prefix = prefix
        """**Префикс темы**"""
        self.content = content
        """**Текст из темы**"""
        self.content_html = html_content
        """**Сырой контент темы**"""
        self.pages_count = pages_content
        """**Количество страниц с ответами в теме**"""
        self.is_closed = is_closed
        """**Закрыта ли тема**"""
        self.thread_post_id = thread_post_id
        """**ID сообщения темы (post_id)**"""


    def close(self) -> Response:
        """Закрыть/открыть тему (для модерации)
        
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/threads/{self.id}/quick-close", {'_xfToken': token})


    def pin(self) -> Response:
        """Закрепить/открепить тему (для модерации)
        
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/threads/{self.id}/quick-stick", {'_xfToken': token})
    

    def answer(self, message_html: str) -> Response:
        """Оставить сообщение в теме

        Attributes:
            message_html (str): Cодержание ответа. Рекомендуется использование HTML
        
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/threads/{self.id}/add-reply", {'_xfToken': token, 'message_html': message_html})


    def watch(self, email_subscribe: bool = False, stop: bool = False) -> Response:
        """Изменить статус отслеживания темы

        Attributes:
            email_subscribe (bool): Отправлять ли уведомления на почту. По умолчанию False (необяз.)
            stop (bool): - Принудительно прекратить отслеживание. По умолчанию False (необяз.)
        
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/threads/{self.id}/watch", {'_xfToken': token, 'stop': int(stop), 'email_subscribe': int(email_subscribe)})
    

    def delete(self, reason: str, hard_delete: bool = False) -> Response:
        """Удалить тему

        Attributes:
            reason (str): Причина для удаления
            hard_delete (bool): Полное удаление сообщения. По умолчанию False (необяз.)
            
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/threads/{self.id}/delete", {"reason": reason, "hard_delete": int(hard_delete), "_xfToken": token})
    

    def edit(self, message_html: str) -> Response:
        """Отредактировать содержимое темы

        Attributes:
            message_html (str): Новое содержимое ответа. Рекомендуется использование HTML
        
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/posts/{self.thread_post_id}/edit", {"message_html": message_html, "message": message_html, "_xfToken": token})


    def edit_info(self, title: str = None, prefix_id: int = None) -> Response:
        """Изменить заголовок и/или префикс темы

        Attributes:
            title (str): Новое название
            prefix_id (int): Новый ID префикса
        
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        data = {"_xfToken": token}

        if title is not None: data.update({'title': title})
        if prefix_id is not None: data.update({'prefix_id[]', prefix_id})

        return self.API.session.post(f"{MAIN_URL}/threads/{self.id}/edit", data)
    

    def get_posts(self, page: int = 1) -> list:
        """Получить все ID сообщений из темы на странице

        Attributes:
            page (int): Cтраница для поиска. По умолчанию 1 (необяз.)
        
        Returns:
            Список (list), состоящий из ID всех сообщений на странице
        """

        soup = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/threads/{self.id}/page-{page}").content, 'lxml')
        return [i['id'].strip('js-post-') for i in soup.find_all('article', {'id': compile('js-post-*')})]


    def react(self, reaction_id: int = 1) -> Response:
        """Поставить реакцию на тему

        Attributes:
            reaction_id (int): ID реакции. По умолчанию 1 (необяз.)
            
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f'{MAIN_URL}/posts/{self.thread_post_id}/react?reaction_id={reaction_id}', {'_xfToken': token})
