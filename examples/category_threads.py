import arz_api

cookies = {"xf_user": "your",
           "xf_tfa_trust": "your",
           "xf_session": "your",
           "xf_csrf": "your"}

api = arz_api.ArizonaAPI(user_agent="your", cookie=cookies)

threads = api.get_threads(354)
print('Закрепленные темы:')
for i in threads["pins"]:
    thread = api.get_thread(i)
    print(f'{thread.title} by {thread.creator.username}')

print('\n____________________\nНезакрепленные темы:')
for i in threads["unpins"]:
    thread = api.get_thread(i)
    print(f'{thread.title} by {thread.creator.username}')
