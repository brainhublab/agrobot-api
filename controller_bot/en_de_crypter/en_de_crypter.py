from cryptography.fernet import Fernet


class EnDeCrypt(object):
    def __init__(self, key, msg):
        self.key = key
        self.msg = msg

    def enCrypt(self):
        f = Fernet(self.key)
        """self.msg.encode() will transform string message to bytes"""
        try:
            return f.encrypt(self.msg.encode())
        except Exception as e:
            raise e

    def DeCrypt(self):
        f = Fernet(self.key)
        """self.msg.decode() will transform bytes message to string"""
        try:
            return f.decrypt(self.msg).decode()
        except Exception as e:
            raise e

