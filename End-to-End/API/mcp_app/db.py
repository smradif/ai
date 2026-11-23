from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from database.postgres import get_postgres
import asyncpg

# class Vendor(BaseModel):
#     model_config = ConfigDict(from_attributes=True)
#     id: int
#     name: str


# class BasicChat(BaseModel):
#     model_config = ConfigDict(from_attributes=True)
#     id: int
#     title: str


class Note(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    text: str
    created_at: str
    created_by: int


class NoteDatabase:
    def __init__(self):
        self.pool = get_postgres()

    async def get_notes(self):
        notes = None
        sql = """SELECT id, text, created_at, created_by FROM notes"""
        try:
            async with self.pool.acquire() as conn:
                notes = await conn.fetch(sql)
                return [Note(**dict(vendor)) for vendor in notes]
        except Exception as error:
            print(error)
        finally:
            return notes

    async def save_note(self, user_id: int, text: str):
        note = None
        sql = """INSERT INTO notes(created_by, text)
                         VALUES($1, $2)
                         ON CONFLICT (session_id) DO UPDATE SET conversation = EXCLUDED.conversation
                         RETURNING id, created_by, created_at, text"""
        try:
            async with self.pool.acquire() as conn:
                note = await conn.fetchrow(sql, user_id, text)
                return Note(**dict(note))
        except Exception as error:
            print(error)
        finally:
            return note

    async def remove_note(self, id: int):
        note = None
        sql = f"""DELETE FROM notes(created_by, text)
                                WHERE id={id} """
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(sql)
                return result
        except Exception as error:
            print(error)
        finally:
            return note
