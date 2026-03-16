import sqlite3

con = sqlite3.connect("database.db")

cur = con.cursor()

cur.execute("""
CREATE TABLE agendamentos(
id INTEGER PRIMARY KEY AUTOINCREMENT,
nome TEXT,
email TEXT,
barbeiro TEXT,
data TEXT,
horario TEXT
)
""")

con.commit()
con.close()

print("Banco criado")