from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
import os
from datetime import datetime, timedelta

app = Flask(__name__, static_folder="frontend")
CORS(app)

FRONTEND = os.path.join(os.path.dirname(__file__), "frontend")

# ---------------- BANCO ----------------
def conectar():
    return psycopg2.connect(
        os.getenv("DATABASE_URL"),
        sslmode="require"
    )

# ---------------- AGENDAR ----------------
@app.route("/api/agendar", methods=["POST"])
def agendar():
    try:
        dados = request.json

        nome = dados.get("nome")
        barbeiro = dados.get("barbeiro")
        data = dados.get("data")
        horario = dados.get("horario")
        telefone = dados.get("telefone")
        servicos = dados.get("servicos") or []
        valor = dados.get("valor") or 0

        if not isinstance(servicos, list):
            servicos = []

        if not nome or not barbeiro or not data or not horario or not telefone:
            return jsonify({"erro": "Dados incompletos"}), 400

        servicos_str = ", ".join(servicos)

        conn = conectar()
        cur = conn.cursor()

        # evitar duplicado
        cur.execute("""
        SELECT 1 FROM agendamentos
        WHERE barbeiro=%s AND data=%s AND horario=%s
        """, (barbeiro, data, horario))

        if cur.fetchone():
            return jsonify({"erro": "Horário já ocupado"}), 400

        cur.execute("""
        INSERT INTO agendamentos 
        (nome, barbeiro, data, horario, telefone, servico, valor, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,'pendente')
        """, (nome, barbeiro, data, horario, telefone, servicos_str, valor))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"mensagem": "Agendado com sucesso"})

    except Exception as e:
        print("ERRO AGENDAR:", e)
        return jsonify({"erro": "Erro ao agendar"}), 500


# ---------------- HORARIOS ----------------
@app.route("/horarios/<barbeiro>/<data>")
def horarios(barbeiro, data):
    try:
        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
        SELECT horario FROM agendamentos
        WHERE barbeiro=%s AND data=%s
        """, (barbeiro, data))

        horarios = [r[0] for r in cur.fetchall()]

        cur.close()
        conn.close()

        return jsonify(horarios)

    except Exception as e:
        print("ERRO HORARIOS:", e)
        return jsonify([])


# ---------------- LISTAR ----------------
@app.route("/agendamentos")
def listar_agendamentos():
    try:
        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
        SELECT nome, barbeiro, data, horario, valor, telefone, status
        FROM agendamentos
        ORDER BY data, horario
        """)

        dados = cur.fetchall()

        cur.close()
        conn.close()

        lista = []
        for d in dados:
            lista.append({
                "nome": d[0],
                "barbeiro": d[1],
                "data": d[2],
                "horario": d[3],
                "valor": d[4],
                "telefone": d[5],
                "status": d[6]
            })

        return jsonify(lista)

    except Exception as e:
        print("ERRO LISTAR:", e)
        return jsonify([])


# ---------------- CANCELAR ----------------
@app.route("/cancelar", methods=["POST"])
def cancelar():
    try:
        dados = request.json

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
        DELETE FROM agendamentos
        WHERE nome=%s AND data=%s AND horario=%s
        """, (dados.get("nome"), dados.get("data"), dados.get("horario")))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"mensagem": "Cancelado"})

    except Exception as e:
        print("ERRO CANCELAR:", e)
        return jsonify({"erro": "Erro"}), 500


# ---------------- FINALIZAR ----------------
@app.route("/finalizar", methods=["POST"])
def finalizar():
    try:
        dados = request.json

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
        UPDATE agendamentos
        SET status='finalizado'
        WHERE nome=%s AND data=%s AND horario=%s
        """, (dados.get("nome"), dados.get("data"), dados.get("horario")))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"mensagem": "Finalizado"})

    except Exception as e:
        print("ERRO FINALIZAR:", e)
        return jsonify({"erro": "Erro"}), 500


# ---------------- RELATORIO ----------------
@app.route("/relatorio")
def relatorio():
    try:
        data = request.args.get("data")

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
        SELECT SUM(valor)
        FROM agendamentos
        WHERE data=%s
        """, (data,))
        total = cur.fetchone()[0] or 0

        cur.execute("""
        SELECT barbeiro, COUNT(*), SUM(valor)
        FROM agendamentos
        WHERE data=%s
        GROUP BY barbeiro
        """ , (data,))

        barbeiros = []
        for b in cur.fetchall():
            barbeiros.append({
                "nome": b[0],
                "quantidade": b[1],
                "total": b[2] or 0
            })

        cur.close()
        conn.close()

        return jsonify({
            "total_dia": total,
            "barbeiros": barbeiros
        })

    except Exception as e:
        print("ERRO RELATORIO:", e)
        return jsonify({"erro": "Erro"}), 500


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
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)