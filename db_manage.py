import sqlite3 as sq
async def db_update(pole, id, text):
    with sq.connect('data_base.db') as con:
        sql = con.cursor()
        sql.execute(f"UPDATE users SET {pole} = (?) WHERE user_id == {id}", (text,))
        con.commit()

async def db_select(pole, id):
    with sq.connect('data_base.db') as con:
        sql = con.cursor()
        sql.execute(f"SELECT {pole} FROM users WHERE user_id == {id}")
        return sql.fetchone()
