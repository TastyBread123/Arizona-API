from requests import Response
from typing import TYPE_CHECKING

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

        return self.API.close_thread(self.id)


    def pin(self) -> Response:
        """Закрепить/открепить тему (для модерации)
        
        Returns:
            Объект Response модуля requests
        """

        return self.API.pin_thread(self.id)
    

    def answer(self, message_html: str) -> Response:
        """Оставить сообщение в теме

        Attributes:
            message_html (str): Cодержание ответа. Рекомендуется использование HTML
        
        Returns:
            Объект Response модуля requests
        """

        return self.API.answer_thread(self.id, message_html)


    def watch(self, email_subscribe: bool = False, stop: bool = False) -> Response:
        """Изменить статус отслеживания темы

        Attributes:
            email_subscribe (bool): Отправлять ли уведомления на почту. По умолчанию False (необяз.)
            stop (bool): - Принудительно прекратить отслеживание. По умолчанию False (необяз.)
        
        Returns:
            Объект Response модуля requests
        """

        return self.API.watch_thread(self.id, email_subscribe, stop)
    

    def delete(self, reason: str, hard_delete: bool = False) -> Response:
        """Удалить тему

        Attributes:
            reason (str): Причина для удаления
            hard_delete (bool): Полное удаление сообщения. По умолчанию False (необяз.)
            
        Returns:
            Объект Response модуля requests
        """

        return self.API.delete_thread(self.id, reason, hard_delete)
    

    def edit(self, message_html: str) -> Response:
        """Отредактировать содержимое темы

        Attributes:
            message_html (str): Новое содержимое ответа. Рекомендуется использование HTML
        
        Returns:
            Объект Response модуля requests
        """

        return self.API.edit_thread(self.id, message_html)


    def edit_info(self, title: str = None, prefix_id: int = None, sticky: bool = True, opened: bool = True) -> Response:
        """Изменить заголовок и/или префикс темы

        Attributes:
            title (str): Новое название
            prefix_id (int): Новый ID префикса
            sticky (bool): Закрепить (True - закреп / False - не закреп)
            opened (bool): Открыть/закрыть тему (True - открыть / False - закрыть)
        
        Returns:
            Объект Response модуля requests
        """

        return self.API.edit_thread_info(self.id, title, prefix_id, sticky, opened)
    

    def get_posts(self, page: int = 1) -> list:
        """Получить все ID сообщений из темы на странице

        Attributes:
            page (int): Cтраница для поиска. По умолчанию 1 (необяз.)
        
        Returns:
            Список (list), состоящий из ID всех сообщений на странице
        """

        return self.API.get_thread_posts(self.id, page)


    def react(self, reaction_id: int = 1) -> Response:
        """Поставить реакцию на тему

        Attributes:
            reaction_id (int): ID реакции. По умолчанию 1 (необяз.)
            
        Returns:
            Объект Response модуля requests
        """

        return self.API.react_thread(self.id, reaction_id)
    

    def get_url(self) -> str:
        """Получить ссылку на объект
        
        Returns:
            Ссылку в формате https://forum.arizona-rp.com/threads/x/"""
        
        return f"https://forum.arizona-rp.com/threads/{self.id}/"
