import hashlib, os

SALT_SIZE = 32

class Login():
    @staticmethod
    def generate(password: str) -> dict:
        salt = str(os.urandom(SALT_SIZE))
        hashed = hashlib.sha256(str(password + salt).encode('utf-8')).hexdigest()
        return {
                'salt': salt,
                'hashed': hashed
        }

    @staticmethod
    def match(cmp_hashed: str, password: str, salt: str) -> bool:
        gen_hashed = hashlib.sha256(str(password + salt).encode('utf-8')).hexdigest()
        return gen_hashed == cmp_hashed

