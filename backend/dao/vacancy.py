import asyncpg


class VacancyDAO:
    def __init__(self, connection: asyncpg.Connection):
        self._connection = connection
