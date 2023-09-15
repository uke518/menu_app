from flask import Flask, request, jsonify
import openai

OPEN_AI_API_KEY = ''
app = Flask(__name__)
app.json.ensure_ascii = False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return ask_gpt(1, 1, 1, 1, 1)
    else:
        meal_type = request.form.get('meal_type')
        dish_num = request.form.get('dish_num')
        tastes = request.form.get('tastes')
        main_dish = request.form.get('main_dish')
        preference = request.form.get('preference')

    question = make_question(meal_type, dish_num, tastes, main_dish, preference)
    gpt_answer = ask_gpt(question)
    return gpt_answer


def make_question(meal_type, dish_num, tastes, main_dish, preference):
    question = f"以下の条件で健康バランスの良い{meal_type}の献立とその材料、調理手順を提案してください。。また出力はフォーマットに則って、それ以外の言葉は喋らないで。以下の条件で朝食の献立を考えてください。また出力はフォーマットに則って、それ以外の言葉は喋らないで\n。## 条件\n品数： {dish_num}\n味の好み： {tastes}\nメイン： {main_dish}\nその他要望： {preference}\n\n## フォーマット\n料理名1：〇〇\n料理名2：〇〇\n料理名3：〇〇..."
    return question


def ask_gpt(question):
    openai.api_key = OPEN_AI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": 'あなたは日本人のユーザーから食べたいものや好みを聞いて1食分の献立を教えるアプリです'},
            {"role": "assistant",
                "content": '了解しました。私はそのようなリクエストを処理できるようになります。ユーザーが食べたいものや好みを教えてくれたら、それに基づいて献立を提案できます。では、お気軽に食べたいものや好みを教えてください！'},
            {'role': 'user', 'content': question}
        ],
    )

    selected_response = response.choices[0]
    reply_text = selected_response.message.content
    return reply_text


if __name__ == "__main__":
    app.run(debug=True)
