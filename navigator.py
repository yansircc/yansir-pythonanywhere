from functools import wraps
from flask import g


def get_navigator_items():
    return [
        {'route': 'index.index', 'text': '首页'},
        # {'route': 'builder.builder', 'text': '建站'},
        # {'route': 'paid_chat.paid_chat', 'text': '对话'},
        {'route': 'business.business', 'text': '生意'},
        # {'route': 'post_ideas.post_ideas', 'text': '标题'},
        # {'route': 'generate_post.generate_post', 'text': '文章'},
        {'route': 'gtm_json.gtm_json', 'text': 'GTM'},
        {'route': 'anki_cards.anki_cards', 'text': 'Anki'},
        # {'route': 'serp_titles.serp_titles', 'text': 'SERP'},
    ]


def navigator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        g.navigator_items = get_navigator_items()
        return f(*args, **kwargs)
    return decorated_function
