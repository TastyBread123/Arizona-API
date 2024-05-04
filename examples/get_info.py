import arz_api


cookies = {"xf_user": "your",
           "xf_tfa_trust": "your",
           "xf_session": "your"}

api = arz_api.ArizonaAPI(user_agent="your", cookie=cookies)

user = api.current_member
print(f'Успешно авторизовались!\nИмя пользователя: {user.username} | Звание: {user.user_title}\nАватарка: {user.avatar}\nСообщений: {user.messages_count} | Реакций: {user.reactions_count}\n')

category = api.get_category(1865)
print(f"Название: {category.title} ({category.id})\nСтраниц: {category.pages_count}\n")

member = api.get_member(583439)
print(f'Пользователь найден!\nИмя пользователя: {member.username} | Звание: {member.user_title}\nАватарка: {member.avatar}\nСообщений: {member.messages_count} | Реакций: {member.reactions_count} | Баллов: {member.trophies_count}\n')

thread = api.get_thread(6594323)
print(f'Название: {thread.title} ({thread.id})\nАвтор темы: {thread.creator.username}\nКатегория: {thread.category.title} ({thread.category.id})\nДата создания: {thread.create_date} | Закрыто: {thread.is_closed}')

statistic = api.get_forum_statistic()
print(f'\n\nТем: {statistic.threads_count} | Постов: {statistic.posts_count} | Пользователей: {statistic.users_count}\nПоследний пользователь: {statistic.last_register_member.username}')

post = api.get_post(36550558)
print(f'\n\nАвтор: {post.creator.username}({post.creator.id})\nID: {post.id} | Дата создания: {post.create_date}\nРазмещено в теме {post.thread.title}\n\n{post.bb_content}')

profile_post = api.get_profile_post(2247012)
print(f"\n\nАвтор: {profile_post.creator.username} ({profile_post.creator.id})\nСоздано в {profile_post.create_date} у пользователя {profile_post.profile.username} ({profile_post.profile.id})\n\n{profile_post.bb_content}")
