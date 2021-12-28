import os
import re


def get_toloka_token():
    return os.environ.get("TOLOKA_TOKEN")


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, ' ', raw_html)
    return cleantext


class AppealMeta:
    def __init__(self, pool_id, project_id, assignment_id):
        self.pool_id = pool_id
        self.project_id = project_id
        self.assignment_id = assignment_id

    def __str__(self):
        return "\n".join([
            f'*Project id:* ```{self.project_id}```',
            f'*Pool id:* ```{self.pool_id}```',
            f'*Assignment id:* ```{self.assignment_id}```'
        ])

    def raw_text(self):
        return "\n".join([
            f'Project id: {self.project_id}',
            f'Pool id: {self.pool_id}',
            f'Assignment id: {self.assignment_id}'
        ])


def extract_topic(items_dict):
    topic_dictionary: dict = items_dict.get('topic')
    if topic_dictionary is None:
        return "Unknown topic"

    topic_keys = list(topic_dictionary.keys())

    if len(topic_keys) < 1:
        return "Unknown topic"

    # RU is primary
    if 'RU' in topic_keys:
        return topic_dictionary['RU']

    return topic_dictionary[topic_keys[0]]


def extract_text(texts_dict):
    if texts_dict is None:
        return "<unknown text>"

    texts_keys = list(texts_dict.keys())

    if len(texts_keys) < 1:
        return "<unknown text>"

    # RU is primary
    if 'RU' in texts_keys:
        return texts_dict['RU']

    return texts_dict[texts_keys[0]]


def extract_meta(items_dict):
    meta = items_dict.get('meta')
    if meta is None:
        return None

    return AppealMeta(
        meta.get('pool_id'),
        meta.get('project_id'),
        meta.get('assignment_id')
    )


def extract_messages(items_dict):
    meta = items_dict.get('meta')
    if meta is None:
        return None

    return AppealMeta(
        meta.get('pool_id'),
        meta.get('project_id'),
        meta.get('assignment_id')
    )