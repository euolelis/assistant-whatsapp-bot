from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

# Descomente a linha abaixo se for usar a OpenAI
# import openai

# Descomente as duas linhas abaixo se for usar o Gemini
# import google.generativeai as genai
# from google.cloud import aiplatform

# Descomente a linha abaixo se for usar o Groq
# from groq import Groq

load_dotenv()

app = Flask(__name__)

# Configurações (obtidas das variáveis de ambiente do Render)
MANYCHAT_API_KEY = os.environ.get("MANYCHAT_API_KEY")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")  # O mesmo token que você definirá no Manychat

# Descomente a linha abaixo se for usar a OpenAI
# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Descomente a linha abaixo se for usar o Gemini
# GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Descomente a linha abaixo se for usar o Groq
# GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Apenas um lembrete amigável para configurar as variáveis de ambiente no Render
if not MANYCHAT_API_KEY or not VERIFY_TOKEN:
    print("AVISO: Variáveis de ambiente MANYCHAT_API_KEY ou VERIFY_TOKEN não configuradas no Render!")

# Configuração da OpenAI (descomente se for usar)
# if OPENAI_API_KEY:
#     openai.api_key = OPENAI_API_KEY
# else:
#     print("AVISO: Variável de ambiente OPENAI_API_KEY não configurada no Render!")

# Configuração do Gemini (descomente se for usar)
# if GOOGLE_API_KEY:
#     genai.configure(api_key=GOOGLE_API_KEY)
#     # Define o projeto e a localização, se necessário
#     # aiplatform.init(project="seu-projeto", location="sua-localizacao")
#     model = genai.GenerativeModel('gemini-pro') # ou o modelo que você quiser usar
# else:
#     print("AVISO: Variável de ambiente GOOGLE_API_KEY não configurada no Render!")

# Configuração do Groq (descomente se for usar)
# if GROQ_API_KEY:
#     client = Groq(api_key=GROQ_API_KEY)
# else:
#     print("AVISO: Variável de ambiente GROQ_API_KEY não configurada no Render!")

# Endpoint para verificar o webhook do Manychat (GET)
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode and token:
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print('WEBHOOK VERIFICADO')
            return challenge, 200
        else:
            return 'Token de verificação inválido.', 403
    else:
        return 'Parâmetros ausentes.', 400

# Endpoint para receber mensagens do Manychat (POST)
@app.route('/webhook', methods=['POST'])
def receive_message():
    data = request.get_json()
    print("Recebido do Manychat:", data)

    try:
        user_id = data['subscriber_id']
        message_text = data['data']['last_input_text']

        # [Lógica de Processamento da Mensagem]
        # Descomente a seção correta, dependendo da API que você for usar

        # Exemplo com OpenAI:
        # if OPENAI_API_KEY:
        #     response = openai.Completion.create(
        #         engine="text-davinci-003",
        #         prompt=message_text,
        #         max_tokens=100,
        #         user=str(user_id)
        #     )
        #     response_text = response.choices[0].text.strip()
        # else:
        #     response_text = "Erro: API da OpenAI não configurada."

        # Exemplo com Gemini:
        # if GOOGLE_API_KEY:
        #     chat = model.start_chat()
        #     response = chat.send_message(message_text)
        #     response_text = response.text
        # else:
        #     response_text = "Erro: API do Gemini não configurada."

        # Exemplo com Groq:
        # if GROQ_API_KEY:
        #     chat_completion = client.chat.completions.create(
        #         messages=[
        #             {
        #                 "role": "user",
        #                 "content": message_text,
        #             }
        #         ],
        #         model="llama2-70b-4096", # ou outro modelo disponível
        #     )
        #     response_text = chat_completion.choices[0].message.content
        # else:
        #     response_text = "Erro: API do Groq não configurada."

        # Exemplo de resposta fixa (para testes):
        response_text = "Olá de volta!"

        # Enviar resposta de volta para o Manychat
        send_message_to_manychat(user_id, response_text)

    except KeyError as e:
        print(f"Erro ao processar mensagem: {e}")
        return jsonify({"message": "Erro ao processar mensagem"}), 500

    return jsonify({"message": "Mensagem processada!"}), 200

def send_message_to_manychat(user_id, message):
    url = f"https://api.manychat.com/fb/subscriber/sendContent"
    headers = {
        "Authorization": f"Bearer {MANYCHAT_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "subscriber_id": user_id,
        "message": {
            "text": message
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print(f"Mensagem enviada com sucesso para {user_id}")
    else:
        print(f"Erro ao enviar mensagem para o Manychat: {response.status_code} - {response.text}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False) # debug=False para produção