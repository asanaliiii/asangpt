import os
import requests
from flask import Flask, render_template, request, jsonify

# Явно указываем Flask, где искать папку templates
current_dir = os.path.dirname(os.path.abspath(__file__))
template_folder = os.path.join(current_dir, '../templates')

app = Flask(__name__, template_folder=template_folder)

# bro hahahahaha in deployed site in vercel and i made environment
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Ошибка загрузки шаблона index.html: {str(e)}", 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json or {}
        user_message = data.get('message', '')
        history = data.get('history', [])

        if not user_message:
            return jsonify({'error': 'Сообщение не может быть пустым'}), 400

        # Формируем историю в формате, который требует официальный API Gemini
        contents = []
        for msg in history:
            role = "user" if msg.get("role") == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg.get("content", " ")}]})
        
        # Добавляем текущее сообщение пользователя
        contents.append({"role": "user", "parts": [{"text": user_message}]})

        # Отправляем прямой HTTP-запрос к Google API без лишних библиотек
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": contents}

        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()

        # Достаем текст ответа из структуры Google
        try:
            ai_text = res_data['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            print(f"Ошибка ответа API: {res_data}")
            return jsonify({'error': 'Google API вернул пустой или некорректный ответ.'}), 502

        return jsonify({'response': ai_text})

    except Exception as e:
        print(f"Ошибка на сервере: {e}")
        return jsonify({'error': 'Внутренняя ошибка сервера.'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
