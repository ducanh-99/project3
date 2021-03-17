class Clinic:

    queue = []

    def __init__(self, id, time, peoples=0):
        super().__init__()
        self.id = id
        self.time = time
        self.peoples = peoples

    def __str__(self):
        return "Id: " + str(self.id) + ", time: " + str(self.time)

    def calculateTime(self):
        return self.time * self.peoples

    def addPeople(self, people):
        self.peoples += 1
        self.queue.append(people)

    def removePeople(self):
        self.peoples -= 1
        self.queue.pop(0)

    def __lt__(self, other):
        return self.calculateTime() < other.calculateTime()


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

if __name__ == "__main__":
    clinics = [
        Clinic(1, 15, 2),
        Clinic(2, 5),
        Clinic(3, 10, 1),
        Clinic(4, 5),
        Clinic(5, 8),
        Clinic(6, 7),
        Clinic(7, 25),
        Clinic(8, 20),
    ]

    res =solution(clinics, [1, 3, 4])
    print(res)
