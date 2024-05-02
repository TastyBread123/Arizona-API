from requests import Response
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arz_api import ArizonaAPI


class Category:
    def __init__(self, API: 'ArizonaAPI', id: int, title: str, pages_count: int, parent_category_id: int) -> None:
        self.API = API
        self.id = id
        """**ID категории**"""
        self.title = title
        """**Название категории**"""
        self.pages_count = pages_count
        """**Количество страниц в категории**"""
        self.parent_category_id = parent_category_id
        """**ID предыдуще категории (родительская). Если нет - None**"""


    def create_thread(self, title: str, message_html: str, discussion_type: str = 'discussion', watch_thread: int = 1) -> Response:
        """Создать тему в категории

        Attributes:
            title (str): Название темы
            message_html (str): Содержание темы. Рекомендуется использование HTML
            discussion_type (str): - Тип темы | Возможные варианты: 'discussion' - обсуждение (по умолчанию), 'article' - статья, 'poll' - опрос (необяз.)
            watch_thread (str): - Отслеживать ли тему. По умолчанию True (необяз.)
        
        Returns:
            Объект Response модуля requests

        Todo:
            Cделать возврат ID новой темы
        """

        return self.API.create_thread(self.id, title, message_html, discussion_type, watch_thread)


    def set_read(self) -> Response:
        """Отметить категорию как прочитанную
        
        Returns:
            Объект Response модуля requests
        """

        return self.API.set_read_category(self.id)
    

    def watch(self, notify: str, send_alert: bool = True, send_email: bool = False, stop: bool = False) -> Response:
        """Настроить отслеживание категории

        Attributes:
            notify (str): Объект отслеживания. Возможные варианты: "thread", "message", ""
            send_alert (bool): - Отправлять ли уведомления на форуме. По умолчанию True (необяз.)
            send_email (bool): - Отправлять ли уведомления на почту. По умолчанию False (необяз.)
            stop (bool): - Принудительное завершение отслеживания. По умолчанию False (необяз.)

        Returns:
            Объект Response модуля requests    
        """

        return self.API.watch_category(self.id, notify, send_alert, send_email, stop)
    

    def get_threads(self, page: int = 1) -> dict:
        """Получить темы из раздела

        Attributes:
            page (int): Cтраница для поиска. По умолчанию 1 (необяз.)
            
        Returns:
            Словарь (dict), состоящий из списков закрепленных ('pins') и незакрепленных ('unpins') тем
        """

        return self.API.get_threads(self.id, page)


    def get_categories(self) -> list:
        """Получить дочерние категории из раздела
        
        Returns:
            Список (list), состоящий из ID дочерних категорий раздела
        """

        return self.API.get_categories(self.id)
    

    def get_url(self) -> str:
        """Получить ссылку на объект
        
        Returns:
            Ссылку в формате https://forum.arizona-rp.com/forums/x/"""
        
        return f"https://forum.arizona-rp.com/forums/{self.id}/"
