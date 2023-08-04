from bs4 import BeautifulSoup
from requests import Response
from re import compile, findall
from typing import TYPE_CHECKING

from arz_api.consts import MAIN_URL
if TYPE_CHECKING:
    from arz_api import ArizonaAPI


class Category:
    def __init__(self, API: 'ArizonaAPI', id: int, title: str, pages_count: int) -> None:
        self.API = API
        self.id = id
        """**ID категории**"""
        self.title = title
        """**Название категории**"""
        self.pages_count = pages_count
        """**Количество страниц в категории**"""


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

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/forums/{self.id}/post-thread?inline-mode=1", {'_xfToken': token, 'title': title, 'message_html': message_html, 'discussion_type': discussion_type, 'watch_thread': watch_thread})


    def set_read(self) -> Response:
        """Отметить категорию как прочитанную
        
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/forums/{self.id}/mark-read", {'_xfToken': token})
    

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

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']

        if stop: return self.API.session.post(f"{MAIN_URL}/forums/{self.id}/watch", {'_xfToken': token, 'stop': "1"})
        else: return self.API.session.post(f"{MAIN_URL}/forums/{self.id}/watch", {'_xfToken': token, 'send_alert': int(send_alert), 'send_email': int(send_email), 'notify': notify})
    

    def get_threads(self, page: int = 1) -> dict:
        """Получить темы из раздела

        Attributes:
            page (int): Cтраница для поиска. По умолчанию 1 (необяз.)
            
        Returns:
            Словарь (dict), состоящий из списков закрепленных ('pins') и незакрепленных ('unpins') тем
        """

        soup = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/forums/{self.id}/page-{page}").content, "lxml")
        result = {'pins': [], 'unpins': []}
        for thread in soup.find_all('div', compile('structItem structItem--thread.*')):
            link = thread.find_all('div', "structItem-title")[0].find_all("a")[-1]
            if len(findall(r'\d+', link['href'])) < 1: continue

            if len(thread.find_all('i', {'title': 'Закреплено'})) > 0: result['pins'].append(int(findall(r'\d+', link['href'])[0]))
            else: result['unpins'].append(int(findall(r'\d+', link['href'])[0]))
        
        return result


    def get_categories(self) -> list:
        """Получить дочерние категории из раздела
        
        Returns:
            Список (list), состоящий из ID дочерних категорий раздела
        """

        soup = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/forums/{self.id}/page-1").content, "lxml")
        return [int(findall(r'\d+', category.find("a")['href'])[0]) for category in soup.find_all('div', compile('.*node--depth2 node--forum.*'))]
