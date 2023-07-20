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
        self.creator = creator
        self.category = category
        self.create_date = create_date
        self.title = title
        self.prefix = prefix
        self.content = content
        self.content_html = html_content
        self.pages_count = pages_content
        self.is_closed = is_closed
        self.thread_post_id = thread_post_id

    def answer(self, html_message: str) -> Response:
        """Оставить ответ в теме"""

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/threads/{self.id}/add-reply", {'_xfToken': token, 'message_html': html_message})


    def watch(self, stop: bool, email_subscribe: bool = False) -> Response:
        """Изменить статус отслеживания темы"""

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/threads/{self.id}/watch", {'_xfToken': token, 'stop': int(stop), 'email_subscribe': int(email_subscribe)})
    

    def close(self) -> Response:
        """Закрыть/открыть тему (для модерации)"""

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/threads/{self.id}/quick-close", {'_xfToken': token})


    def pin(self) -> Response:
        """Закрепить/открепить тему (для модерации)"""

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/threads/{self.id}/quick-stick", {'_xfToken': token})
    

    def edit(self, html_message: str) -> Response:
        """Отредактировать тему"""

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/posts/{self.thread_post_id}/edit", {"message_html": html_message, "message": html_message, "_xfToken": token})


    def edit_info(self, title: str = None, prefix_id: int = None) -> Response:
        """Изменить заголовок и префикс темы"""

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        data = {"_xfToken": token}

        if title is not None: data.update({'title': title})
        if prefix_id is not None: data.update({'prefix_id[]', prefix_id})

        return self.API.session.post(f"{MAIN_URL}/threads/{self.id}/edit", data)


    def delete(self, reason: str, hard_delete: int = 0) -> Response:
        """Удалить тему"""

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f"{MAIN_URL}/threads/{self.id}/delete", {"reason": reason, "hard_delete": hard_delete, "_xfToken": token})


    def react(self, reaction_id: int) -> Response:
        """Поставить реакцию на тему"""

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.API.session.post(f'{MAIN_URL}/posts/{self.thread_post_id}/react?reaction_id={reaction_id}', {'_xfToken': token})
    

    def get_posts(self, page: int = 1) -> list:
        """Получить все посты из темы"""

        soup = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/threads/{self.id}/page-{page}").content, 'lxml')
        return [i['id'].strip('js-post-') for i in soup.find_all('article', {'id': compile('js-post-*')})]
