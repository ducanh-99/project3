import os
import random
import time
import threading


class Clinic:

    queue = []

    def __init__(self, id, time, peoples=0):
        super().__init__()
        self.id = id
        self.time = time
        self.peoples = peoples

    def __str__(self):
        return "Id: " + str(self.id) + ", time: " + str(self.time) + ", people: " + str(self.peoples)

    def calculateTime(self):
        return self.time * self.peoples

    def addPeople(self, people):
        self.peoples += 1
        self.queue.append(people)

    def removePeople(self, index):
        self.peoples -= 1
        self.queue.pop(0)

    def __lt__(self, other):
        return self.calculateTime() < other.calculateTime()


class Doctor:

    def __init__(self):
        super().__init__()

    def addSchedule(self, clinic):
        n = len(clinic)
        listSchedule = random.sample(range(1, n), random.randint(1, n-1))
        return listSchedule


class People:
    def __init__(self, name):
        super().__init__()
        self.name = name


def solution(clinics, schedule):
    '''
        clinics: List of chinics in hopital
        schedule: doctor appointments specified
        return: schedule of people
    '''
    listClinicsInSchedule = []
    for clinic in clinics:
        for i in schedule:
            if i == clinic.id:
                listClinicsInSchedule.append(clinic)
                break
    res = []

    listClinicsInSchedule.sort()
    for i in listClinicsInSchedule:
        res.append(i.id)
    return res


class ThreadingInBackGround(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, interval=1):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        """ Method that runs forever """
        i = 0
        while i < self.interval:
            # Do something
            time.sleep(self.interval)
            i += 1
        print()

def addInBackGround(schedule):
    for i in schedule:
        Thread = ThreadingInBackGround(i)


def menu():
    print("1. Thêm mới khoa khám bệnh")
    print("2. Kiểm tra một khoa khám đang có bao nhiêu người")
    print("3. Thêm một danh sách khám bênh cho một bênh nhân")
    print("Mời bác sĩ lựa chọn một phương thức:")


if __name__ == "__main__":
    clinics = [
        Clinic(1, 15, 2),
        Clinic(2, 5),
        Clinic(3, 10, 1),
        Clinic(4, 5),
        Clinic(5, 5),
        Clinic(6, 5),
        Clinic(7, 5),
    ]
    id = 4
    doctor = Doctor()
    while True:
        menu()
        i = int(input())
        if i == 1:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Mời nhập thời gian khám")
            time = int(input())
            clinics.append(Clinic(id+1, time))
            i += 1
        elif i == 2:
            os.system('cls' if os.name == 'nt' else 'clear')
            for clinic in clinics:
                print(clinic)
        elif i == 3:
            os.system('cls' if os.name == 'nt' else 'clear')
            # print()
            schedule = doctor.addSchedule(clinics)
            print("Thứ tự khám của bác sĩ", str(schedule))
            print("Thứ tự khám lần lượt là: " + str(solution(clinics, schedule)))

            # addInBackGround(res)
            # print(res)
