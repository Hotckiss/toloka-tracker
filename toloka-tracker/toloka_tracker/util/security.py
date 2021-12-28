import jwt
import datetime
import os
import bcrypt


class AuthService:
    def __init__(self, salt_path=None, secret=None):
        if secret is None:
            try:
                self.secret = os.environ["JWT_SECRET"]
            except:
                raise RuntimeError("No explicit secret or secret in ENV was provided")
        else:
            self.secret = secret

        if salt_path is None:
            try:
                salt_path = os.environ["SALT_PATH"]
            except:
                raise RuntimeError("No explicit salt or salt in ENV was provided")

        with open(salt_path) as f:
            self.salt = f.read()

    def generate_token(self, data: dict):
        data.update({"exp": (datetime.datetime.utcnow() + datetime.timedelta(days=365))})
        return jwt.encode(
            data,
            self.secret,
            algorithm="HS256"
        )

    def decode_token(self, data: str):
        return jwt.decode(
            data,
            self.secret,
            algorithms=["HS256"]
        )

    def hashed_password(self, password):
        return bcrypt.hashpw(password + self.salt + self.secret, self.salt)

    def check_password(self, password, expected_hashed_password):
        return expected_hashed_password == self.hashed_password(password)
