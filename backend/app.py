from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import yagmail

app = Flask(__name__, static_folder="../frontend")
CORS(app)

FRONTEND = os.path.join(os.path.dirname(__file__), "../frontend")


# ---------------- BANCO ----------------
def conectar():
    return sqlite3.connect("barbearia.db")


def criar_tabela():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS agendamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        barbeiro TEXT,
        data TEXT,
        horario TEXT,
        email TEXT,
        servico TEXT,
        valor REAL
    )
    """)

    conn.commit()
    conn.close()


criar_tabela()

# ---------------- AGENDAR ----------------
@app.route("/api/agendar", methods=["POST"])
def agendar():
    try:
        dados = request.json

        nome = dados.get("nome")
        barbeiro = dados.get("barbeiro")
        data = dados.get("data")
        horario = dados.get("horario")
        email = dados.get("email")
        servico = dados.get("servico")
        valores = {
    "corte": 30,
    "barba": 20,
    "combo": 45
}

        valor = valores.get(servico, 0)

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO agendamentos (nome, barbeiro, data, horario, email, servico, valor)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nome, barbeiro, data, horario, email, servico, valor))

        conn.commit()
        conn.close()

        # -------- EMAIL --------
        try:
            yag = yagmail.SMTP(
                os.getenv("EMAIL_USER"),
                os.getenv("EMAIL_PASS")
            )

            yag.send(
                to=email,
                subject="Agendamento confirmado - Yagor's Barber 💈",
                contents=f"""
Olá {nome}!

Seu horário foi confirmado.

Barbeiro: {barbeiro}
Data: {data}
Horário: {horario}
Valor: R$ {valor}

Obrigado pela preferência!
"""
            )
        except Exception as e:
            print("Erro ao enviar email:", e)

        return jsonify({"mensagem": "Agendado com sucesso"})

    except Exception as e:
        print("ERRO:", e)
        return jsonify({"erro": "Erro ao agendar"}), 500


# ---------------- HORARIOS ----------------
@app.route("/horarios/<barbeiro>/<data>")
def horarios(barbeiro, data):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    SELECT horario FROM agendamentos
    WHERE barbeiro=? AND data=?
    """, (barbeiro, data))

    resultados = cur.fetchall()
    conn.close()

    horarios = [r[0] for r in resultados]

    return jsonify(horarios)


# ---------------- LISTAR ----------------
@app.route("/agendamentos")
def listar_agendamentos():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    SELECT nome, barbeiro, data, horario, valor
    FROM agendamentos
    ORDER BY data, horario
    """)

    dados = cur.fetchall()
    conn.close()

    lista = []

    for d in dados:
        lista.append({
            "nome": d[0],
            "barbeiro": d[1],
            "data": d[2],
            "horario": d[3],
            "valor": d[4]
        })

    return jsonify(lista)


# ---------------- CANCELAR ----------------
@app.route("/cancelar", methods=["POST"])
def cancelar():
    dados = request.json

    nome = dados.get("nome")
    data = dados.get("data")
    horario = dados.get("horario")

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    DELETE FROM agendamentos
    WHERE nome=? AND data=? AND horario=?
    """, (nome, data, horario))

    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Agendamento cancelado"})


# ---------------- LOGIN ADMIN ----------------
@app.route("/login", methods=["POST"])
def login():
    dados = request.json

    usuario = dados.get("usuario")
    senha = dados.get("senha")

    if usuario == "admin" and senha == "1234":
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "erro"}), 401


# ---------------- SITE ----------------
@app.route("/")
def index():
    return send_from_directory(FRONTEND, "index.html")


@app.route("/<path:arquivo>")
def arquivos(arquivo):
    return send_from_directory(FRONTEND, arquivo)


@app.route("/painel")
def painel():
    return send_from_directory(FRONTEND, "admin.html")


# ---------------- RODAR ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)