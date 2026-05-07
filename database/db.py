import aiosqlite
from config import DATABASE_URL


async def init_db():
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                notify_time TEXT DEFAULT '09:00',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orchids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                species TEXT NOT NULL,
                color TEXT,
                last_watered DATE,
                last_fertilized DATE,
                last_repotted DATE,
                watering_interval INTEGER DEFAULT 7,
                fertilizing_interval INTEGER DEFAULT 14,
                repotting_interval INTEGER DEFAULT 365,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(telegram_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS care_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orchid_id INTEGER NOT NULL,
                care_type TEXT NOT NULL,
                care_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (orchid_id) REFERENCES orchids(id)
            )
        """)
        await db.commit()


async def add_user(telegram_id: int, username: str = None):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?)",
            (telegram_id, username)
        )
        await db.commit()


async def get_user(telegram_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        async with db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            return await cursor.fetchone()


async def update_notify_time(telegram_id: int, time: str):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute(
            "UPDATE users SET notify_time = ? WHERE telegram_id = ?",
            (time, telegram_id)
        )
        await db.commit()


async def add_orchid(user_id: int, name: str, species: str, color: str = None,
                     watering_interval: int = 7, fertilizing_interval: int = 14):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute(
            """INSERT INTO orchids (user_id, name, species, color, watering_interval, fertilizing_interval)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, name, species, color, watering_interval, fertilizing_interval)
        )
        await db.commit()


async def get_user_orchids(user_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        async with db.execute(
            "SELECT * FROM orchids WHERE user_id = ? ORDER BY name", (user_id,)
        ) as cursor:
            return await cursor.fetchall()


async def get_orchid(orchid_id: int, user_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        async with db.execute(
            "SELECT * FROM orchids WHERE id = ? AND user_id = ?", (orchid_id, user_id)
        ) as cursor:
            return await cursor.fetchone()


async def update_orchid_care(orchid_id: int, care_type: str):
    from datetime import date
    field_map = {
        "water": "last_watered",
        "fertilize": "last_fertilized",
        "repot": "last_repotted"
    }
    field = field_map.get(care_type)
    if not field:
        return
    today = date.today().isoformat()
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute(
            f"UPDATE orchids SET {field} = ? WHERE id = ?",
            (today, orchid_id)
        )
        await db.execute(
            "INSERT INTO care_history (orchid_id, care_type, care_date) VALUES (?, ?, ?)",
            (orchid_id, care_type, today)
        )
        await db.commit()


async def add_care_history(orchid_id: int, care_type: str):
    from datetime import date
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute(
            "INSERT INTO care_history (orchid_id, care_type, care_date) VALUES (?, ?, ?)",
            (orchid_id, care_type, date.today().isoformat())
        )
        await db.commit()


async def get_care_history(orchid_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        async with db.execute(
            """SELECT care_type, care_date FROM care_history
               WHERE orchid_id = ? ORDER BY care_date DESC, id DESC LIMIT 30""",
            (orchid_id,)
        ) as cursor:
            return await cursor.fetchall()


async def delete_orchid(orchid_id: int, user_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute(
            "DELETE FROM orchids WHERE id = ? AND user_id = ?", (orchid_id, user_id)
        )
        await db.commit()


async def get_all_users():
    async with aiosqlite.connect(DATABASE_URL) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            return await cursor.fetchall()


async def get_orchids_needing_care(user_id: int):
    from datetime import date, timedelta
    today = date.today()
    async with aiosqlite.connect(DATABASE_URL) as db:
        async with db.execute(
            "SELECT * FROM orchids WHERE user_id = ?", (user_id,)
        ) as cursor:
            orchids = await cursor.fetchall()

    needing_care = []
    for o in orchids:
        # o indices: 0=id,1=user_id,2=name,3=species,4=color,5=last_watered,
        #            6=last_fertilized,7=last_repotted,8=watering_interval,
        #            9=fertilizing_interval,10=repotting_interval,11=notes
        needs = []
        if o[5]:
            last = date.fromisoformat(o[5])
            if (today - last).days >= o[8]:
                needs.append("💧 полив")
        else:
            needs.append("💧 полив (никогда не поливали)")

        if o[6]:
            last = date.fromisoformat(o[6])
            if (today - last).days >= o[9]:
                needs.append("🌿 подкормка")
        else:
            needs.append("🌿 подкормка (никогда не подкармливали)")

        if needs:
            needing_care.append((o, needs))

    return needing_care
