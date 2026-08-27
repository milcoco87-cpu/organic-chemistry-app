import pandas as pd
import streamlit as st
import random
import re
from datetime import datetime, timezone, timedelta


# =========================
# CSV読み込み
# =========================

compounds_df = pd.read_csv("compounds.csv")
reactions_df = pd.read_csv("reactions.csv")
chart_map_df = pd.read_csv("compound_chart_map.csv")



# =========================
# 読み込み確認
# =========================
st.set_page_config(
    layout="wide",
    )

# =========================
# 画面全体のデザイン
# =========================
st.markdown(
    """
    <style>
    h1,
    h1 span {
        font-size: 40px;
        text-align: center;
        color: #ffffff !important;
        padding: 10px;
        margin: 1px;
        background-color: #000000;
    }
    .block-container {
        padding-top: 4rem !important;
    }
    div[data-testid="stSelectbox"] label p {
        font-size: 20px !important;
        font-weight: 600 !important;
    }
    div[data-testid="stButton"] button {
        min-height: 44px;
        padding: 8px 18px;
        border-radius: 8px;
    }
    div[data-testid="stButton"] button p {
        font-size: 18px !important;
        font-weight: 600 !important;
    }

    div[class*="st-key-compound_"]{
        background-color: #FFFFFF;
        border-width: 10px;
        border: 3px solid #555555;
        border-radius: 10px !important;
        min-height: 105px;
        display: flex;
        align-items: center;
    }


    div[class*="st-key-btn_good"] button {
        border: 3px solid #2e7d32 !important;
        background-color: #e8f5e9 !important;
        color: #1b5e20 !important;
    }
    div[class*="st-key-btn_mid"] button {
        border: 3px solid #ed8b00 !important;
        background-color: #fff8e1 !important;
        color: #8a4f00 !important;
    }
    div[class*="st-key-btn_bad"] button {
        border: 3px solid #c62828 !important;
        background-color: #ffebee !important;
        color: #b71c1c !important;
    }

    div[class*="st-key-btn_good"] button,
    div[class*="st-key-btn_mid"] button,
    div[class*="st-key-btn_bad"] button {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 150px;
}

    div[class*="st-key-btn_answer"] {
        width: 100%;
        margin-top: 20px;
        margin-bottom: 18px;
    }

    div[class*="st-key-btn_answer"] button {
        display: block;
        margin-left: auto;
        margin-right: auto;
        min-width: 300px;
        min-height: 52px;
        border: 5px solid #00008b !important;
        background-color: #00008b !important;
        color: #ffffff !important;
        font-weight: bold!important;
    }

    .compound {
        font-size: 25px;
        font-weight: 900;
        text-align: center;
        padding: 0 8px;
        line-height: 1.2;
        overflow-wrap: anywhere;
    }
    .compound.long-name,
    .answer.long-name {
        font-size: 20px !important;
    }

    .condition {
        font-size: 20px;
        font-weight: 600;
        text-align: center;
        color: #222222;
        padding: 20px;
    }
    .blank {
        font-size: 25px;
        font-weight: 700;
        text-align: center;
        color: #c62828;
        border: 3px dashed #c62828;
        border-radius: 10px;
        background-color: #fff5f5;
        box-sizing: border-box;
    }
    .answer {
        font-size: 25px;
        font-weight: 700;
        text-align: center;
        border: 2px solid #2e8b57;
        border-radius: 10px;
        padding: 8px 12px;
        margin: 10px;
        background-color: #eefaf3;
        color: #000000;
        line-height: 1.2;
        overflow-wrap: anywhere;
    }
    .reaction-row {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 12px;
        margin: 10px;
    }
    .co-reactant {
        font-size: 18px;
        font-weight: 700;
        text-align: right;
        white-space: nowrap;
        color: #222222;
    }
    .co-reactant-arrow {
        font-size: 30px;
        font-weight: 800;
        line-height: 1;
        white-space: nowrap;
    }
    .vertical-arrow-wrap {
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 36px;
    }
    .condition-box {
        min-width: 5em;
        padding: 8px 12px;
    }
    .arrow {
        font-size: 50px;
        font-weight: 800;
        line-height: 1;
    }
    .label-subtitle {
        font-size: 30px;
        font-weight: 700;
        text-align: center;
        font-weight: bold;
    }
    .question-number {
        font-size: 18px;
    }
    .self-rating-title {
        font-size: 30px;
        font-weight: 700;
        text-align: center;
        margin: 8px 0 10px;
    }
    /* ========================================
    画面の向きによる化合物名・画像の並び替え
    ======================================== */

    /* 化合物名と構造式画像の2列を中央にそろえる */
    div[class*="st-key-compound_"] div[data-testid="stHorizontalBlock"] {
        align-items: center;
    }

    div[class*="st-key-compound_"] div[data-testid="stImage"] {
        display: flex;
        justify-content: center;
        padding: 10px 14px;
        box-sizing: border-box;
    }


    /* iPad横向きなど、高さが低い横長画面だけをコンパクトにする */
    @media (orientation: landscape) and (max-height: 1100px) and (hover: none) and (pointer: coarse) {
        .block-container {
            padding-top: 4rem !important;
            padding-bottom: 0.5rem !important;
        }

        .block-container div[data-testid="stVerticalBlock"] {
            gap: 0.35rem !important;
        }

        h1,
        h1 span {
            font-size: 26px !important;
            line-height: 1.2 !important;
            padding: 6px 4px !important;
            overflow: visible !important;
        }

        div[data-testid="stSelectbox"] label p {
            font-size: 16px !important;
        }

        div[class*="st-key-compound_"] {
            min-height: 92px !important;
        }

        div[class*="st-key-compound_"] div[data-testid="stImage"] img {
            width: auto !important;
            max-width: 140px !important;
            max-height: 70px !important;
            object-fit: contain;
        }

        div[class*="st-key-compound_"] .compound,
        div[class*="st-key-compound_"] .answer {
            font-size: 19px !important;
        }

        div[class*="st-key-compound_"] .compound.long-name,
        div[class*="st-key-compound_"] .answer.long-name {
            font-size: 16px !important;
        }

        div[class*="st-key-compound_"] .answer {
            padding: 3px 8px !important;
            margin: 2px !important;
        }

        .reaction-row {
            margin: 0 !important;
            gap: 6px !important;
        }

        .co-reactant {
            font-size: 14px !important;
        }

        .co-reactant-arrow {
            font-size: 22px !important;
        }

        .condition,
        .condition-box {
            font-size: 16px !important;
            padding: 2px 6px !important;
        }

        .arrow {
            font-size: 30px !important;
        }

        div[data-testid="stAlert"] {
            padding: 0.4rem 0.7rem !important;
        }

        .label-subtitle {
            font-size: 24px !important;
        }

        div[class*="st-key-btn_answer"] {
            margin-top: 8px !important;
            margin-bottom: 8px !important;
        }

        div[class*="st-key-btn_answer"] button {
            min-height: 38px !important;
        }

        .self-rating-title {
            font-size: 24px !important;
            margin: 3px 0 5px !important;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)

chart_types = chart_map_df["chart_type"].dropna().unique().tolist()
question_styles = ["通常モード", "構造式モード"]

title_col, control_col = st.columns([2, 1])

with title_col:
    st.title("有機化合物 系統図トレーニング")

with control_col:
    selected_chart = st.selectbox(
        "練習する系統図を選んでください",
        chart_types,
    )
    selected_question_style = st.selectbox(
        "出題モードを選んでください",
        question_styles,
    )

student_name = st.text_input(
    "氏名を入力してください",
    key="student_name_input",
    placeholder="例：山田 花子",
)


# =========================
# 系統図を切り替えたらクイズ状態をリセット
# =========================

if "selected_chart" not in st.session_state:
    st.session_state.selected_chart = selected_chart

if "selected_question_style" not in st.session_state:
    st.session_state.selected_question_style = selected_question_style

if (
    st.session_state.selected_chart != selected_chart
    or st.session_state.selected_question_style != selected_question_style
):
    st.session_state.selected_chart = selected_chart
    st.session_state.selected_question_style = selected_question_style

    st.session_state.mode = "normal"
    st.session_state.quiz_number = 0
    st.session_state.show_answer = False
    st.session_state.review_list = []
    st.session_state.review_number = 0
    st.session_state.finished_once = False
    st.session_state.completed_at = None
    st.session_state.run_name = ""
    st.session_state.run_chart = ""
    st.session_state.run_question_style = ""

    if "quiz_items" in st.session_state:
        del st.session_state.quiz_items

    if "two_questions" in st.session_state:
        del st.session_state.two_questions

    st.rerun()



# st.subheader("compounds.csv")
# st.dataframe(compounds_df)

# st.subheader("reactions.csv")
# st.dataframe(reactions_df)

# st.subheader("compound_chart_map.csv")
# st.dataframe(chart_map_df)




compounds = {}

for _, row in compounds_df.iterrows():
    compounds[row["compound_id"]] = {
    "name": row["name_ja"],
    "image": "images/" + row["image"],
    "memo": row["memo"],
}

# =========================
# reactions.csv から反応辞書を作る
# =========================

reactions = {}

for _, row in reactions_df.iterrows():
    reactions[row["reaction_id"]] = {
        "condition": row["condition"],
        "reaction_type": row["reaction_type"],
        "memo": row["memo"],
    }


def clean_text(value):
    """NaN・None・空文字を画面に表示しないための整形。"""
    if pd.isna(value):
        return ""
    return str(value).strip()


def extract_co_reactant(memo):
    """memo の「共反応物：○○」から共反応物名を取り出す。"""
    memo_text = clean_text(memo)
    if not memo_text:
        return ""

    match = re.search(r"共反応物[：:]\s*([^\n、,]+)", memo_text)
    if match:
        return match.group(1).strip()

    return ""


def clean_reaction_memo(memo):
    """共反応物の記述は画面の横表示に回し、その他のメモだけ残す。"""
    memo_text = clean_text(memo)
    if not memo_text:
        return ""

    memo_text = re.sub(r"共反応物[：:]\s*[^\n、,]+", "", memo_text)
    memo_text = memo_text.strip(" 、,\n")
    return memo_text


def format_reaction_label(reaction):
    """反応名と条件を整形。共反応物と同じ条件文字列は重複表示しない。"""
    reaction_type = clean_text(reaction["reaction_type"])
    condition = clean_text(reaction["condition"])
    co_reactant = extract_co_reactant(reaction["memo"])

    if co_reactant and condition == co_reactant:
        condition = ""

    parts = [part for part in [reaction_type, condition] if part]
    return "｜".join(parts)
# =========================
# 選択した系統図の化合物IDを取得
# =========================

selected_compound_ids = set(
    chart_map_df[
        chart_map_df["chart_type"] == selected_chart
    ]["compound_id"]
)

# =========================
# reactions.csv から反応のつながりを作る
# =========================

connections = []

for _, row in reactions_df.iterrows():

    if (
        row["reactant_id"] in selected_compound_ids
        and row["product_id"] in selected_compound_ids
    ):
        connections.append(
            {
                "from": row["reactant_id"],
                "reaction": row["reaction_id"],
                "to": row["product_id"],
            }
        )

# =========================
# 連続する2反応から問題を作る
# =========================

def make_questions_from_connections():
    generated_questions = []

    for first_connection in connections:
        for second_connection in connections:

             # 反応が連続し、出発物質と最終生成物が異なる場合だけ出題
            if (
                first_connection["to"] == second_connection["from"]
                and first_connection["from"] != second_connection["to"]
            ):
                generated_questions.append(
                    {
                        "id": len(generated_questions) + 1,
                        "before": first_connection["from"],
                        "condition1": first_connection["reaction"],
                        "answer": first_connection["to"],
                        "condition2": second_connection["reaction"],
                        "after": second_connection["to"],
                    }
                )

    return generated_questions

questions = make_questions_from_connections()


def make_two_compound_question(connection, hidden_compound_id):
    """3化合物ルートに入れない化合物用の、1反応だけの構造式問題。"""
    if connection["from"] == hidden_compound_id:
        hidden_part = "before"
    else:
        hidden_part = "after"

    return {
        "id": f"two_{connection['reaction']}_{hidden_compound_id}",
        "layout": "two",
        "before": connection["from"],
        "condition1": connection["reaction"],
        "after": connection["to"],
        "hidden_part": hidden_part,
    }

all_hidden_parts = [
    "before",
    "condition1",
    "answer",
    "condition2",
    "after",
]

part_names = {
    "before": "最初の化合物",
    "condition1": "1つ目の反応条件",
    "answer": "中央の化合物",
    "condition2": "2つ目の反応条件",
    "after": "最後の化合物",
}


def get_target_hidden_parts():
    if selected_question_style == "構造式モード":
        return ["before", "answer", "after"]
    return all_hidden_parts


def make_quiz_items():
    # 構造式モード：
    # 選択した系統図に登録されている化合物を、1周につき各1回出題する。
    # まず3化合物ルートから候補を集め、そこに入れない化合物は
    # 1反応だけの2化合物表示（例：55→56、57→58）で補う。
    if selected_question_style == "構造式モード":
        candidates_by_compound = {}

        # 3化合物ルートから候補を集める
        for question in questions:
            for hidden_part in ["before", "answer", "after"]:
                compound_id = question[hidden_part]
                candidates_by_compound.setdefault(compound_id, []).append(
                    {
                        "question_id": question["id"],
                        "hidden_part": hidden_part,
                        "layout": "three",
                    }
                )

        # 3化合物ルートに入らない化合物は、単独反応から候補を作る
        two_questions = {}
        for compound_id in selected_compound_ids:
            if compound_id in candidates_by_compound:
                continue

            matching_connections = [
                connection
                for connection in connections
                if (
                    connection["from"] == compound_id
                    or connection["to"] == compound_id
                )
            ]

            if matching_connections:
                for connection in matching_connections:
                    q = make_two_compound_question(connection, compound_id)
                    two_questions[q["id"]] = q
                    candidates_by_compound.setdefault(compound_id, []).append(
                        {
                            "question_id": q["id"],
                            "hidden_part": q["hidden_part"],
                            "layout": "two",
                        }
                    )

        # 後で get_question_by_id から参照できるよう保存
        st.session_state.two_questions = two_questions

        items = [
            random.choice(candidates)
            for candidates in candidates_by_compound.values()
        ]

        random.shuffle(items)
        return items

    # 通常モード：
    # 従来どおり、5か所すべてを出題対象にする。
    items = []

    for question in questions:
        for hidden_part in all_hidden_parts:
            items.append(
                {
                    "question_id": question["id"],
                    "hidden_part": hidden_part,
                    "layout": "three",
                }
            )

    random.shuffle(items)
    return items


if "mode" not in st.session_state:
    st.session_state.mode = "normal"

if "quiz_items" not in st.session_state:
    st.session_state.quiz_items = make_quiz_items()

if "quiz_number" not in st.session_state:
    st.session_state.quiz_number = 0

if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

if "review_list" not in st.session_state:
    st.session_state.review_list = []

if "review_number" not in st.session_state:
    st.session_state.review_number = 0

if "finished_once" not in st.session_state:
    st.session_state.finished_once = False

if "completed_at" not in st.session_state:
    st.session_state.completed_at = None

if "run_name" not in st.session_state:
    st.session_state.run_name = ""

if "run_chart" not in st.session_state:
    st.session_state.run_chart = ""

if "run_question_style" not in st.session_state:
    st.session_state.run_question_style = ""


def lock_run_info():
    """その回の氏名・系統・出題モードを固定する。"""
    if st.session_state.run_name == "":
        st.session_state.run_name = st.session_state.student_name_input.strip()

    if st.session_state.run_chart == "":
        st.session_state.run_chart = selected_chart

    if st.session_state.run_question_style == "":
        st.session_state.run_question_style = selected_question_style


def show_completion_certificate():
    """完成画面に、その回の完了証明を表示する。"""
    lock_run_info()

    if st.session_state.completed_at is None:
        st.session_state.completed_at = datetime.now(
            timezone(timedelta(hours=9))
        ).strftime("%Y/%m/%d %H:%M:%S")

    st.success("🎉 完成！おめでとうございます！")

    certificate_lines = [
        f"**氏名：{st.session_state.run_name}**",
        f"**系統：{st.session_state.run_chart}**",
    ]

    # 将来「出題方法」を実装したら、run_question_style を保存するだけで
    # この完了証明にも自動で1行追加できます。
    if st.session_state.get("run_question_style"):
        certificate_lines.append(
            f"**出題方法：{st.session_state.run_question_style}**"
        )

    certificate_lines.append(
        f"**完了日時：{st.session_state.completed_at}**"
    )

    st.info("\n\n".join(certificate_lines))
    st.info(
        "この画面をスクリーンショットして先生に見せたら、"
        "平常点を追加します。"
    )


def show_question(question, hidden_part):
    def show_compound(key):
        compound_id = question[key]
        value = compounds[compound_id]["name"]
        image_path = compounds[compound_id]["image"]
        name_class = "long-name" if len(str(value)) >= 12 else ""

        with st.container(border=False, key=f"compound_{key}"):
            if hidden_part == key and not st.session_state.show_answer:
                st.markdown(
                    '<div class="blank">？</div>',
                    unsafe_allow_html=True,
                )
            elif hidden_part == key:
                name_col, image_col = st.columns([2, 3])

                with name_col:
                    st.markdown(
                        f'<div class="answer">{value}</div>',
                        unsafe_allow_html=True,
                    )

                with image_col:
                    st.image(image_path)

                memo = compounds[compound_id]["memo"]

                if pd.notna(memo) and str(memo).strip() != "":
                    st.info(f"メモ：{memo}")

            else:
                name_col, image_col = st.columns([2, 3])

                with name_col:
                    st.markdown(
                        f'<div class="compound">{value}</div>',
                        unsafe_allow_html=True,
                    )

                with image_col:
                    st.image(image_path)

    def show_condition(key):
        reaction_id = question[key]
        reaction = reactions[reaction_id]

        value = format_reaction_label(reaction)
        co_reactant = extract_co_reactant(reaction["memo"])

        if hidden_part == key and not st.session_state.show_answer:
            condition_html = (
                '<div class="blank condition-box">反応名・反応条件は？</div>'
            )
            co_reactant_html = ""

        elif hidden_part == key:
            condition_html = (
                f'<div class="answer condition-box">{value}</div>'
            )
            if co_reactant:
                co_reactant_html = (
                    f'<div class="co-reactant">{co_reactant}</div>'
                    '<div class="co-reactant-arrow">→</div>'
                )
            else:
                co_reactant_html = ""
        else:
            condition_html = (
                f'<div class="condition condition-box">{value}</div>'
            )
            if co_reactant:
                co_reactant_html = (
                    f'<div class="co-reactant">{co_reactant}</div>'
                    '<div class="co-reactant-arrow">→</div>'
                )
            else:
                co_reactant_html = ""

        reaction_html = (
            f'<div class="reaction-row">'
            f'{co_reactant_html}'
            f'<div class="vertical-arrow-wrap">'
            f'<div class="arrow">↓</div>'
            f'</div>'
            f'{condition_html}'
            f'</div>'
        )

        st.markdown(
            reaction_html,
            unsafe_allow_html=True,
        )

        if hidden_part == key and st.session_state.show_answer:
            memo = clean_reaction_memo(reaction["memo"])

            if memo:
                st.info(f"メモ：{memo}")
            
    if question.get("layout") == "two":
        show_compound("before")
        show_condition("condition1")
        show_compound("after")
    else:
        show_compound("before")
        show_condition("condition1")
        show_compound("answer")
        show_condition("condition2")
        show_compound("after")


def get_question_by_id(question_id):
    if isinstance(question_id, str) and question_id.startswith("two_"):
        return st.session_state.two_questions[question_id]

    return next(
        question
        for question in questions
        if question["id"] == question_id
    )

def make_review_item(question, hidden_part):
    if hidden_part in ["before", "answer", "after"]:
        item_type = "compound"
        item_id = question[hidden_part]
    else:
        item_type = "reaction"
        item_id = question[hidden_part]

    return {
        "item_type": item_type,
        "item_id": item_id,

        # 復習問題を表示するための代表的な系統図
        "question_id": question["id"],
        "hidden_part": hidden_part,
    }


def find_review_candidates(review_item):
    candidates = []

    for question in questions:
        for hidden_part in all_hidden_parts:
            if hidden_part in ["before", "answer", "after"]:
                item_type = "compound"
            else:
                item_type = "reaction"

            if (
                item_type == review_item["item_type"]
                and question[hidden_part] == review_item["item_id"]
            ):
                candidates.append(
                    {
                        "question_id": question["id"],
                        "hidden_part": hidden_part,
                    }
                )

    if review_item["item_type"] == "compound":
        for q in st.session_state.get("two_questions", {}).values():
            for hidden_part in ["before", "after"]:
                if q.get(hidden_part) == review_item["item_id"]:
                    candidates.append(
                        {
                            "question_id": q["id"],
                            "hidden_part": hidden_part,
                        }
                    )

    return candidates

def show_review_list():
    st.html(
        f'<span class="label-subtitle">【復習リスト】</span>'
    )
    st.caption("この欄は上下にスクロールできます。")
    if len(st.session_state.review_list) == 0:
        if not st.session_state.finished_once:
            st.write("まだ復習項目はありません。")
    else:
        st.info("復習リストがなくなるまで続けましょう。")

        for item in st.session_state.review_list:
            if item["item_type"] == "compound":
                display_name = compounds[item["item_id"]]["name"]
                item_label = "化合物名"
            else:
                reaction = reactions[item["item_id"]]
                display_name = format_reaction_label(reaction)
                co_reactant = extract_co_reactant(reaction["memo"])
                if co_reactant:
                    display_name += f"（共反応物：{co_reactant}）"
                item_label = "反応条件"

            st.write(f"{item_label}：「{display_name}」")


left_col, right_col = st.columns([2, 1])

with left_col:
    if st.session_state.mode == "normal":

        if st.session_state.quiz_number >= len(
            st.session_state.quiz_items
        ):
            st.session_state.finished_once = True

            st.success(
                f"全{len(st.session_state.quiz_items)}問終了しました！"
            )

            if len(st.session_state.review_list) > 0:
                if st.button("間違えた問題だけ復習する"):
                    random.shuffle(st.session_state.review_list)
                    st.session_state.mode = "review"
                    st.session_state.review_number = 0
                    st.session_state.show_answer = False
                    st.rerun()

            else:
                show_completion_certificate()

            if st.button("もう一度最初からやりましょう"):
                st.session_state.mode = "normal"
                st.session_state.quiz_items = make_quiz_items()
                st.session_state.quiz_number = 0
                st.session_state.show_answer = False
                st.session_state.review_list = []
                st.session_state.review_number = 0
                st.session_state.finished_once = False
                st.session_state.completed_at = None
                st.session_state.run_name = ""
                st.session_state.run_chart = ""
                st.session_state.run_question_style = ""
                st.rerun()

        else:
            quiz_item = st.session_state.quiz_items[
                st.session_state.quiz_number
            ]

            question = get_question_by_id(
                quiz_item["question_id"]
            )

            hidden_part = quiz_item["hidden_part"]

            st.html(
                f'<span class="label-subtitle">【問題】</span>'
                f'<span class="question-number"> '
                f"({st.session_state.quiz_number + 1}"
                f" / {len(st.session_state.quiz_items)})</span>",
            )

            if hidden_part in ["before", "answer", "after"]:
                if selected_question_style == "構造式モード":
                    st.info("「？」の構造式を書いてください。")
                else:
                    st.info("「？」の化合物名と構造式の両方を答えてください。")

            show_question(question, hidden_part)

            if st.button("答えを見る", key="btn_answer"):
                if st.session_state.student_name_input.strip() == "":
                    st.warning("氏名を入力してから始めてください。")
                else:
                    lock_run_info()
                    st.session_state.show_answer = True
                    st.rerun()


            if st.session_state.show_answer:
                st.html('<div class="self-rating-title">【自己評価】</div>')

                space1, col1, col2, col3, space2 = st.columns([1, 2, 2, 2, 1])
                with col1:
                    if st.button("できた", key="btn_good"):
                        st.session_state.quiz_number += 1
                        st.session_state.show_answer = False
                        st.rerun()

                with col2:
                    if st.button("微妙", key="btn_mid"):
                        st.session_state.quiz_number += 1
                        st.session_state.show_answer = False
                        st.rerun()

                with col3:
                    if st.button("できなかった", key="btn_bad"):
                        review_item = make_review_item(
                            question,
                            hidden_part,
                        )

                        already_registered = any(
                            item["item_type"] == review_item["item_type"]
                            and item["item_id"] == review_item["item_id"]
                            for item in st.session_state.review_list
                        )

                        if not already_registered:
                            st.session_state.review_list.append(review_item)
                        st.session_state.quiz_number += 1
                        st.session_state.show_answer = False
                        st.rerun()
    else:
        if len(st.session_state.review_list) == 0:
            show_completion_certificate()

            if st.button("もう一度最初からやりましょう"):
                st.session_state.mode = "normal"
                st.session_state.quiz_items = make_quiz_items()
                st.session_state.quiz_number = 0
                st.session_state.show_answer = False
                st.session_state.review_number = 0
                st.session_state.finished_once = False
                st.session_state.completed_at = None
                st.session_state.run_name = ""
                st.session_state.run_chart = ""
                st.session_state.run_question_style = ""
                st.rerun()

        else:
            if st.session_state.review_number >= len(
                st.session_state.review_list
            ):
                st.session_state.review_number = 0
                random.shuffle(st.session_state.review_list)

            review_item = st.session_state.review_list[
                st.session_state.review_number
            ]

            candidates = find_review_candidates(review_item)

            different_candidates = [
                candidate
                for candidate in candidates
                if candidate["question_id"] != review_item["question_id"]
            ]

            if len(different_candidates) > 0:
                selected_candidate = random.choice(different_candidates)
            else:
                selected_candidate = random.choice(candidates)

            question = get_question_by_id(
                selected_candidate["question_id"]
            )

            hidden_part = selected_candidate["hidden_part"]

            st.html(
                f'<span class="label-subtitle">復習</span>'
                f'<span class="question-number"> '
                f"{st.session_state.review_number + 1}"
                f" / {len(st.session_state.review_list)}</span>"
            )

            if hidden_part in ["before", "answer", "after"]:
                if st.session_state.get("run_question_style") == "構造式モード":
                    st.info("「？」の構造式を書いてください。")
                else:
                    st.info("「？」の化合物名と構造式の両方を答えてください。")

            show_question(question, hidden_part)
            if st.button("答えを見る", key="btn_answer"):
                if st.session_state.student_name_input.strip() == "":
                    st.warning("氏名を入力してから始めてください。")
                else:
                    lock_run_info()
                    st.session_state.show_answer = True
                    st.rerun()

            if st.session_state.show_answer:
                st.html('<div class="self-rating-title">【自己評価】</div>')

                space1, col1, col2, col3, space2 = st.columns([1, 2, 2, 2, 1])

                with col1:
                    if st.button("できた", key="btn_good"):
                        st.session_state.review_list.pop(
                            st.session_state.review_number
                        )
                        st.session_state.show_answer = False

                        if st.session_state.review_number >= len(
                            st.session_state.review_list
                        ):
                            st.session_state.review_number = 0

                        st.rerun()

                with col2:
                    if st.button("微妙", key="btn_mid"):
                        st.session_state.review_number += 1
                        st.session_state.show_answer = False
                        st.rerun()

                with col3:
                    if st.button("できなかった", key="btn_bad"):
                        st.session_state.review_number += 1
                        st.session_state.show_answer = False
                        st.rerun()

with right_col:
    with st.container(
        height=850,
        border=True,
        key="review_scroll",
    ):
        show_review_list()
