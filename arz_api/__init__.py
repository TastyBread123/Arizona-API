from .api import *
from .consts import *
from .exceptions import *

"""
**Update v1.1**
- В объект пользователя (Member) был добавлен метод get_profile_messages(page: int), возвращает список из ID сообщений
- В объект поста (Post) были добавлены поля text_content - текст без html тегов
- Теперь методы объекта раздела (Category) get_threads(page) и get_categories() возвращают список (list) из ID
- Поправлены/добавлены комментарии
- Добавлен requirements.txt
- Добавлены новые примеры


**Update v1.2**
- Теперь из объекта ArizonaAPI можно вызвать большинство методов (пример)
- Теперь по умолчанию в get_posts() у объекта Thread стоит 1 страница
- Улучшен внешний вид документации
- Мелкие исправления, улучшения


**Update v1.3**
- Добавлен метод в объект темы (Thread) - edit_info(title: str, prefix_id: int). В ArizonaAPI - edit_thread_info(thread_id: int, title: str, prefix_id: int)
- Новый метод ArizonaAPI send_form(form_id: int, form_data: dict). Может быть использован для создания жалоб (пример)
- Мелкие исправления, улучшения

**Update v1.3.1**
- Исправлена ошибка с методом get_post

**Update v1.4**
- Теперь методы с действиями, которые раньше возвращали True или None, теперь возвращает объект Response, откуда можно узнать код ответа и тд
- В объект Thread (тема) добавлено поле prefix (префикс темы)
- В объект Member (пользователь) добавлен метод ignore() - ignore_member(member_id: int) в ArizonaAPI

**Update v1.5**
- Изменена механика работы get_threads. Теперь функция возвращает словарь (dict) с ключами 'pins' и 'unpins' - списки (list) закрепленных и незакрепленных тем соответственно. Пример (link)
- Теперь member.avatar возвращает полную ссылку на аватарку
- Уборка в сортире репозитория

**Update v1.6**
- Добавлены более подробные комментарии ко всем методам
- Новые методы в ArizonaAPI, react_thread(thread_id: int, reaction_id: int) - поставить реакцию на тему, edit_thread(thread_id: int, message_html: str) - изменить содержимое темы
- Добавлены новые методы в объект CurrentMember - edit_avatar(upload_photo: str) - изменить автарку, delete_avatar() - удалить аватарку (спасибо https://www.blast.hk/members/502833 за функцию, а то я бы и не вспомнил :D)
- Теперь в методах react всех обхектов по умолчанию ставится реакция 1 id
- В некоторых методах изменен рекомендуемый тип данных с int на bool. Подробнее в документации
- Незначительные изменения
"""