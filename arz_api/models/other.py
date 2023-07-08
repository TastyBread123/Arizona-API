from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arz_api import ArizonaAPI
    from arz_api.models.member_object import Member


class Statistic:
    def __init__(self, API: 'ArizonaAPI', threads_count: int, posts_count: int, users_count: int, last_register_member: 'Member') -> None:
        self.API = API
        self.threads_count = threads_count
        self.posts_count = posts_count
        self.users_count = users_count
        self.last_register_member = last_register_member
