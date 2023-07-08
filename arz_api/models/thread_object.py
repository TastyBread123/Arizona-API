from typing import TYPE_CHECKING
from bs4 import BeautifulSoup
from re import compile

from arz_api.consts import MAIN_URL
if TYPE_CHECKING:
    from arz_api.models.member_object import Member
    from arz_api.models.category_object import Category
    from arz_api import ArizonaAPI


class Thread:
    def __init__(self, API: 'ArizonaAPI', id: int | str, creator: 'Member', category: 'Category', create_date: int, title: str, content: str, html_content: str, pages_content: int, thread_post_id: int, is_closed: bool) -> None:
        self.API = API
        self.id = id
        self.creator = creator
        self.category = category
        self.create_date = create_date
        self.title = title
        self.content = content
        self.content_html = html_content
        self.pages_count = pages_content
        self.is_closed = is_closed
        self.thread_post_id = thread_post_id

    def answer(self, html_message: str) -> bool:
        """Оставить ответ в теме"""

        token = BeautifulSoup(self.API.session.get(MAIN_URL + f"/threads/{self.id}").content, 'lxml').find('input', {'name': '_xfToken'})['value']
        self.API.session.post(MAIN_URL + f"/threads/{self.id}/add-reply", {'_xfToken': token, 'message_html': html_message})
        return True


    def watch(self, stop: bool, email_subscribe: bool = False) -> bool:
        """Начать отслеживать тему"""

        token = BeautifulSoup(self.API.session.get(MAIN_URL + f"/threads/{self.id}/watch").content, 'lxml').find('input', {'name': '_xfToken'})['value']
        self.API.session.post(MAIN_URL + f"/threads/{self.id}/watch", {'_xfToken': token, 'stop': int(stop), 'email_subscribe': int(email_subscribe)})
        return True
    

    def close(self) -> bool:
        """Закрыть тему (для модерации)"""

        token = BeautifulSoup(self.API.session.get(MAIN_URL + f"/threads/{self.id}/quick-close").content, 'lxml').find('input', {'name': '_xfToken'})['value']
        self.API.session.post(MAIN_URL + f"/threads/{self.id}/quick-close", {'_xfToken': token})
        return True


    def pin(self) -> bool:
        """Закрепить тему (для модерации)"""

        token = BeautifulSoup(self.API.session.get(MAIN_URL + f"/threads/{self.id}/quick-stick").content, 'lxml').find('input', {'name': '_xfToken'})['value']
        self.API.session.post(MAIN_URL + f"/threads/{self.id}/quick-stick", {'_xfToken': token})
        return True
    

    def edit(self, html_message: str):
        """Отредактировать тему"""

        token = BeautifulSoup(self.API.session.get(MAIN_URL + f"/posts/{self.thread_post_id}/edit").content, 'lxml').find('input', {'name': '_xfToken'})['value']
        self.API.session.post(f"{MAIN_URL}/posts/{self.thread_post_id}/edit", {"message_html": html_message, "message": html_message, "_xfToken": token})


    def delete(self, reason: str, hard_delete: int = 0) -> bool:
        """Удалить тему"""

        token = BeautifulSoup(self.API.session.get(MAIN_URL + f"/threads/{self.id}/delete").content, 'lxml').find('input', {'name': '_xfToken'})['value']
        self.API.session.post(f"{MAIN_URL}/threads/{self.id}/delete", {"reason": reason, "hard_delete": hard_delete, "_xfToken": token})
        return True


    def make_reaction(self, reaction_id: int) -> bool:
        """Поставить реакцию на тему"""

        token = BeautifulSoup(self.API.session.get(f"{MAIN_URL}/posts/{self.thread_post_id}/react?reaction_id={reaction_id}").content, 'lxml').find('input', {'name': '_xfToken'})['value']
        self.API.session.post(f'{MAIN_URL}/posts/{self.thread_post_id}/react?reaction_id={reaction_id}', {'_xfToken': token})
        return True
    

    def get_posts(self, page: int) -> list | None:
        """Получить все посты из темы"""

        soup = BeautifulSoup(self.API.session.get(MAIN_URL + f"/threads/{self.id}/page-{page}").content, 'lxml')

        return_data = []
        for i in soup.find_all('article', {'id': compile('js-post-*')}):
            if i['id'].startswith('js-post-') == False: continue
            return_data.append(i['id'].strip('js-post-'))

        return return_data
