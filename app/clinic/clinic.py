import abc
from typing import Collection


class Clinic(abc.ABC):
    @property
    def id(self):
        raise NotImplementedError

    @property
    def time(self):
        raise NotImplementedError

    @property
    def peoples(self):
        raise NotImplementedError

    @property
    def queue(self):
        raise NotImplementedError

    def __str__(self):
        return "time: " + str(self.time) + ", people: " + str(self.peoples)

    def calculateTime(self):
        return self.time * self.peoples

    def addPeople(self, people):
        self.peoples += 1
        self.queue.append(people)

    def showQueue(self):
        return self.queue

    def removePeople(self, index):
        self.peoples -= 1
        self.queue.pop(0)


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class PrimaryCareClinic(Clinic, Singleton):
    __instance = None
    id = 1
    queue = []
    time = 3
    peoples = 0


class CardiologyClinic(Clinic, Singleton):
    __instance = None
    id = 2
    queue = []
    time = 5
    peoples = 0


class GastroenterologyClinic(Clinic, Singleton):
    __instance = None
    id = 3
    queue = []
    time = 10
    peoples = 0


if __name__ == "__main__":
    a = PrimaryCareClinic()
    a.addPeople(1)
    print(id(a), a.queue)
    pass
