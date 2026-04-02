from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
import os
import yagmail
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
        email = dados.get("email")
        servicos = dados.get("servicos") or []
        valor = dados.get("valor")

        if not isinstance(servicos, list):
            servicos = []

        servicos_str = ", ".join(servicos)

        if not nome or not barbeiro or not data or not horario or not email:
            return jsonify({"erro": "Dados incompletos"}), 400

        conn = conectar()
        cur = conn.cursor()

        # 🚫 EVITA HORÁRIO DUPLICADO
        cur.execute("""
        SELECT * FROM agendamentos
        WHERE barbeiro=%s AND data=%s AND horario=%s
        """, (barbeiro, data, horario))

        if cur.fetchone():
            return jsonify({"erro": "Horário já ocupado"}), 400

        cur.execute("""
        INSERT INTO agendamentos (nome, barbeiro, data, horario, email, servico, valor)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nome, barbeiro, data, horario, email, servicos_str, valor))

        conn.commit()
        cur.close()
        conn.close()

        # -------- EMAIL CONFIRMAÇÃO --------
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
Serviços: {servicos_str}
Valor: R$ {valor}

Obrigado pela preferência!
"""
            )
        except Exception as e:
            print("ERRO EMAIL:", e)

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

        resultados = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify([r[0] for r in resultados])

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
        SELECT nome, barbeiro, data, horario, valor
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
                "valor": d[4]
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

        nome = dados.get("nome")
        data = dados.get("data")
        horario = dados.get("horario")

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
        DELETE FROM agendamentos
        WHERE nome=%s AND data=%s AND horario=%s
        """, (nome, data, horario))

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({"mensagem": "Agendamento cancelado"})

    except Exception as e:
        print("ERRO CANCELAR:", e)
        return jsonify({"erro": "Erro ao cancelar"}), 500


# ---------------- LOGIN ADMIN ----------------
@app.route("/login", methods=["POST"])
def login():
    dados = request.json

    if dados.get("usuario") == "admin" and dados.get("senha") == "1234":
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "erro"}), 401


# ---------------- FINALIZAR ----------------
@app.route("/finalizar", methods=["POST"])
def finalizar():
    try:
        dados = request.json

        nome = dados.get("nome")
        data = dados.get("data")
        horario = dados.get("horario")

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
        DELETE FROM agendamentos
        WHERE nome=%s AND data=%s AND horario=%s
        """, (nome, data, horario))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"mensagem": "Finalizado"})

    except Exception as e:
        print("ERRO FINALIZAR:", e)
        return jsonify({"erro": "Erro"}), 500


# ---------------- LEMBRETES AUTOMÁTICOS ----------------
@app.route("/lembretes")
def lembretes():
    try:
        agora = datetime.now()
        daqui_1h = agora + timedelta(hours=1)

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
        SELECT nome, email, barbeiro, data, horario
        FROM agendamentos
        """)

        dados = cur.fetchall()

        cur.close()
        conn.close()

        enviados = 0

        for d in dados:
            nome, email, barbeiro, data, horario = d

            try:
                dataHora = datetime.strptime(f"{data} {horario}", "%Y-%m-%d %H:%M")

                if agora <= dataHora <= daqui_1h:

                    yag = yagmail.SMTP(
                        os.getenv("EMAIL_USER"),
                        os.getenv("EMAIL_PASS")
                    )

                    yag.send(
                        to=email,
                        subject="⏰ Lembrete de horário - Yagor's Barber",
                        contents=f"""
Olá {nome}!

Seu horário é em breve 💈

Barbeiro: {barbeiro}
Horário: {horario}

Te esperamos!
"""
                    )

                    enviados += 1

            except Exception as e:
                print("Erro lembrete:", e)

        return f"Lembretes enviados: {enviados}"

    except Exception as e:
        print("ERRO LEMBRETES:", e)
        return "Erro", 500


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