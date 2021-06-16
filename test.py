# import threading
# import time
# sem = threading.Semaphore()

# def fun1():
#     while True:
#         sem.acquire()
#         print(1)
#         sem.release()
#         time.sleep(0.25)

# def fun2():
#     while True:
#         sem.acquire()
#         print(2)
#         sem.release()
#         time.sleep(0.25)

# t = threading.Thread(target = fun1)
# t.start()
# t2 = threading.Thread(target = fun2)
# t2.start()

from abc import ABC, abstractmethod
from typing import AbstractSet

class A(ABC):
    a = []
    @abstractmethod
    def test():
        pass

class B(A):
    def test():
        print("asdsd")
