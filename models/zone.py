class Normal():
    cost: int | None = 1


class Blocked():
    cost: int | None = None  # inaccessible


class Restricted():
    cost: int | None = 2


class Priority():
    cost: int | None = 1
