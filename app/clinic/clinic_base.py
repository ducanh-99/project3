class ClinicBase(object):
    mean: int

    def __init__(self) -> None:
        super().__init__()
        self.queue = []

    def add_person(self, id_person):
        self.queue.append(id_person)

    def leave_person(self):
        self.queue.pop()
