import pandas as pd
import streamlit as st
import random


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
        padding-top: 1.5rem !important;
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
        padding: 0;
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
    }
    .reaction-row {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 12px;
        margin: 10px;
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
    }

    /* 縦向き：化合物名と画像を上下に並べる */
    @media (orientation: portrait) {
        div[class*="st-key-compound_"] div[data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            align-items: center !important;
            gap: 4px !important;
        }

        div[class*="st-key-compound_"] div[data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
            max-width: 100% !important;
            flex: 0 0 100% !important;
        }

        div[class*="st-key-compound_"] .compound,
        div[class*="st-key-compound_"] .answer {
            width: 100%;
            white-space: nowrap;
            text-align: center;
            box-sizing: border-box;
        }

        div[class*="st-key-compound_"] div[data-testid="stImage"] img {
            display: block;
            width: auto !important;
            max-width: 180px !important;
            height: auto !important;
            margin: 0 auto;
        }
    }

    /* iPad横向きなど、高さが低い横長画面だけをコンパクトにする */
    @media (orientation: landscape) and (max-height: 1100px) {
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

        div[class*="st-key-compound_"] .answer {
            padding: 3px 8px !important;
            margin: 2px !important;
        }

        .reaction-row {
            margin: 0 !important;
            gap: 6px !important;
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

title_col, chart_col = st.columns([3, 1])

with title_col:
    st.title("有機化合物 系統図トレーニング")

with chart_col:
    selected_chart = st.selectbox(
        "練習する系統図を選んでください",
        chart_types,
        label_visibility="collapsed",
    )


# =========================
# 系統図を切り替えたらクイズ状態をリセット
# =========================

if "selected_chart" not in st.session_state:
    st.session_state.selected_chart = selected_chart

elif st.session_state.selected_chart != selected_chart:
    st.session_state.selected_chart = selected_chart

    st.session_state.mode = "normal"
    st.session_state.quiz_number = 0
    st.session_state.show_answer = False
    st.session_state.review_list = []
    st.session_state.review_number = 0
    st.session_state.finished_once = False

    if "quiz_items" in st.session_state:
        del st.session_state.quiz_items

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

hidden_parts = [
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


def make_quiz_items():
    items = []

    for question in questions:
        for hidden_part in hidden_parts:
            items.append(
                {
                    "question_id": question["id"],
                    "hidden_part": hidden_part,
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


def show_question(question, hidden_part):
    def show_compound(key):
        compound_id = question[key]
        value = compounds[compound_id]["name"]
        image_path = compounds[compound_id]["image"]

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
                    st.image(image_path, width=260)

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
                    st.image(image_path, width=260)

    def show_condition(key):
        reaction_id = question[key]
        reaction = reactions[reaction_id]

        reaction_type = reaction["reaction_type"]
        condition = reaction["condition"]

        value = f"{reaction_type}｜{condition}"

        if hidden_part == key and not st.session_state.show_answer:
            condition_html = (
                '<div class="blank condition-box">反応名・反応条件は？</div>'
            )

        elif hidden_part == key:
            condition_html = (
                f'<div class="answer condition-box">{value}</div>'
            )
        else:
            condition_html = (
                f'<div class="condition condition-box">{value}</div>'
            )

        st.markdown(
            f"""
            <div class="reaction-row">
                <div class="arrow">↓</div>
                {condition_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if hidden_part == key and st.session_state.show_answer:
            memo = reactions[reaction_id]["memo"]

            if pd.notna(memo) and str(memo).strip() != "":
                st.info(f"メモ：{memo}")
            
    show_compound("before")
    show_condition("condition1")
    show_compound("answer")
    show_condition("condition2")
    show_compound("after")


def get_question_by_id(question_id):
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
        for hidden_part in hidden_parts:
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
                display_name = (
                    f'{reaction["reaction_type"]}｜{reaction["condition"]}'
                )
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
                st.success("🎉 完成！おめでとうございます！")
                st.info(
                    "この画面をスクリーンショットして先生に見せたら、"
                    "平常点を追加します。"
                )

            if st.button("もう一度最初からやりましょう"):
                st.session_state.mode = "normal"
                st.session_state.quiz_items = make_quiz_items()
                st.session_state.quiz_number = 0
                st.session_state.show_answer = False
                st.session_state.review_list = []
                st.session_state.review_number = 0
                st.session_state.finished_once = False
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
                st.info("「？」の化合物名と構造式の両方を答えてください。")

            show_question(question, hidden_part)

            if st.button("答えを見る", key="btn_answer"):
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
            st.success("🎉 完成！おめでとうございます！")
            st.info(
                "この画面をスクリーンショットして先生に見せたら、"
                "平常点を追加します。"
            )

            if st.button("もう一度最初からやりましょう"):
                st.session_state.mode = "normal"
                st.session_state.quiz_items = make_quiz_items()
                st.session_state.quiz_number = 0
                st.session_state.show_answer = False
                st.session_state.review_number = 0
                st.session_state.finished_once = False
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
                st.info("「？」の化合物名と構造式の両方を答えてください。")

            show_question(question, hidden_part)
            if st.button("答えを見る", key="btn_answer"):
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
        height=1000,
        border=True,
        key="review_scroll",
    ):
        show_review_list()
