from flask import Flask, request
import openai
import unicodedata
import os

OPEN_AI_API_KEY = os.environ['OPEN_AI_API_KEY']
app = Flask(__name__)
app.json.ensure_ascii = False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return '<h1>Hello World</h1>'
    else:
        meal_type = request.form.get('meal_type', '朝食')
        dish_num = request.form.get('dish_num', 3)
        tastes = request.form.get('tastes', ['辛い'])
        main_dish = request.form.get('main_dish', '肉')
        preference = request.form.get('preference', 'ニンジンを使いたい')
        print(meal_type, dish_num, tastes, main_dish, preference)

        response = make_response(meal_type, dish_num, tastes, main_dish, preference)
        return response


def make_response(meal_type, dish_num, tastes, main_dish, preference):
    question = f"以下の条件で健康バランスの良い{meal_type}の献立とその原材料・料理手順を提案してください。また出力はフォーマットに則って、それ以外の言葉は喋らないで。'フォーマット'の部分は返答には入れないで。\n## 条件\n品数： {dish_num}\n味の好み： {tastes}\nメイン： {main_dish}\nその他要望： {preference}\n\n## フォーマット\n料理名1：〇〇\n原材料：〇〇\n手順：〇〇\n料理名2：〇〇\n原材料：〇〇\n手順：〇〇\n"
    menu_text = ask_gpt(question)
    print("menu_text:", menu_text)
    response = []
    for line in menu_text.split("料理名"):
        if (line == ""):
            continue
        if (line[0] != ":") and (not line[0].isdigit()):
            continue
        try:
            line = line.split(':', 1)[1]
            print("line:", line)
            splited_line = line.split("原材料:")
            splited_line[1] = "原材料：" + splited_line[1]
            response.append({"title": splited_line[0].replace(" ", "").replace("\n", ""), "description": splited_line[1]})
        except BaseException as e:
            print(e)
            break
    return response


def ask_gpt(question):
    openai.api_key = OPEN_AI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": 'あなたは日本人のユーザーから食べたいものや好みを聞いて1食分の献立とその原材料・料理手順を教えるアプリです'},
            {"role": "assistant",
                "content": '了解しました。私はそのようなリクエストを処理できるようになります。ユーザーが食べたいものや好みを教えてくれたら、それに基づいて献立とその原材料・料理手順を提案できます。では、お気軽に食べたいものや好みを教えてください！'},
            {'role': 'user', 'content': question}
        ],
    )

    selected_response = response.choices[0]
    reply_text = unicodedata.normalize('NFKC', selected_response.message.content)
    return reply_text


if __name__ == "__main__":
    app.run(debug=True)
