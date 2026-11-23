import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import psycopg
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

@asynccontextmanager
async def get_database_checkpointer() -> AsyncGenerator[AsyncPostgresSaver, None]:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError(
            "DATABASE_URL is missing. Please add your PostgreSQL database URL to .env"
        )

    async with AsyncPostgresSaver.from_conn_string(database_url) as checkpointer:
        await checkpointer.setup()
        yield checkpointer

    # database_url = os.getenv("DATABASE_URL")
        
    # if not database_url:
    #     raise ValueError(
    #         "DATABASE_URL is missing. Please add your PostgreSQL database URL to .env"
    #     )
    # rows = None
    # sql = """SELECT id, title FROM chat_history WHERE user_id=%(user_id)s"""
    # try:
    #     with  psycopg.connect(database_url) as conn:
    #         with  conn.cursor() as cur:
    #             cur.execute(sql, {"user_id": user_id})
    #             # get the generated id back
    #             rows = cur.fetchall()
    # except (Exception, psycopg.DatabaseError) as error:
    #     print(error)
    # finally:
    #     return rows
