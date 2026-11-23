from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
import asyncpg


class Vendor(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class BasicChat(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str


class Chat(BasicChat):
    model_config = ConfigDict(from_attributes=True)
    conversation: str
    vendor_id: int
    user_id: int


class ChatDatabase:
    def __init__(self, pool: Optional[asyncpg.Pool]):
        self.pool = pool

    async def get_vendors(self):
        vendors = None
        sql = """SELECT id, name FROM vendors"""
        try:
            async with self.pool.acquire() as conn:
                vendors = await conn.fetch(sql)
                return [Vendor(**dict(vendor)) for vendor in vendors]
        except Exception as error:
            print(error)
        finally:
            return vendors

    async def get_chat(self, id: int):
        chat = None
        sql = """SELECT id, title, conversation, vendor_id, user_id FROM chat_history WHERE id=$1"""
        try:
            async with self.pool.acquire() as conn:
                chat = await conn.fetchrow(sql, id)
                return Chat(**dict(chat))
        except Exception as error:
            print(error)
        finally:
            return chat

    async def get_chats(self, user_id: int, vendor_id: int):
        chats = None
        sql = """SELECT id, title FROM chat_history WHERE user_id=$1 and vendor_id=$2 ORDER BY created_at DESC"""
        try:
            async with self.pool.acquire() as conn:
                chats = await conn.fetch(sql, user_id, vendor_id)
                return [BasicChat(**dict(chat)) for chat in chats]
        except Exception as error:
            print(error)
        finally:
            return chats

    async def save_chat(
        self,
        user_id: int,
        title: str,
        conversation: str,
        vendor_id: int,
        session_id: Optional[str] = None,
    ):
        chat = None
        sql = """INSERT INTO chat_history(title, conversation, user_id, vendor_id, session_id)
                         VALUES($1, $2, $3, $4, $5)
                         ON CONFLICT (session_id) DO UPDATE SET conversation = EXCLUDED.conversation
                         RETURNING id, user_id, vendor_id, title, conversation"""
        try:
            async with self.pool.acquire() as conn:
                chat = await conn.fetchrow(
                    sql, title, conversation, user_id, vendor_id, session_id
                )
                return Chat(**dict(chat))
        except Exception as error:
            print(error)
        finally:
            return chat
