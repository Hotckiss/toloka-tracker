import io
from datetime import datetime
import urllib.request
from enum import Enum

import pydub
import requests
from telegram.ext import CallbackContext

from toloka_tracker.toloka_api.common import extract_text, get_toloka_token, extract_topic, extract_meta, cleanhtml


class TolokaProject:
    id: str
    name: str

    def __init__(self, id, name):
        self.id = id
        self.name = name

    @staticmethod
    def from_json(json_dict):
        return TolokaProject(json_dict['id'], json_dict['public_name'])


class TolokaPool:
    id: str
    project_id: str
    status: str

    def __init__(self, id, project_id, status):
        self.id = id
        self.project_id = project_id
        self.status = status

    @staticmethod
    def from_json(json_dict):
        return TolokaPool(json_dict['id'], json_dict['project_id'], PoolStatus[json_dict['status']])


class PoolStatus(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    LOCKED = "LOCKED"
    ARCHIVED = "ARCHIVED"


class UserInfo:
    def __init__(self, user_id, user_role, is_me):
        self.user_id = user_id
        self.user_role = user_role
        self.is_me = is_me

    def is_toloker(self):
        return self.user_role == "USER"

    def __str__(self):
        return f'*User id:* {self.user_id}'

    def raw_text(self):
        return f'User id: {self.user_id}'


class TolokaMessage:
    def __init__(self, text, user_info, timestamp_string):
        try:
            self.text = cleanhtml(text)
        except:
            self.text = text
        self.user_info = user_info
        try:
            self.timestamp = datetime.strptime(timestamp_string, '%Y-%m-%dT%H:%M:%S.%f')
        except:
            self.timestamp = datetime.strptime(timestamp_string, '%Y-%m-%dT%H:%M:%S')

    @staticmethod
    def from_dictionary(dict_info):
        return TolokaMessage(
            extract_text(dict_info.get('text')),
            UserInfo(
                dict_info['from']['id'],
                dict_info['from']['role'],
                dict_info['from'].get('myself') is not None
            ),
            dict_info['created']
        )

    def to_dictionary(self):
        result = {}
        ts = self.timestamp
        result['created'] = f'{ts.year}-{ts.month}-{ts.day}T{ts.hour}:{ts.minute}:{ts.second}.{ts.microsecond}'
        result['text'] = {"RU": self.text}
        result['from'] = {'id': self.user_info.user_id, 'role': self.user_info.user_role}

        return result

    def __str__(self):
        """return "\n".join([
            f'*Text:*\n{self.processed_text()}\n',
            f'*Date:* {self.timestamp}\n',
            f'*Meta info:*\n{self.user_info}'
        ])"""
        date_str = f'{f"{self.timestamp.hour:02d}"}:{f"{self.timestamp.minute:02d}"} {f"{self.timestamp.day:02d}"}.{f"{self.timestamp.month:02d}"}.{f"{self.timestamp.year:02d}"}'
        return "\n".join([
            f'{"ME" if self.user_info.is_me else self.user_info.user_role} ({date_str}): {self.processed_text()}\n'
        ])

    def raw_text(self):
        """return "\n".join([
            f'Text:\n{self.processed_text()}\n',
            f'Date: {self.timestamp}\n',
            f'Meta info:\n{self.user_info.raw_text()}'
        ])"""
        date_str = f'{f"{self.timestamp.hour:02d}"}:{f"{self.timestamp.minute:02d}"} {f"{self.timestamp.day:02d}"}.{f"{self.timestamp.month:02d}"}.{f"{self.timestamp.year:02d}"}'
        return "\n".join([
            f'{"ME" if self.user_info.is_me else self.user_info.user_role} ({date_str}): {self.processed_text()}\n'
        ])

    def processed_text(self):
        try:
            processed_text = self.text.replace("<br/>", "\n").replace("<br />", "\n").replace("<div>", "")
            processed_text_parts = processed_text.split("</div>")
            processed_text = "\n".join(processed_text_parts)

            return processed_text
        except:
            return self.text


class UnreadInboxMessagesThread:
    def __init__(self, messages_thread_id, topic, messages, appeal_meta, associated_assignment_ids):
        self.messages_thread_id = messages_thread_id
        self.topic = topic
        self.messages = messages
        self.appeal_meta = appeal_meta
        self.task_url = None
        self.associated_assignment_ids = associated_assignment_ids

        if appeal_meta is not None:
            self.task_url = f'https://toloka.yandex.ru/task/{appeal_meta.pool_id}/{appeal_meta.assignment_id}'

    def __str__(self):
        info = [
            f'*Message id:* ```{self.messages_thread_id}```\n',
            f'*Topic:* {self.topic}',
            f'*User id*: {self.retrieve_user_id()}',
        ]

        if self.appeal_meta is not None and self.appeal_meta.pool_id is not None and self.appeal_meta.assignment_id is not None:
            info.append(f'\n-----------------------\n')
            info.append(f'*Appeal meta:*\n')
            info.append(f'{self.appeal_meta}')
            info.append(f'Task URL: [open]({self.task_url})')

        info.append(f'*Messages info:*\n\n')

        for message in reversed(self.messages):
            info.append(f'{message}\n')

        return "\n".join(info)

    def raw_text(self):
        info = [
            f'Message id: {self.messages_thread_id}\n',
            f'Topic: {self.topic}',
            f'User id: {self.retrieve_user_id()}',
        ]

        if self.appeal_meta is not None and self.appeal_meta.pool_id is not None and self.appeal_meta.assignment_id is not None:
            info.append(f'\n-----------------------\n')
            info.append(f'Appeal meta:\n')
            info.append(f'{self.appeal_meta.raw_text()}')
            info.append(f'Task URL: {self.task_url}')

        info.append(f'Messages info:\n\n')

        for message in reversed(self.messages):
            info.append(f'{message.raw_text()}\n')

        return "\n".join(info)

    @staticmethod
    def from_dict(items_dict):

        messages_thread_id = items_dict.get('id')
        if messages_thread_id is None:
            return None

        topic = extract_topic(items_dict)
        appeal_meta = extract_meta(items_dict)

        messages = list(map(lambda msg: TolokaMessage.from_dictionary(msg), items_dict['messages']))
        associated_tasks_ids = items_dict.get("associated_tasks")

        return UnreadInboxMessagesThread(
            messages_thread_id,
            topic,
            messages,
            appeal_meta,
            associated_tasks_ids
        )

    def retrieve_user_id(self):
        user_ids = list(map(lambda m: m.user_info.user_id, list(filter(lambda msg: msg.user_info.user_role == "USER", self.messages))))
        return user_ids[0] if len(user_ids) > 0 else "<UNKNOWN ID>"

    def __extract_assignments_id_from_message(self, text):
        result = set()
        try:
            for word in text.replace("<", " ").replace(">", " ").replace("/", " ").replace("\\", " ").replace(".", " ").replace(",", " ").split():
                if len(word) == 36 and word[10] == '-' and word[11] == '-':
                    resp = requests.get(f'https://toloka.yandex.ru/api/v1/assignments/{word}',
                                        timeout=7200.0,
                                        headers={'Content-Type': 'application/json',
                                                 'Authorization': f'OAuth {get_toloka_token()}'})
                    if 300 > resp.status_code >= 200:
                        result.add(word)
        except:
            return result

        return result

    def to_dictionary(self, associated_assignment_id=None):
        result = {'id': self.messages_thread_id, 'topic': {"RU": self.topic}}
        if associated_assignment_id is not None:
            result["associated_tasks"] = [associated_assignment_id]
        elif self.associated_assignment_ids is not None:
            result["associated_tasks"] = self.associated_assignment_ids

        if self.appeal_meta is not None:
            result['meta'] = {"pool_id": self.appeal_meta.pool_id, "project_id": self.appeal_meta.project_id, "assignment_id": self.appeal_meta.assignment_id}
        result['messages'] = list(map(lambda m: m.to_dictionary(), self.messages))

        return result

    def extract_all_assignment_ids(self):
        if self.associated_assignment_ids is not None:
            return self.associated_assignment_ids

        result = []
        if (self.appeal_meta is not None) and (self.appeal_meta.assignment_id is not None):
            result.append(self.appeal_meta.assignment_id)

        for message in self.messages:
            result.extend(self.__extract_assignments_id_from_message(message.text))

        result = list(set(result))

        return result

    def __get_assignment_info(self, assignment_id):
        resp = requests.get(f'https://toloka.yandex.ru/api/v1/assignments/{assignment_id}',
                            timeout=7200.0,
                            headers={'Content-Type': 'application/json',
                                     'Authorization': f'OAuth {get_toloka_token()}'})

        return resp.json()


class FailedTranscriptionHoneypotModel:
    def __init__(self, index, task_id, audio_url, ok_solution, user_solution):
        self.index = index
        self.task_id = task_id
        self.audio_url = audio_url
        self.ok_solution = ok_solution
        self.user_solution = user_solution

    def report(self, update, context: CallbackContext):
        context.bot.send_message(update.effective_chat.id, f'Task number: {self.index}')
        context.bot.send_message(update.effective_chat.id, f'Expected text: {self.ok_solution}')
        context.bot.send_message(update.effective_chat.id, f'User text: {self.user_solution}')

        contents = urllib.request.urlopen(self.audio_url).read()
        sound = pydub.AudioSegment.from_wav(io.BytesIO(contents))
        audio_bytes = io.BytesIO()
        sound.export(audio_bytes, format="mp3")

        context.bot.send_audio(update.effective_chat.id, audio_bytes, title=self.task_id)


class FailedCheckTranscriptionHoneypotModel:
    def __init__(self, index, task_id, audio_url, ref_text, ok_solution, user_solution):
        self.index = index
        self.task_id = task_id
        self.audio_url = audio_url
        self.ref_text = ref_text
        self.ok_solution = ok_solution
        self.user_solution = user_solution

    def report(self, update, context: CallbackContext):
        context.bot.send_message(update.effective_chat.id, f'Task number: {self.index}')
        context.bot.send_message(update.effective_chat.id, f'Expected ok: {self.ok_solution}')
        context.bot.send_message(update.effective_chat.id, f'User ok: {self.user_solution}')
        context.bot.send_message(update.effective_chat.id, f'Reference text: {self.ref_text}')

        contents = urllib.request.urlopen(self.audio_url).read()
        sound = pydub.AudioSegment.from_wav(io.BytesIO(contents))
        audio_bytes = io.BytesIO()
        sound.export(audio_bytes, format="mp3")

        context.bot.send_audio(update.effective_chat.id, audio_bytes, title=self.task_id)