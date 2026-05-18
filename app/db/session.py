import asyncpg
import ssl
from app.core.config import settings

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        if not self.pool:
            # Strip query params like ?sslmode=require
            clean_url = settings.DATABASE_URL.split('?')[0]
            
            # Create a permissive SSL context for Neon
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            self.pool = await asyncpg.create_pool(
                clean_url,
                ssl=ctx
            )

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def execute(self, query: str, *args):
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def fetchrow(self, query: str, *args):
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)

    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)

db = Database()
