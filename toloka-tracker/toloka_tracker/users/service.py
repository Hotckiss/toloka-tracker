from toloka_tracker.users.data import UsersDatabase


def get_user_by_login(db, login: str):
    return db.query(UsersDatabase).filter(UsersDatabase.login == login).first()


def get_user_by_id(db, user_id: int):
    user = db.query(UsersDatabase).filter(UsersDatabase.id == user_id).first()
    return {"id": user.id, "login": user.login, "tg_chat_id": user.tg_chat_id, "created_at": user.created_at}
