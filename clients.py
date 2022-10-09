import hashlib as _hashlib
import random
import datetime

class Address():

    def __init__(self) -> None:
        pass

    def create(self, number: str):
        self.addr = self.__generator__(data=number)
        return self.addr

    def __register__(self):
        pass

    def __is_unique__(self):
        pass

    def __generator__(self, data):
        hash = _hashlib.sha256(f'{datetime.datetime.now()}{data}{random.randint(0, 999)}'.encode()).hexdigest()
        return f'jadlen{hash}'