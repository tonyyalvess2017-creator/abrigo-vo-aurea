import json
import random
import urllib.request
import urllib.error
import time
from flask import Flask, send_file, request, jsonify

app = Flask(__name__, static_folder=".", template_folder=".")

# Sua chave de API
API_KEY = "AQ.Ab8RN6JarQSnkemzVcxRbqVhkc_1If_DZ-TtSvvOZ9lRv3DQIQ"

# URL utilizando o gemini-1.5-flash (mais estável para cotas)
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

SYSTEM_INSTRUCTION_SABEDORIA = (
    "Você é um filósofo apaixonado pela causa animal. "
    "Gere UMA ÚNICA frase reflexiva e poética sobre cães e animais. "
    "Nunca use clichês. Varie totalmente o vocabulário a cada chamada."
)

SYSTEM_INSTRUCTION_JOGO = (
    "Você é um cachorro muito expressivo reagindo a um petisco ou carinho. "
    "Gere uma reação CURTA (máximo 5 palavras) usando combinações divertidas de onomatopeias e emojis."
)

SYSTEM_INSTRUCTION_ABRIGO = (
    "Você é a assistente interativa do Abrigo Vó Áurea (Proteção Animal). "
    "Forneça informações sobre cuidados com animais, resgates e doações via Pix de forma simpática."
)

def chamar_gemini(system_instruction, prompt_texto, temperature=0.9):
    corpo = {
        "system_instruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt_texto}]
            }
        ],
        "generationConfig": {
            "temperature": temperature
        }
    }

    data_bytes = json.dumps(corpo).encode('utf-8')
    headers = {'Content-Type': 'application/json'}

    # Tentativa com repetição automática caso ocorra o Erro 429 (Limite excedido)
    max_tentativas = 3
    for tentativa in range(max_tentativas):
        try:
            req = urllib.request.Request(URL, data=data_bytes, headers=headers)
            with urllib.request.urlopen(req) as resp:
                resultado = json.loads(resp.read().decode('utf-8'))
                return resultado['candidates'][0]['content']['parts'][0]['text'].strip()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"[AVISO] Erro 429 (Cota excedida). Tentativa {tentativa + 1} de {max_tentativas}. Aguardando...")
                time.sleep(2 * (tentativa + 1))  # Espera progressiva (2s, 4s...) antes de tentar de novo
                continue
            else:
                erro_corpo = e.read().decode('utf-8')
                print(f"[ERRO HTTP {e.code}]: {erro_corpo}")
                raise e
        except Exception as e:
            raise e
            
    raise Exception("Limite de requisições excedido (Erro 429). Aguarde alguns segundos antes de tentar novamente.")

@app.route("/")
def index():
    return send_file("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    dados = request.get_json() or {}
    mensagem_usuario = dados.get("mensagem", "").strip()

    if not mensagem_usuario:
        return jsonify({"resposta": "Como posso ajudar você e os animais do abrigo hoje?"})

    try:
        texto_ia = chamar_gemini(SYSTEM_INSTRUCTION_ABRIGO, mensagem_usuario, temperature=0.7)
        return jsonify({"resposta": texto_ia})
    except Exception as e:
        print(f"[ERRO NO CHAT]: {e}")
        return jsonify({"resposta": "Muitos pedidos simultâneos! Aguarde alguns segundos e envie novamente."})

@app.route("/api/sabedoria", methods=["POST"])
def sabedoria():
    angulos = [
        "a percepção do tempo pelo olhar de um cão",
        "metáforas sobre silêncio, pegadas e lealdade",
        "a dignidade dos animais resgatados",
        "a transformação emocional ao adotar um pet"
    ]
    prompt = f"Escreva uma frase sobre a causa animal abordando {random.choice(angulos)}. [ID: {time.time()}]"

    try:
        texto_ia = chamar_gemini(SYSTEM_INSTRUCTION_SABEDORIA, prompt, temperature=1.3)
        return jsonify({"resposta": texto_ia})
    except Exception as e:
        print(f"[ERRO SABEDORIA]: {e}")
        return jsonify({"resposta": "A compaixão pelos animais transforma a nossa própria humanidade."})

@app.route("/api/reacao-jogo", methods=["POST"])
def reacao_jogo():
    estimulos = ["Carinho na orelha", "Petisco saboroso", "Brincadeira com bolinha", "Coçadinha na barriga"]
    prompt = f"Reação ao estímulo: {random.choice(estimulos)}. [ID: {time.time()}]"

    try:
        reacao = chamar_gemini(SYSTEM_INSTRUCTION_JOGO, prompt, temperature=1.3)
        return jsonify({"reacao": reacao})
    except Exception as e:
        print(f"[ERRO JOGO]: {e}")
        reacoes = ["Nham nham! 🍖", "Rabo balançando! ✨", "Sniff sniff! 🐾", "Yum! ❤️"]
        return jsonify({"reacao": random.choice(reacoes)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)