import motor.motor_asyncio
from database.config_db import mdb
from info import DATABASE_URI, DATABASE_NAME

class NotifyDB:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URI)
        self.db = self.client[DATABASE_NAME]
        self.col = self.db.notification

    async def add_notify(self, user_id, query):
        # চেক করবে আগে থেকেই রিকোয়েস্ট করা আছে কিনা
        if not await self.col.find_one({"id": user_id, "query": query}):
            await self.col.insert_one({"id": user_id, "query": query})
            return True
        return False

    async def remove_notify(self, user_id, query):
        await self.col.delete_one({"id": user_id, "query": query})

    async def get_all_notify(self):
        return self.col.find({})

notify_db = NotifyDB()
