class Token:
    def __init__(self, str: str) -> None:
        self._str = str
        self._count = 1

    def count_up(self):
        self._count += 1

    def get_str(self) -> str:
        return self._str

    def get_count(self) -> int:
        return self._count
