from db import Database

db = Database()
print(db.post_tag({"title": "test"}))
print(db.get_tag(1))
