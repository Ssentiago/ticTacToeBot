import asyncio
import aiosqlite
import sqlite3
import os


class Database:
    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), 'database.db')
        print(path, 'initiated')
        self.connect = sqlite3.connect(path)
        self.connect.execute('''CREATE TABLE IF NOT EXISTS scores(
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL, 
        win INTEGER NOT NULL)''')
        self.connect.commit()
        self.connect.close()


    async def connect_to_db(self):
        path = os.path.join(os.path.dirname(__file__), 'database.db')
        print(path, 'connected')
        self.connect = await aiosqlite.connect(path)

    async def close_db(self):
        await self.connect.close()

    async def get_values(self, id: int):
        await self.connect_to_db()
        all = (await (await self.connect.execute('SELECT * FROM scores ORDER BY win DESC LIMIT 10')).fetchall())
        user_data = (await (await self.connect.execute('SELECT * FROM scores WHERE id = ?', (id,))).fetchone())
        await self.close_db()
        return {'user_data': user_data[2], 'all': all}

    async def increment_wins(self, id: int):
        await self.connect_to_db()
        cur_value = await self.connect.execute('SELECT * FROM scores WHERE id = ?', (id,))
        cur_value = (await cur_value.fetchone())[1]
        res = await self.connect.execute('''UPDATE scores SET win = win + 1 WHERE id = ?''', (id,))
        await self.connect.commit()
        await self.close_db()

    async def initiate_user(self, id: int, name: str):
        await self.connect_to_db()
        check = await self.connect.execute('''SELECT * FROM scores WHERE id = ?''', (id,))
        check = await check.fetchone()

        if not check:
            await self.connect.execute('INSERT INTO scores VALUES(?, ?, ?)', (id, name, 0))
            await self.connect.commit()
        await self.close_db()
