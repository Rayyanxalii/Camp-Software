from sqlalchemy import text
from app.database import SessionLocal

db = SessionLocal()

result = db.execute(text("PRAGMA table_info(inventory);"))

for row in result:
    print(row)
    


from app.database import engine

print(engine.url)