import sqlite3

def conectar():
    return sqlite3.connect("dados.db")

def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS licitacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        nome TEXT,
        objeto TEXT,
        data TEXT,
        link TEXT,
        registro TEXT
    )
    """)

    conn.commit()
    conn.close()