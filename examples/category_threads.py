import arz_api

cookies = {"xf_user": "your",
           "xf_tfa_trust": "your",
           "xf_session": "your",
           "xf_csrf": "your"}

api = arz_api.ArizonaAPI(user_agent="your", cookie=cookies)

for thread_id in api.get_threads(1583):
    thread = api.get_thread(thread_id)
    print(f"{thread.title} by {thread.creator.username}")