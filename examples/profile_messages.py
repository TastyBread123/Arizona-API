import arz_api

cookies = {"xf_user": "your",
           "xf_tfa_trust": "your",
           "xf_session": "your",
           "xf_csrf": "your"}

try: 
    api = arz_api.ArizonaAPI(user_agent="your", cookie=cookies)
    print('Success login! Getting last posts in your profile...')

    for post_id in api.current_member.get_profile_messages():
        post = api.get_profile_post(post_id)
        print("\nMessage ID: {0}\nFrom: {1}\nText: {2}\nUnformatted text: {3}".format(post.creator.id, post.creator.username, post.text_content, post.bb_content))

except arz_api.IncorrectLoginData: print('Invalid login data!')