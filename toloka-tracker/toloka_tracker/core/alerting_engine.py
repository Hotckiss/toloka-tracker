import time

import telegram
import datetime
import os
import typing

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from toloka_tracker.dashboards.data import DashboardsTracksDatabase, DashboardsRolesDatabase
from toloka_tracker.toloka_api.api import get_pools, get_pool_tasks, get_all_messages
from toloka_tracker.toloka_api.models import PoolStatus, UnreadInboxMessagesThread
from toloka_tracker.tracks.service import get_all_tracks
from toloka_tracker.users.data import UsersDatabase


def alert_all(db, track_id, alert_text):
    related_dashboards = db.query(DashboardsTracksDatabase) \
        .filter(DashboardsTracksDatabase.track_id == int(track_id)).all()

    dashboards_ids = [d.dashboard_id for d in related_dashboards]

    all_related_users = db.query(DashboardsRolesDatabase) \
        .filter(DashboardsRolesDatabase.dashboard_id in dashboards_ids).all()

    to_notify = db.query(UsersDatabase).filter(UsersDatabase.id in all_related_users).all()

    for u in to_notify:
        telegram.Bot(os.environ["BOT_TOKEN"]).send_message(chat_id=u.tg_chat_id, text=alert_text)


class AlertingEngine:
    def __init__(self):
        SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

        engine = create_engine(
            SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.db = SessionLocal()
        self.bot_token = os.environ["BOT_TOKEN"]

    def __iter(self):
        tracks = get_all_tracks(self.db)

        for track in tracks:
            project_id = track['project_id']
            pools = get_pools(project_id, PoolStatus.OPEN)

            if track["max_parallel_pools"] < len(pools):
                alert_all(self.db, track['id'], f"Внимание! В проекте {project_id} превышен лимит параллельных пулов!")

            for pool in pools:
                pool_id = pool['id']
                tasks = get_pool_tasks(pool_id)
                ac_rate = len(list(filter(lambda t: t['status'] == "ACCEPTED", tasks))) / len(tasks)
                if track["min_pool_acceptance_rate"] < ac_rate:
                    alert_all(self.db, track['id'],
                              f"Внимание! В проекте {project_id} для пула {pool_id} слишком низкий AC рейт заданий!")

            messages: typing.List[UnreadInboxMessagesThread] = get_all_messages()

            cnt = 0
            for msg in messages:
                if msg.appeal_meta.project_id == project_id and \
                        msg.messages[-1].timestamp + datetime.timedelta(hours=1) >= datetime.datetime.now():
                    cnt += 1

            if cnt > track["max_hourly_appeals"]:
                alert_all(self.db, track['id'],
                          f"Внимание! В проекте {project_id} слишком много апелляций за последний час!")

    def run(self):
        while True:
            try:
                self.__iter()
                time.sleep(60)
            except:
                time.sleep(300)

