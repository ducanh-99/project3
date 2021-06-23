import enum


class UserRole(enum.Enum):
    ADMIN = 'admin'
    GUEST = 'guest'


class StaffContractType(enum.Enum):
    PART_TIME = 'Thoi vu'
    OFFICIAL = 'Chinh thuc'


class SearchTreeParam(enum.Enum):
    TREE = 'tree'
    LIST = 'list'
