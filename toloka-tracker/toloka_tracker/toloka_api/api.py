import requests
import json

from toloka_tracker.toloka_api.common import get_toloka_token
from toloka_tracker.toloka_api.models import PoolStatus, TolokaProject, TolokaPool, UnreadInboxMessagesThread


def simple_toloka_get_request(url):
    resp = requests.get(url,
                        timeout=7200.0,
                        headers={'Content-Type': 'application/json',
                                 'Authorization': f'OAuth {get_toloka_token()}'})

    return resp.json()


def parse_projects(projects):
    return [TolokaProject.from_json(project_json) for project_json in projects]


def parse_pools(pools):
    return [TolokaPool.from_json(pools_json) for pools_json in pools]


def list_projects():
    url = f'https://toloka.yandex.ru/api/v1/projects?status=ACTIVE&limit=300&sort=id'
    projects = simple_toloka_get_request(url)['items']

    return parse_projects(projects)


def get_pool_tasks(pool_id):
    url = f'https://toloka.yandex.com/api/v1/assignments?pool_id={pool_id}&status=ACCEPTED,REJECTED&limit=10000'

    return simple_toloka_get_request(url)['items']


def count_pool_stats(pool_id):
    tasks = get_pool_tasks(pool_id)
    return len(list(filter(lambda t: t['status'] == "ACCEPTED", tasks))), \
           len(list(filter(lambda t: t['status'] == "REJECTED", tasks)))


def get_pools(project_id, status: PoolStatus):
    url = f'https://toloka.yandex.com/api/v1/pools?project_id={project_id}&status={status.value}'

    return parse_pools(simple_toloka_get_request(url)['items'])


def get_all_messages():
    resp = requests.get(f'https://toloka.yandex.ru/api/v1/message-threads?folder=UNREAD,INBOX&sort=-created&limit=300',
                        timeout=7200.0,
                        headers={'Content-Type': 'application/json',
                                 'Authorization': f'OAuth {get_toloka_token()}'})

    resp_string = resp.content.decode('utf-8')

    response_json = json.loads(resp_string)

    result_messages = list(map(lambda item: UnreadInboxMessagesThread.from_dict(item), response_json['items']))

    return result_messages, response_json['has_more']


def number_of_unread_messages(project_id):
    resp = requests.get(f'https://toloka.yandex.ru/api/v1/message-threads?folder=UNREAD,INBOX&sort=-created&limit=300',
                        timeout=7200.0,
                        headers={'Content-Type': 'application/json',
                                 'Authorization': f'OAuth {get_toloka_token()}'})
    resp_string = resp.content.decode('utf-8')

    response_json = json.loads(resp_string)

    if project_id == "OTHER":
        all_ids = []
        all_names = []

        projects_list = list_projects()
        for project_description in projects_list:
            all_ids.append(str(project_description["id"]).lower())
            all_names.append(project_description["public_name"].lower())

        return len(list(response_json['items']))


    elif project_id is not None:
        projects_list = list_projects()
        for project_description in projects_list:
            if project_description["id"] == project_id:
                project_name = project_description["public_name"]

        return len(list(response_json['items']))

    return len(response_json['items'])


def has_unread_messages():
    return number_of_unread_messages() > 0


def mark_message_as(message_id, folder):
    requests.post(f'https://toloka.yandex.ru/api/v1/message-threads/{message_id}/add-to-folders',
                  timeout=7200.0,
                  headers={'Content-Type': 'application/json',
                           'Authorization': f'OAuth {get_toloka_token()}'},
                  json={"folders": [folder]})


def mark_as_read(message_id):
    requests.post(f'https://toloka.yandex.ru/api/v1/message-threads/{message_id}/remove-from-folders',
                  timeout=7200.0,
                  headers={'Content-Type': 'application/json',
                           'Authorization': f'OAuth {get_toloka_token()}'},
                  json={"folders": ["UNREAD"]})


def accept(assignment_id, comment):
    resp = requests.patch(f'https://toloka.yandex.ru/api/v1/assignments/{assignment_id}',
                          timeout=7200.0,
                          headers={'Content-Type': 'application/json',
                                   'Authorization': f'OAuth {get_toloka_token()}'},
                          json={"status": "ACCEPTED", "public_comment": f'{comment}'})


def get_task_info(assignment_id):
    resp = requests.get(f'https://toloka.yandex.ru/api/v1/tasks/{assignment_id}',
                        timeout=7200.0,
                        headers={'Content-Type': 'application/json',
                                 'Authorization': f'OAuth {get_toloka_token()}'})

    return json.loads(resp.content.decode('utf-8'))


def get_assignment_info(assignment_id):
    resp = requests.get(f'https://toloka.yandex.ru/api/v1/assignments/{assignment_id}',
                        timeout=7200.0,
                        headers={'Content-Type': 'application/json',
                                 'Authorization': f'OAuth {get_toloka_token()}'})

    return resp.json()


def reply_text(messages_thread_id, lang_code: str, comment):

    resp = requests.post(f'https://toloka.yandex.ru/api/v1/message-threads/{messages_thread_id}/reply',
                         timeout=7200.0,
                         headers={'Content-Type': 'application/json',
                                  'Authorization': f'OAuth {get_toloka_token()}'},
                         json={"text": {lang_code.upper(): comment}})

    return resp.json()
