from requests import session, Response
from bs4 import BeautifulSoup
from re import compile, findall

from arz_api.exceptions import ThisIsYouError
from arz_api.bypass_antibot import bypass
from arz_api.consts import MAIN_URL
from arz_api.models.category_object import Category
from arz_api.models.member_object import Member, CurrentMember
from arz_api.models.thread_object import Thread
from arz_api.models.other import Statistic
from arz_api.models.post_object import Post, ProfilePost
from arz_api.exceptions import IncorrectLoginData



class ArizonaAPI:
    def __init__(self, user_agent: str, cookie: dict, do_bypass: bool = True) -> None:
        self.user_agent = user_agent
        self.cookie = cookie
        self.session = session()
        self.session.headers = {"user-agent": user_agent}
        self.session.cookies.update(cookie)

        if do_bypass:
            name, code = str(bypass(user_agent)).split('=')
            self.session.cookies.set(name, code)

        if BeautifulSoup(self.session.get(f"{MAIN_URL}").content, 'lxml').find('html')['data-logged-in'] == "false":
            raise IncorrectLoginData

    
    def logout(self):
        """Закрыть сессию"""

        return self.session.close()

    
    @property
    def current_member(self) -> CurrentMember:
        """Объект текущего пользователя"""

        content = BeautifulSoup(self.session.get(f"{MAIN_URL}/account").content, 'lxml')
        user_id = int(content.find('span', {'class': 'avatar avatar--xxs'})['data-user-id'])
        member_info = self.get_member(user_id)

        return CurrentMember(self, user_id, member_info.username, member_info.user_title, member_info.avatar, member_info.messages_count, member_info.reactions_count, member_info.trophies_count)

    
    def get_category(self, category_id: int) -> Category:
        """Найти раздел по ID"""

        content = BeautifulSoup(self.session.get(f"{MAIN_URL}/forums/{category_id}").content, 'lxml')
        title = content.find('h1', {'class': 'p-title-value'}).text

        try: pages_count = int(content.find_all('li', {'class': 'pageNav-page'})[-1].text)
        except IndexError: pages_count = 1
        try: parent_category_id = int(content.find('html')['data-container-key'].strip('node-'))
        except: parent_category_id = None

        temp_url = ''
        if parent_category_id is not None: temp_url = f'forums/{parent_category_id}/'
        content = BeautifulSoup(self.session.get(f"{MAIN_URL}/{temp_url}").content, 'lxml')
        
        return Category(self, category_id, title, pages_count)
    
    
    def get_member(self, user_id: int) -> Member:
        """Найти пользователя по ID"""

        content = BeautifulSoup(self.session.get(f"{MAIN_URL}/members/{user_id}").content, 'lxml')
        username = content.find('span', {'class': 'username'}).text
        
        try: user_title = content.find('span', {'class': 'userTitle'}).text
        except AttributeError: user_title = None
        try: avatar = content.find('a', {'class': 'avatar avatar--l'})['href']
        except TypeError: avatar = None

        messages_count = int(content.find('a', {'href': f'/search/member?user_id={user_id}'}).text.strip().replace(',', ''))
        reactions_count = int(content.find('dl', {'class': 'pairs pairs--rows pairs--rows--centered'}).find('dd').text.strip().replace(',', ''))
        trophies_count = int(content.find('a', {'href': f'/members/{user_id}/trophies'}).text.strip().replace(',', ''))
        
        return Member(self, user_id, username, user_title, avatar, messages_count, reactions_count, trophies_count)

    
    def get_thread(self, thread_id: int) -> Thread:
        """Найти тему по ID"""

        content = BeautifulSoup(self.session.get(f"{MAIN_URL}/threads/{thread_id}/page-1").content, 'lxml')
        
        try: creator = self.get_member(int(content.find('a', {'class': 'username'})['data-user-id']))
        except: creator = Member(self, int(content.find('a', {'class': 'username'})['data-user-id']), content.find('a', {'class': 'username'}).text, None, None, None, None, None)
        
        category = self.get_category(int(content.find('html')['data-container-key'].strip('node-')))
        create_date = int(content.find('time')['data-time'])
        
        try: title = [i for i in content.find('h1', {'class': 'p-title-value'}).strings][-1]
        except: title = ""
        try: prefix = content.find('h1', {'class': 'p-title-value'}).find('span', {'class': 'label'}).text
        except: prefix = ""
        thread_content_html = content.find('div', {'class': 'bbWrapper'})
        thread_content = thread_content_html.text
        
        try: pages_count = int(content.find_all('li', {'class': 'pageNav-page'})[-1].text)
        except IndexError: pages_count = 1

        is_closed = False
        if content.find('dl', {'class': 'blockStatus'}): is_closed = True
        thread_post_id = content.find('article', {'id': compile('js-post-*')})['id'].strip('js-post-')

        return Thread(self, thread_id, creator, category, create_date, title, prefix, thread_content, thread_content_html, pages_count, thread_post_id, is_closed)
    

    def get_post(self, post_id: int) -> Post:
        """Найти пост по ID"""

        content = BeautifulSoup(self.session.get(f"{MAIN_URL}/posts/{post_id}").content, 'lxml')
        post = content.find('article', {'id': f'js-post-{post_id}'})
        
        try: creator = self.get_member(int(post.find('a', {'data-xf-init': 'member-tooltip'})['data-user-id']))
        except:
            user_info = post.find('a', {'data-xf-init': 'member-tooltip'})
            creator = Member(self, int(user_info['data-user-id']), user_info.text, None, None, None, None, None)

        thread = self.get_thread(int(content.find('html')['data-content-key'].strip('thread-')))
        create_date = int(post.find('time', {'class': 'u-dt'})['data-time'])
        bb_content = post.find('div', {'class': 'bbWrapper'})
        text_content = bb_content.text
        return Post(self, post_id, creator, thread, create_date, bb_content, text_content)


    def get_profile_post(self, post_id) -> ProfilePost:
        """Найти сообщение профиля по ID"""

        content = BeautifulSoup(self.session.get(f"{MAIN_URL}/profile-posts/{post_id}").content, 'lxml')
        post = content.find('article', {'id': f'js-profilePost-{post_id}'})
        creator = self.get_member(int(post.find('a', {'class': 'username'})['data-user-id']))
        profile = self.get_member(int(content.find('span', {'class': 'username'})['data-user-id']))
        create_date = int(post.find('time')['data-time'])
        bb_content = post.find('div', {'class': 'bbWrapper'})
        text_content = bb_content.text

        return ProfilePost(self, post_id, creator, profile, create_date, bb_content, text_content)

    def get_forum_statistic(self) -> Statistic:
        """Получить статистику форума"""

        content = BeautifulSoup(self.session.get(MAIN_URL).content, 'lxml')
        threads_count = int(content.find('dl', {'class': 'pairs pairs--justified count--threads'}).find('dd').text.replace(',', ''))
        posts_count = int(content.find('dl', {'class': 'pairs pairs--justified count--messages'}).find('dd').text.replace(',', ''))
        users_count = int(content.find('dl', {'class': 'pairs pairs--justified count--users'}).find('dd').text.replace(',', ''))
        last_register_member = self.get_member(int(content.find('dl', {'class': 'pairs pairs--justified'}).find('a')['data-user-id']))

        return Statistic(self, threads_count, posts_count, users_count, last_register_member)
    

    # -------------================ МЕТОДЫ ОБЪЕКТОВ ====================--------------------


    # CATEGORY
    def create_thread(self, category_id: int, title: str, message_html: str, discussion_type: str = 'discussion', watch_thread: int = 1) -> Response:
        """Создать тему в категории"""
        # TODO: сделать возврат ID новой темы

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/forums/{category_id}/post-thread?inline-mode=1", {'_xfToken': token, 'title': title, 'message_html': message_html, 'discussion_type': discussion_type, 'watch_thread': watch_thread})
    

    def set_read_category(self, category_id: int) -> Response:
        """Отметить тему как прочитанную"""

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/forums/{category_id}/mark-read", {'_xfToken': token})
    

    def watch_category(self, category_id: int, notify: str, send_alert: bool = True, send_email: bool = False, stop: bool = False) -> Response:
        """Настроить отслеживание темы\n
        :param notify - Возможные варианты: "thread", "message", "" """

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']

        if stop: return self.session.post(f"{MAIN_URL}/forums/{category_id}/watch", {'_xfToken': token, 'stop': "1"})
        else: return self.session.post(f"{MAIN_URL}/forums/{category_id}/watch", {'_xfToken': token, 'send_alert': int(send_alert), 'send_email': int(send_email), 'notify': notify})


    def get_threads(self, category_id: int, page: int = 1) -> list:
        """Получить темы из раздела"""

        soup = BeautifulSoup(self.session.get(f"{MAIN_URL}/forums/{category_id}/page-{page}").content, "lxml")
        result = []
        for thread in soup.find_all('div', compile('structItem structItem--thread.*')):
            link = object
            for el in thread.find_all('div', "structItem-title")[0].find_all("a"): 
                if "threads" in el['href']: link = el

            result.append(int(findall(r'\d+', link['href'])[0]))
        
        return result


    def get_categories(self, category_id: int) -> list:
        """Получить дочерние категории из раздела"""

        soup = BeautifulSoup(self.session.get(f"{MAIN_URL}/forums/{category_id}").content, "lxml")
        result = []
        for category in soup.find_all('div', compile('.*node--depth2 node--forum.*')): 
            result.append(int(findall(r'\d+', category.find("a")['href'])[0]))
        
        return result
    
    # MEMBER
    def follow_member(self, member_id: int) -> Response:
        """Изменить статус подписки на пользователя"""

        if member_id == self.current_member.id: raise ThisIsYouError(member_id)

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/members/{member_id}/follow", {'_xfToken': token})
    

    def ignore_member(self, member_id: int) -> Response:
        """Изменить статус игнора пользователя"""

        if member_id == self.current_member.id: raise ThisIsYouError(member_id)

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/members/{member_id}/ignore", {'_xfToken': token})
    

    def add_profile_message(self, member_id: int, message_html: str) -> Response:
        """Отправить сообщение на стенку пользователя"""

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/members/{member_id}/post", {'_xfToken': token, 'message_html': message_html})
    

    def get_profile_messages(self, member_id: int, page: int = 1) -> list:
        """Возвращает ID всех сообщений со стенки пользователя"""

        soup = BeautifulSoup(self.session.get(f"{MAIN_URL}/members/{member_id}/page-{page}").content, "lxml")
        result = []
        for post in soup.find_all('article', {'id': compile('js-profilePost-*')}):
            result.append(int(post['id'].strip('js-profilePost-')))

        return result

    # POST
    def react_post(self, post_id: int, reaction_id: int) -> Response:
        """Поставить реакцию на пост"""

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f'{MAIN_URL}/posts/{post_id}/react?reaction_id={reaction_id}', {'_xfToken': token})
    

    def edit_post(self, post_id: int, html_message: str) -> Response:
        """Отредактировать пост"""

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/posts/{post_id}/edit", {"message_html": html_message, "message": html_message, "_xfToken": token})


    def delete_post(self, post_id: int, reason: str, hard_delete: int = 0) -> Response:
        """Удалить пост"""

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/posts/{post_id}/delete", {"reason": reason, "hard_delete": hard_delete, "_xfToken": token})
    

    # PROFILE POST
    def react_profile_post(self, post_id: int, reaction_id: int) -> Response:
        """Поставить реакцию на сообщение профиля"""

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f'{MAIN_URL}/profile-posts/{post_id}/react?reaction_id={reaction_id}', {'_xfToken': token})


    def comment_profile_post(self, post_id: int, message_html: str) -> Response:
        """Поставить комментарий на сообщение профиля"""

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/profile-posts/{post_id}/add-comment", {"message_html": message_html, "_xfToken": token})


    def delete_profile_post(self, post_id: int, reason: str, hard_delete: int = 0) -> Response:
        """Удалить сообщение профиля"""

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/profile-posts/{post_id}/delete", {"reason": reason, "hard_delete": hard_delete, "_xfToken": token})
    

    def edit_profile_post(self, post_id: int, html_message: str) -> Response:
        """Отредактировать сообщение профиля"""

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/profile-posts/{post_id}/edit", {"message_html": html_message, "message": html_message, "_xfToken": token})


    # THREAD
    def answer_thread(self, thread_id: int, html_message: str) -> Response:
        """Оставить ответ в теме"""

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/threads/{thread_id}/add-reply", {'_xfToken': token, 'message_html': html_message})


    def watch_thread(self, thread_id: int, stop: bool, email_subscribe: bool = False) -> Response:
        """Отслеживание темы"""

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/threads/{thread_id}/watch", {'_xfToken': token, 'stop': int(stop), 'email_subscribe': int(email_subscribe)})
    

    def delete_thread(self, thread_id: int, reason: str, hard_delete: int = 0) -> Response:
        """Удалить тему"""

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/threads/{thread_id}/delete", {"reason": reason, "hard_delete": hard_delete, "_xfToken": token})
    

    def edit_thread_info(self, thread_id: int, title: str = None, prefix_id: int = None) -> Response:
        """Изменить заголовок и префикс темы"""

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        data = {"_xfToken": token}

        if title is not None: data.update({'title': title})
        if prefix_id is not None: data.update({'prefix_id[]', prefix_id})

        return self.session.post(f"{MAIN_URL}/threads/{thread_id}/edit", data)
    

    def close_thread(self, thread_id: int) -> Response:
        """Закрыть тему (для модерации)"""

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/threads/{thread_id}/quick-close", {'_xfToken': token})


    def pin_thread(self, thread_id: int) -> Response:
        """Закрепить тему (для модерации)"""

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/threads/{thread_id}/quick-stick", {'_xfToken': token})
    

    def get_thread_posts(self, thread_id: int, page: int = 1) -> list:
        """Получить все посты из темы"""

        soup = BeautifulSoup(self.session.get(f"{MAIN_URL}/threads/{thread_id}/page-{page}").content, 'lxml')

        return_data = []
        for i in soup.find_all('article', {'id': compile('js-post-*')}):
            if i['id'].startswith('js-post-') == False: continue
            return_data.append(i['id'].strip('js-post-'))

        return return_data


    # OTHER
    def send_form(self, form_id: int, data: dict) -> str:
        """Заполнить форму"""

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        data.update({'_xfToken': token})
        response = self.session.post(f"{MAIN_URL}/form/{form_id}/submit", data)

        return response.text