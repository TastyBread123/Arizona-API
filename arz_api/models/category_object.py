from bs4 import BeautifulSoup
from re import compile, findall
from typing import TYPE_CHECKING

from arz_api.consts import MAIN_URL
if TYPE_CHECKING:
    from arz_api import ArizonaAPI


class Category:
    def __init__(self, API: 'ArizonaAPI', id: int, title: str, pages_count: int) -> None:
        self.API = API
        self.id = id
        self.title = title
        self.pages_count = pages_count


    def create_thread(self, title: str, message_html: str, discussion_type: str = 'discussion', watch_thread: int = 1) -> bool:
        """Создать тему в категории"""
        # TODO: сделать возврат ID новой темы

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        self.API.session.post(f"{MAIN_URL}/forums/{self.id}/post-thread?inline-mode=1", {'_xfToken': token, 'title': title, 'message_html': message_html, 'discussion_type': discussion_type, 'watch_thread': watch_thread})
        return True


    def set_read(self) -> bool:
        """Отметить тему как прочитанную"""

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        self.API.session.post(f"{MAIN_URL}/forums/{self.id}/mark-read", {'_xfToken': token})
        return True
    

    def watch(self, notify: str, send_alert: bool = True, send_email: bool = False, stop: bool = False) -> bool:
        """Настроить отслеживание темы\n
        :param notify - Возможные варианты: "thread", "message", "" """

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']

        if stop: self.API.session.post(f"{MAIN_URL}/forums/{self.id}/watch", {'_xfToken': token, 'stop': "1"})
        else: self.API.session.post(f"{MAIN_URL}/forums/{self.id}/watch", {'_xfToken': token, 'send_alert': int(send_alert), 'send_email': int(send_email), 'notify': notify})

        return True

    
    def get_threads(self, page: int = 1) -> list:
        """Получить темы из раздела"""

        soup = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/forums/{self.id}/page-{page}").content, "lxml")
        result = []
        for thread in soup.find_all('div', compile('structItem structItem--thread.*')):
            link = object
            for el in thread.find_all('div', "structItem-title")[0].find_all("a"): 
                if "threads" in el['href']: link = el

            result.append(int(findall(r'\d+', link['href'])[0]))
        
        return result


    def get_categories(self) -> list:
        """Получить дочерние категории из раздела"""

        soup = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/forums/{self.id}/page-1").content, "lxml")
        result = []
        for category in soup.find_all('div', compile('.*node--depth2 node--forum.*')): 
            result.append(int(findall(r'\d+', category.find("a")['href'])[0]))
        
        return result
