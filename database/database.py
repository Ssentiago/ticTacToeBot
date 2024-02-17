import asyncio

import aiosqlite


class Database:
    def __init__(self):
        self.conn = None

    async def connect(self):
        self.conn = await aiosqlite.connect('/home/arseny/Projects/ticTacToeBot/database/database.db')

    async def get_values(self, id: int):
        await self.connect()
        all = (await (await self.conn.execute('SELECT * FROM scores ORDER BY win DESC LIMIT 10')).fetchall())
        user_data = (await (await self.conn.execute('SELECT * FROM scores WHERE id = ?', (id,))).fetchone())
        return {'user_data': user_data[2], 'all': all}

    async def increment_wins(self, id: int):
        if not self.conn:
            await self.connect()
        cur_value = await self.conn.execute('SELECT * FROM scores WHERE id = ?', (id,))
        cur_value = (await cur_value.fetchone())[1]
        res = await self.conn.execute('''UPDATE scores SET win = win + 1 WHERE id = ?''', (id,))
        await self.conn.commit()

    async def initiate_user(self, id: int, name: str):
        if not self.conn:
            await self.connect()
        check = await self.conn.execute('''SELECT * FROM scores WHERE id = ?''', (id,))
        check = await check.fetchone()

        if not check:
            await self.conn.execute('INSERT INTO scores VALUES(?, ?, ?)', (id, name, 0))
            await self.conn.commit()


