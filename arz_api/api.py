from requests import session
from bs4 import BeautifulSoup
from re import compile

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

    
    def logout(self) -> None:
        self.session.close()

    
    @property
    def current_member(self) -> CurrentMember:
        """Объект текущего пользователя"""

        content = BeautifulSoup(self.session.get(f"{MAIN_URL}/account").content, 'lxml')
        user_id = int(content.find('span', {'class': 'avatar avatar--xxs'})['data-user-id'])
        member_info = self.get_member(user_id)

        return CurrentMember(self, user_id, member_info.username, member_info.user_title, member_info.avatar, member_info.messages_count, member_info.reactions_count, member_info.trophies_count)

    
    def get_category(self, category_id: int) -> Category | None:
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
    
    
    def get_member(self, user_id: int) -> Member | None:
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

    
    def get_thread(self, thread_id: int | str) -> Thread | None:
        content = BeautifulSoup(self.session.get(f"{MAIN_URL}/threads/{thread_id}/page-1").content, 'lxml')
        try: creator = self.get_member(int(content.find('a', {'class': 'username'})['data-user-id']))
        except: creator = Member(self, int(content.find('a', {'class': 'username'})['data-user-id']), content.find('a', {'class': 'username'}).text, None, None, None, None, None)
        category = self.get_category(int(content.find('html')['data-container-key'].strip('node-')))
        create_date = int(content.find('time')['data-time'])
        title = content.find('h1', {'class': 'p-title-value'}).text
        thread_content_html = content.find('div', {'class': 'bbWrapper'})
        thread_content = thread_content_html.text
        try: pages_count = int(content.find_all('li', {'class': 'pageNav-page'})[-1].text)
        except IndexError: pages_count = 1
        is_closed = False
        if content.find('dl', {'class': 'blockStatus'}): is_closed = True
        thread_post_id = content.find('article', {'id': compile('js-post-*')})['id'].strip('js-post-')

        return Thread(self, thread_id, creator, category, create_date, title, thread_content, thread_content_html, pages_count, thread_post_id, is_closed)
    

    def get_post(self, post_id: int) -> Post | None:
        content = BeautifulSoup(self.session.get(f"{MAIN_URL}/posts/{post_id}").content, 'lxml')
        post = content.find('article', {'id': f'js-post-{post_id}'})
        try: creator = self.get_member(int(post.find('a', {'data-xf-init': 'member-tooltip'})['data-user-id']))
        except:
            user_info = post.find('a', {'data-xf-init': 'member-tooltip'})
            creator = Member(self, int(user_info['data-user-id']), user_info.text, None, None, None, None, None)

        thread = self.get_thread(int(content.find('html')['data-content-key'].strip('thread-')))
        create_date = int(post.find('time', {'class': 'u-dt'})['data-time'])
        bb_content = post.find('div', {'class': 'bbWrapper'})
        
        return Post(self, post_id, creator, thread, create_date, bb_content)


    def get_profile_post(self, post_id) -> ProfilePost | None:
        content = BeautifulSoup(self.session.get(f"{MAIN_URL}/profile-posts/{post_id}").content, 'lxml')
        post = content.find('article', {'id': f'js-profilePost-{post_id}'})
        creator = self.get_member(int(post.find('a', {'class': 'username'})['data-user-id']))
        bb_content = post.find('div', {'class': 'bbWrapper'})
        create_date = int(post.find('time')['data-time'])
        profile = self.get_member(int(content.find('span', {'class': 'username'})['data-user-id']))

        return ProfilePost(self, post_id, creator, profile, create_date, bb_content)

    def get_forum_statistic(self) -> Statistic:
        content = BeautifulSoup(self.session.get(MAIN_URL).content, 'lxml')
        threads_count = int(content.find('dl', {'class': 'pairs pairs--justified count--threads'}).find('dd').text.replace(',', ''))
        posts_count = int(content.find('dl', {'class': 'pairs pairs--justified count--messages'}).find('dd').text.replace(',', ''))
        users_count = int(content.find('dl', {'class': 'pairs pairs--justified count--users'}).find('dd').text.replace(',', ''))
        last_register_member = self.get_member(int(content.find('dl', {'class': 'pairs pairs--justified'}).find('a')['data-user-id']))

        return Statistic(self, threads_count, posts_count, users_count, last_register_member)
