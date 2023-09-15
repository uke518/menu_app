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
        meal_type = request.form.get('meal_type')
        dish_num = request.form.get('dish_num', 3)
        tastes = request.form.get('tastes', ['辛い'])
        main_dish = request.form.get('main_dish', '肉')
        preference = request.form.get('preference', 'ニンジンを使いたい')

        dish_list = make_dish_list(meal_type, dish_num, tastes, main_dish, preference)
        print(dish_list)
        descriptions = make_descriptions(dish_list)
        response = []
        for dish, description in zip(dish_list, descriptions):
            response.append({"title": dish, "description": description})
        return response


def make_dish_list(meal_type, dish_num, tastes, main_dish, preference):
    question = f"以下の条件で健康バランスの良い{meal_type}の献立を提案してください。。また出力はフォーマットに則って、それ以外の言葉は喋らないで。以下の条件で朝食の献立を考えてください。また出力はフォーマットに則って、それ以外の言葉は喋らないで\n。## 条件\n品数： {dish_num}\n味の好み： {tastes}\nメイン： {main_dish}\nその他要望： {preference}\n\n## フォーマット\n料理名1：〇〇\n料理名2：〇〇\n料理名3：〇〇\n..."
    menu_text = ask_gpt(question)
    dish_list = []
    for line in menu_text.split("\n"):
        try:
            print(line.split(":"))
            if '料理名' in line.split(":")[0]:
                dish_list.append(line.split(":")[1])
        except BaseException:
            break
    dish_list = [dish.strip() for dish in dish_list]
    return dish_list


def make_descriptions(dish_list):
    descriptions = []
    for dish in dish_list:
        question = f"{dish}の原材料と料理手順を教えて。出力はフォーマットに則って、それ以外の言葉は喋らないで。n## フォーマット\n原材料：〇〇\n手順：〇〇"
        description = ask_gpt(question)
        print(description)
        descriptions.append(description)
    print(descriptions)
    return descriptions


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
    reply_text = unicodedata.normalize('NFKC', selected_response.message.content)
    return reply_text


if __name__ == "__main__":
    app.run(debug=True)
