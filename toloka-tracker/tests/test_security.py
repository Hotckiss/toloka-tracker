from toloka_tracker.util.security import AuthService


def test_generate_token():
    auth = AuthService()
    assert auth.generate_token({"iss": "hotckiss"}) is not None


def test_encode_decode_token():
    auth = AuthService()
    enc = auth.generate_token({"iss": "hotckiss"})
    dec = auth.decode_token(enc)
    assert dec['iss'] == 'hotckiss'


def test_hashed_password():
    auth = AuthService()
    assert auth.hashed_password("1234") == "$2a$12$qLmUtJRhhOUn.ogUOkMTd.1C8fkBxKXqEmPRkCU.sCYQ.E0BnWy1G"


def test_check_password():
    auth = AuthService()
    hashed = auth.hashed_password("12345678")
    assert auth.check_password("12345678", hashed)
    assert not auth.check_password("123456789", hashed)
