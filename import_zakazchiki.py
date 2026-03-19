import json
import psycopg2
from dotenv import load_dotenv
import os

# Загружаем переменные из .env
load_dotenv()

DB_HOST   = os.getenv("DB_HOST")
DB_PORT   = int(os.getenv("DB_PORT", 5432))
DB_NAME   = os.getenv("DB_NAME")
DB_USER   = os.getenv("DB_USER")
DB_PASS   = os.getenv("DB_PASS")
JSON_FILE = os.getenv("JSON_FILE", "Заказчики.json")

def import_zakazchiki():
    with open(JSON_FILE, encoding="utf-8") as f:
        data = json.load(f)

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cur = conn.cursor()

    inserted = 0
    skipped = 0

    for item in data:
        try:
            cur.execute("""
                INSERT INTO kontragent 
                    (id_kontragenta, naimenovanie, inn, adres, telefon, yavl_postavshikom, yavl_pokupatel)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id_kontragenta) DO NOTHING
            """, (
                item["id"],
                item["name"],
                item.get("inn", ""),
                item.get("addres", ""),
                item.get("phone", ""),
                item.get("salesman", False),
                item.get("buyer", False)
            ))
            if cur.rowcount > 0:
                inserted += 1
                print(f"Добавлен: {item['name']}")
            else:
                skipped += 1
                print(f"Пропущен (уже существует): {item['name']}")
        except Exception as e:
            print(f"Ошибка при добавлении {item['name']}: {e}")
            conn.rollback()
            continue

    conn.commit()
    cur.close()
    conn.close()

    print(f"\nГотово! Добавлено: {inserted}, пропущено: {skipped}")

if __name__ == "__main__":
    import_zakazchiki()
