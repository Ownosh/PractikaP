import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", ""),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", ""),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def init_users_table():
    """Создаёт таблицу пользователей если не существует"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS polzovateli (
            id          SERIAL PRIMARY KEY,
            login       VARCHAR(100) UNIQUE NOT NULL,
            parol       VARCHAR(255) NOT NULL,
            rol         VARCHAR(50)  NOT NULL DEFAULT 'Пользователь',
            zablokirovan BOOLEAN NOT NULL DEFAULT FALSE,
            popytki     INTEGER NOT NULL DEFAULT 0
        );
    """)
    # Добавляем администратора по умолчанию если нет пользователей
    cur.execute("SELECT COUNT(*) FROM polzovateli;")
    count = cur.fetchone()[0]
    if count == 0:
        cur.execute("""
            INSERT INTO polzovateli (login, parol, rol)
            VALUES ('admin', 'admin123', 'Администратор'),
                   ('user1', 'user123',  'Пользователь');
        """)
    conn.commit()
    cur.close()
    conn.close()


def get_user(login: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, login, parol, rol, zablokirovan, popytki FROM polzovateli WHERE login = %s;",
        (login,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {
            "id": row[0],
            "login": row[1],
            "parol": row[2],
            "rol": row[3],
            "zablokirovan": bool(row[4]),
            "popytki": row[5],
        }
    return None


def increment_attempts(login: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE polzovateli
        SET
            popytki = popytki + 1,
            zablokirovan = CASE WHEN (popytki + 1) >= 3 THEN TRUE ELSE zablokirovan END
        WHERE login = %s;
    """, (login,))
    conn.commit()
    cur.close()
    conn.close()


def reset_attempts(login: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE polzovateli SET popytki = 0 WHERE login = %s;",
        (login,)
    )
    conn.commit()
    cur.close()
    conn.close()


def block_user(login: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE polzovateli SET zablokirovan = TRUE, popytki = GREATEST(popytki, 3) WHERE login = %s;",
        (login,),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_all_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, login, rol, zablokirovan, popytki FROM polzovateli ORDER BY id;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def add_user(login: str, parol: str, rol: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO polzovateli (login, parol, rol) VALUES (%s, %s, %s);",
            (login, parol, rol)
        )
        conn.commit()
        return True, "Пользователь добавлен."
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False, "Пользователь с таким логином уже существует."
    finally:
        cur.close()
        conn.close()


def update_user(user_id: int, login: str, parol: str, rol: str, zablokirovan: bool):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE polzovateli
        SET login = %s, parol = %s, rol = %s, zablokirovan = %s,
            popytki = CASE WHEN %s = FALSE THEN 0 ELSE popytki END
        WHERE id = %s;
    """, (login, parol, rol, zablokirovan, zablokirovan, user_id))
    conn.commit()
    cur.close()
    conn.close()
