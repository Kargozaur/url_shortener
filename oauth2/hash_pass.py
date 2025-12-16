import hashlib
import bcrypt


def hash_password(password: str):
    sha = hashlib.sha256(password.encode()).digest()
    return bcrypt.hashpw(sha, bcrypt.gensalt()).decode()


def verify_password(user_password: str, db_hashed: str):
    sha = hashlib.sha256(user_password.encode()).digest()
    return bcrypt.checkpw(sha, db_hashed.encode())
