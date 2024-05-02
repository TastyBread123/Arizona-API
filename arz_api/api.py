from bs4 import BeautifulSoup
from re import compile, findall
from requests import session, Response

from arz_api.consts import MAIN_URL
from arz_api.bypass_antibot import bypass

from arz_api.exceptions import IncorrectLoginData, ThisIsYouError
from arz_api.models.other import Statistic
from arz_api.models.post_object import Post, ProfilePost
from arz_api.models.member_object import Member, CurrentMember
from arz_api.models.thread_object import Thread
from arz_api.models.category_object import Category



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
        user_id = int(content.find('span', {'class': 'avatar--xxs'})['data-user-id'])
        member_info = self.get_member(user_id)

        return CurrentMember(self, user_id, member_info.username, member_info.user_title, member_info.avatar, member_info.roles, member_info.messages_count, member_info.reactions_count, member_info.trophies_count)

    
    def get_category(self, category_id: int) -> Category:
        """Найти раздел по ID"""

        content = BeautifulSoup(self.session.get(f"{MAIN_URL}/forums/{category_id}").content, 'lxml')
        title = content.find('h1', {'class': 'p-title-value'}).text
        if "Упс! Мы столкнулись с некоторыми проблемами." in title:
            return None

        try: pages_count = int(content.find_all('li', {'class': 'pageNav-page'})[-1].text)
        except IndexError: pages_count = 1
        try: parent_category_id = int(content.find('html')['data-container-key'].strip('node-'))
        except: parent_category_id = None

        temp_url = ''
        if parent_category_id is not None: temp_url = f'forums/{parent_category_id}/'
        content = BeautifulSoup(self.session.get(f"{MAIN_URL}/{temp_url}").content, 'lxml')
        
        return Category(self, category_id, title, pages_count, parent_category_id)
    
    
    def get_member(self, user_id: int) -> Member:
        """Найти пользователя по ID (возвращает либо Member, либо None (если профиль закрыт / не существует))"""

        content = BeautifulSoup(self.session.get(f"{MAIN_URL}/members/{user_id}").content, 'lxml')

        username = content.find('span', {'class': 'username'})
        if username is None:
            return None
        username = username.text

        roles = []
        for i in content.find('div', {'class': 'memberHeader-banners'}).children:
            if i.text != '\n': roles.append(i.text)

        try: user_title = content.find('span', {'class': 'userTitle'}).text
        except AttributeError: user_title = None
        try: avatar = MAIN_URL + content.find('a', {'class': 'avatar avatar--l'})['href']
        except TypeError: avatar = None

        messages_count = int(content.find('a', {'href': f'/search/member?user_id={user_id}'}).text.strip().replace(',', ''))
        reactions_count = int(content.find('dl', {'class': 'pairs pairs--rows pairs--rows--centered'}).find('dd').text.strip().replace(',', ''))
        trophies_count = int(content.find('a', {'href': f'/members/{user_id}/trophies'}).text.strip().replace(',', ''))
        
        return Member(self, user_id, username, user_title, avatar, roles, messages_count, reactions_count, trophies_count)

    
    def get_thread(self, thread_id: int) -> Thread:
        """Найти тему по ID (Thread если тема существует, None если недоступна / не существует)"""

        content = BeautifulSoup(self.session.get(f"{MAIN_URL}/threads/{thread_id}/page-1").content, 'lxml')
        
        creator_id = content.find('a', {'class': 'username'})
        if creator_id is None:
            return None

        try: creator = self.get_member(int(creator_id['data-user-id']))
        except: creator = Member(self, int(creator_id['data-user-id']), content.find('a', {'class': 'username'}).text, None, None, None, None, None, None)
        
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
        """Найти пост по ID (Post если существует, None - удален / нет доступа)"""

        content = BeautifulSoup(self.session.get(f"{MAIN_URL}/posts/{post_id}").content, 'lxml')
        post = content.find('article', {'id': f'js-post-{post_id}'})
        if post is None:
            return None

        try: creator = self.get_member(int(post.find('a', {'data-xf-init': 'member-tooltip'})['data-user-id']))
        except:
            user_info = post.find('a', {'data-xf-init': 'member-tooltip'})
            creator = Member(self, int(user_info['data-user-id']), user_info.text, None, None, None, None, None, None)

        thread = self.get_thread(int(content.find('html')['data-content-key'].strip('thread-')))
        create_date = int(post.find('time', {'class': 'u-dt'})['data-time'])
        bb_content = post.find('div', {'class': 'bbWrapper'})
        text_content = bb_content.text
        return Post(self, post_id, creator, thread, create_date, bb_content, text_content)


    def get_profile_post(self, post_id: int) -> ProfilePost:
        """Найти сообщение профиля по ID"""

        content = BeautifulSoup(self.session.get(f"{MAIN_URL}/profile-posts/{post_id}").content, 'lxml')
        post = content.find('article', {'id': f'js-profilePost-{post_id}'})
        if post is None:
            return None

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
    

    # ---------------================ МЕТОДЫ ОБЪЕКТОВ ====================--------------------


    # CATEGORY
    def create_thread(self, category_id: int, title: str, message_html: str, discussion_type: str = 'discussion', watch_thread: bool = True) -> Response:
        """Создать тему в категории

        Attributes:
            category_id (int): ID категории
            title (str): Название темы
            message_html (str): Содержание темы. Рекомендуется использование HTML
            discussion_type (str): - Тип темы | Возможные варианты: 'discussion' - обсуждение (по умолчанию), 'article' - статья, 'poll' - опрос (необяз.)
            watch_thread (str): - Отслеживать ли тему. По умолчанию True (необяз.)
        
        Returns:
            Объект Response модуля requests

        Todo:
            Cделать возврат ID новой темы
        """

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/forums/{category_id}/post-thread?inline-mode=1", {'_xfToken': token, 'title': title, 'message_html': message_html, 'discussion_type': discussion_type, 'watch_thread': int(watch_thread)})
    

    def set_read_category(self, category_id: int) -> Response:
        """Отметить категорию как прочитанную

        Attributes:
            category_id (int): ID категории
        
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/forums/{category_id}/mark-read", {'_xfToken': token})
    

    def watch_category(self, category_id: int, notify: str, send_alert: bool = True, send_email: bool = False, stop: bool = False) -> Response:
        """Настроить отслеживание категории

        Attributes:
            category_id (int): ID категории
            notify (str): Объект отслеживания. Возможные варианты: "thread", "message", ""
            send_alert (bool): - Отправлять ли уведомления на форуме. По умолчанию True (необяз.)
            send_email (bool): - Отправлять ли уведомления на почту. По умолчанию False (необяз.)
            stop (bool): - Принудительное завершение отслеживания. По умолчанию False (необяз.)

        Returns:
            Объект Response модуля requests    
        """

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']

        if stop: return self.session.post(f"{MAIN_URL}/forums/{category_id}/watch", {'_xfToken': token, 'stop': "1"})
        else: return self.session.post(f"{MAIN_URL}/forums/{category_id}/watch", {'_xfToken': token, 'send_alert': int(send_alert), 'send_email': int(send_email), 'notify': notify})


    def get_threads(self, category_id: int, page: int = 1) -> dict:
        """Получить темы из раздела

        Attributes:
            category_id (int): ID категории
            page (int): Cтраница для поиска. По умолчанию 1 (необяз.)
            
        Returns:
            Словарь (dict), состоящий из списков закрепленных ('pins') и незакрепленных ('unpins') тем
        """

        soup = BeautifulSoup(self.session.get(f"{MAIN_URL}/forums/{category_id}/page-{page}").content, "lxml")
        result = {'pins': [], 'unpins': []}
        for thread in soup.find_all('div', compile('structItem structItem--thread.*')):
            link = thread.find_all('div', "structItem-title")[0].find_all("a")[-1]
            if len(findall(r'\d+', link['href'])) < 1: continue

            if len(thread.find_all('i', {'title': 'Закреплено'})) > 0: result['pins'].append(int(findall(r'\d+', link['href'])[0]))
            else: result['unpins'].append(int(findall(r'\d+', link['href'])[0]))
        
        return result


    def get_categories(self, category_id: int) -> list:
        """Получить дочерние категории из раздела
        
        Attributes:
            category_id (int): ID категории
        
        Returns:
            Список (list), состоящий из ID дочерних категорий раздела
        """

        soup = BeautifulSoup(self.session.get(f"{MAIN_URL}/forums/{category_id}").content, "lxml")
        return [int(findall(r'\d+', category.find("a")['href'])[0]) for category in soup.find_all('div', compile('.*node--depth2 node--forum.*'))]
    

    # MEMBER
    def follow_member(self, member_id: int) -> Response:
        """Изменить статус подписки на пользователя
        
        Attributes:
            member_id (int): ID пользователя
        
        Returns:
            Объект Response модуля requests
        """

        if member_id == self.current_member.id: raise ThisIsYouError(member_id)

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/members/{member_id}/follow", {'_xfToken': token})
    

    def ignore_member(self, member_id: int) -> Response:
        """Изменить статус игнорирования пользователя

        Attributes:
            member_id (int): ID пользователя
        
        Returns:
            Объект Response модуля requests
        """

        if member_id == self.current_member.id: raise ThisIsYouError(member_id)

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/members/{member_id}/ignore", {'_xfToken': token})
    

    def add_profile_message(self, member_id: int, message_html: str) -> Response:
        """Отправить сообщение на стенку пользователя

        Attributes:
            member_id (int): ID пользователя
            message_html (str): Текст сообщения. Рекомендуется использование HTML
            
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/members/{member_id}/post", {'_xfToken': token, 'message_html': message_html})
    

    def get_profile_messages(self, member_id: int, page: int = 1) -> list:
        """Возвращает ID всех сообщений со стенки пользователя на странице

        Attributes:
            member_id (int): ID пользователя
            page (int): Страница для поиска. По умолчанию 1 (необяз.)
            
        Returns:
            Cписок (list) с ID всех сообщений профиля
        """

        soup = BeautifulSoup(self.session.get(f"{MAIN_URL}/members/{member_id}/page-{page}").content, "lxml")
        return [int(post['id'].strip('js-profilePost-')) for post in soup.find_all('article', {'id': compile('js-profilePost-*')})]


    # POST
    def react_post(self, post_id: int, reaction_id: int = 1) -> Response:
        """Поставить реакцию на сообщение

        Attributes:
            post_id (int): ID сообщения
            reaction_id (int): ID реакции. По умолчанию 1 (необяз.)
            
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f'{MAIN_URL}/posts/{post_id}/react?reaction_id={reaction_id}', {'_xfToken': token})
    

    def edit_post(self, post_id: int, message_html: str) -> Response:
        """Отредактировать сообщение

        Attributes:
            post_id (int): ID сообщения
            message_html (str): Новый текст сообщения. Рекомендуется использование HTML
            
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/posts/{post_id}/edit", {"message_html": message_html, "message": message_html, "_xfToken": token})


    def delete_post(self, post_id: int, reason: str, hard_delete: bool = False) -> Response:
        """Удалить сообщение

        Attributes:
            post_id (int): ID сообщения
            reason (str): Причина для удаления
            hard_delete (bool): Полное удаление сообщения. По умолчанию False (необяз.)
        
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/posts/{post_id}/delete", {"reason": reason, "hard_delete": int(hard_delete), "_xfToken": token})
    

    def bookmark_post(self, post_id: int) -> Response:
        """Добавить сообщение в закладки

        Attributes:
            post_id (int): ID сообщения
        
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/posts/{post_id}/bookmark", {"_xfToken": token})


    # PROFILE POST
    def react_profile_post(self, post_id: int, reaction_id: int = 1) -> Response:
        """Поставить реакцию на сообщение профиля

        Attributes:
            post_id (int): ID сообщения профиля
            reaction_id (int): ID реакции. По умолчанию 1 (необяз.)
            
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f'{MAIN_URL}/profile-posts/{post_id}/react?reaction_id={reaction_id}', {'_xfToken': token})


    def comment_profile_post(self, post_id: int, message_html: str) -> Response:
        """Прокомментировать сообщение профиля

        Attributes:
            post_id (int): ID сообщения
            message_html (str): Текст комментария. Рекомендуется использование HTML
            
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/profile-posts/{post_id}/add-comment", {"message_html": message_html, "_xfToken": token})


    def delete_profile_post(self, post_id: int, reason: str, hard_delete: bool = False) -> Response:
        """Удалить сообщение профиля

        Attributes:
            post_id (int): ID сообщения профиля
            reason (str): Причина для удаления
            hard_delete (bool): Полное удаление сообщения. По умолчанию False (необяз.)
        
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/profile-posts/{post_id}/delete", {"reason": reason, "hard_delete": int(hard_delete), "_xfToken": token})
    

    def edit_profile_post(self, post_id: int, message_html: str) -> Response:
        """Отредактировать сообщение профиля
        
        Attributes:
            post_id (int): ID сообщения
            message_html (str): Новый текст сообщения. Рекомендуется использование HTML
            
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/profile-posts/{post_id}/edit", {"message_html": message_html, "message": message_html, "_xfToken": token})


    # THREAD
    def close_thread(self, thread_id: int) -> Response:
        """Закрыть/открыть тему (для модерации)
        
        Attributes:
            thread_id (int): ID темы
        
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/threads/{thread_id}/quick-close", {'_xfToken': token})


    def pin_thread(self, thread_id: int) -> Response:
        """Закрепить/открепить тему (для модерации)
        
        Attributes:
            thread_id (int): ID темы
        
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/threads/{thread_id}/quick-stick", {'_xfToken': token})
    

    def answer_thread(self, thread_id: int, message_html: str) -> Response:
        """Оставить сообщенме в теме

        Attributes:
            thread_id (int): ID темы
            message_html (str): Текст сообщения. Рекомендуется использование HTML
            
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/threads/{thread_id}/add-reply", {'_xfToken': token, 'message_html': message_html})


    def watch_thread(self, thread_id: int, email_subscribe: bool = False, stop: bool = False) -> Response:
        """Изменить статус отслеживания темы

        Attributes:
            thread_id (int): ID темы
            email_subscribe (bool): Отправлять ли уведомления на почту. По умолчанию False (необяз.)
            stop (bool): - Принудительно прекратить отслеживание. По умолчанию False (необяз.)
        
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/threads/{thread_id}/watch", {'_xfToken': token, 'stop': int(stop), 'email_subscribe': int(email_subscribe)})
    

    def delete_thread(self, thread_id: int, reason: str, hard_delete: bool = False) -> Response:
        """Удалить тему

        Attributes:
            thread_id (int): ID темы
            reason (str): Причина для удаления
            hard_delete (bool): Полное удаление сообщения. По умолчанию False (необяз.)
            
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        return self.session.post(f"{MAIN_URL}/threads/{thread_id}/delete", {"reason": reason, "hard_delete": int(hard_delete), "_xfToken": token})
    

    def edit_thread(self, thread_id: int, message_html: str) -> Response:
        """Отредактировать содержимое темы

        Attributes:
            thread_id (int): ID темы
            message_html (str): Новое содержимое ответа. Рекомендуется использование HTML
        
        Returns:
            Объект Response модуля requests
        """

        content = BeautifulSoup(self.session.get(f"{MAIN_URL}/threads/{thread_id}/page-1").content, 'lxml')
        token = content.find('html')['data-csrf']
        thread_post_id = content.find('article', {'id': compile('js-post-*')})['id'].strip('js-post-')
        return self.session.post(f"{MAIN_URL}/posts/{thread_post_id}/edit", {"message_html": message_html, "message": message_html, "_xfToken": token})
    

    def edit_thread_info(self, thread_id: int, title: str = None, prefix_id: int = None, sticky: bool = True, opened: bool = True) -> Response:
        """Изменить заголовок и/или префикс темы

        Attributes:
            thread_id (int): ID темы
            title (str): Новое название
            prefix_id (int): Новый ID префикса
            sticky (bool): Закрепить (True - закреп / False - не закреп)
            opened (bool): Открыть/закрыть тему (True - открыть / False - закрыть)
        
        Returns:
            Объект Response модуля requests
        """
        
        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        data = {"_xfToken": token, "sticky": sticky, "discussion_open": opened}

        if title is not None: data.update({'title': title})
        if prefix_id is not None: data.update({'prefix_id[]': prefix_id})

        return self.session.post(f"{MAIN_URL}/threads/{thread_id}/edit", data)
    

    def get_thread_posts(self, thread_id: int, page: int = 1) -> list:
        """Получить все сообщения из темы на странице
        
        Attributes:
            thread_id (int): ID темы
            page (int): Cтраница для поиска. По умолчанию 1 (необяз.)
        
        Returns:
            Список (list), состоящий из ID всех сообщений на странице
        """

        soup = BeautifulSoup(self.session.get(f"{MAIN_URL}/threads/{thread_id}/page-{page}").content, 'lxml')
        return [i['id'].strip('js-post-') for i in soup.find_all('article', {'id': compile('js-post-*')})]
    

    def react_thread(self, thread_id: int, reaction_id: int = 1) -> Response:
        """Поставить реакцию на тему

        Attributes:
            thread_id (int): ID темы
            reaction_id (int): ID реакции. По умолчанию 1 (необяз.)
            
        Returns:
            Объект Response модуля requests
        """

        content = BeautifulSoup(self.session.get(f"{MAIN_URL}/threads/{thread_id}/page-1").content, 'lxml')
        token = content.find('html')['data-csrf']
        thread_post_id = content.find('article', {'id': compile('js-post-*')})['id'].strip('js-post-')
        return self.session.post(f'{MAIN_URL}/posts/{thread_post_id}/react?reaction_id={reaction_id}', {'_xfToken': token})


    # OTHER
    def send_form(self, form_id: int, data: dict) -> Response:
        """Заполнить форму

        Attributes:
            form_id (int): ID формы
            data (dict): Информация для запонения в виде словаря. Форма словаря: {'question[id вопроса]' = 'необходимая информация'} | Пример: {'question[531]' = '1'}
        
        Returns:
            Объект Response модуля requests
        """

        token = BeautifulSoup(self.session.get(f"{MAIN_URL}/help/terms/").content, 'lxml').find('html')['data-csrf']
        data.update({'_xfToken': token})
        response = self.session.post(f"{MAIN_URL}/form/{form_id}/submit", data)

        return response