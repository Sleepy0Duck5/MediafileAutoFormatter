class Token:
    def __init__(self, index: int, str: str) -> None:
        self._index = index
        self._str = str
        self._count = 1

    def count_up(self):
        self._count += 1

    def get_index(self) -> int:
        return self._index

    def get_str(self) -> str:
        return self._str

    def get_count(self) -> int:
        return self._count

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Token):
            return False

        return (self._index == __o._index) and self._str == __o._str
