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
st.set_page_config(layout="wide")
st.title("有機化合物 系統図トレーニング")

chart_types = chart_map_df["chart_type"].dropna().unique().tolist()

selected_chart = st.selectbox(
    "練習する系統図を選んでください",
    chart_types
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
        "label": row["condition"],
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

            # 1つ目の生成物と
            # 2つ目の反応物が同じなら連続反応
            if first_connection["to"] == second_connection["from"]:
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
    st.markdown(
        """
        <style>
        h1 {
        font-size: 2rem !important;
        text-align: center;
        }
        .compound {
            font-size: 25px;
            font-weight: 700;
            text-align: center;
            padding: 12px;
        }

        .condition {
            font-size: 18px;
            text-align: center;
            color: #555;
            padding: 4px;
        }
        .blank {
            font-size: 25px;
            font-weight: 700;
            text-align: center;
            color: #c62828;
            border: 2px dashed #c62828;
            border-radius: 10px;
            padding: 8px 12px;
            margin: 0;
            background-color: #fff5f5;
        }
        .answer {
            font-size: 25px;
            font-weight: 700;
            text-align: center;
            border: 2px solid #2e8b57;
            border-radius: 10px;
            padding: 8px 12px;
            margin: 0;
            background-color: #eefaf3;
            color: #000000;
        }
        .reaction-row {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 12px;
            margin: 2px 0;
        }
        .condition-box {
            min-width: 130px;
        }
        .arrow {
            font-size: 46px;
            font-weight: 800;
            line-height: 1;
        }
        """,
        unsafe_allow_html=True,
    )

    def show_compound(key):
        compound_id = question[key]
        value = compounds[compound_id]["name"]
        image_path = compounds[compound_id]["image"]

        with st.container(border=True):
            if hidden_part == key and not st.session_state.show_answer:
                st.markdown(
                    '<div class="blank">？</div>',
                    unsafe_allow_html=True,
                )
            elif hidden_part == key:
                st.markdown(
                    f'<div class="answer">{value}</div>',
                    unsafe_allow_html=True,
                )

                left, center, right = st.columns([1, 3, 1])

                with center:
                    st.image(image_path, width=260)

                memo = compounds[compound_id]["memo"]

                if pd.notna(memo) and str(memo).strip() != "":
                    st.info(f"メモ：{memo}")

            else:
                st.markdown(
                    f'<div class="compound">{value}</div>',
                    unsafe_allow_html=True,
                )

                left, center, right = st.columns([1, 3, 1])

                with center:
                    st.image(image_path, width=260)

    def show_condition(key):
        reaction_id = question[key]
        value = reactions[reaction_id]["label"]

        if hidden_part == key and not st.session_state.show_answer:
            condition_html = (
                '<div class="blank condition-box">反応条件は？</div>'
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
    st.subheader("復習リスト")

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
                display_name = reactions[item["item_id"]]["label"]
                item_label = "反応条件"

            st.write(f"{item_label}：「{display_name}」")


left_col, right_col = st.columns([3, 1])

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

            st.write(
                f"問題 {st.session_state.quiz_number + 1}"
                f" / {len(st.session_state.quiz_items)}"
            )

            if hidden_part in ["before", "answer", "after"]:
                st.info("「？」の化合物名と構造式の両方を答えてください。")

            show_question(question, hidden_part)

            if st.button("答えを見る"):
                st.session_state.show_answer = True
                st.rerun()

            if st.session_state.show_answer:
                st.write("自己評価")

                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("できた"):
                        st.session_state.quiz_number += 1
                        st.session_state.show_answer = False
                        st.rerun()

                with col2:
                    if st.button("微妙"):
                        st.session_state.quiz_number += 1
                        st.session_state.show_answer = False
                        st.rerun()

                with col3:
                    if st.button("できなかった"):
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

            st.write(
                f"復習 {st.session_state.review_number + 1}"
                f" / {len(st.session_state.review_list)}"
            )

            if hidden_part in ["before", "answer", "after"]:
                st.info("「？」の化合物名と構造式の両方を答えてください。")

            show_question(question, hidden_part)
            if st.button("答えを見る"):
                st.session_state.show_answer = True
                st.rerun()

            if st.session_state.show_answer:
                st.write("自己評価")

                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("できた"):
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
                    if st.button("微妙"):
                        st.session_state.review_number += 1
                        st.session_state.show_answer = False
                        st.rerun()

                with col3:
                    if st.button("できなかった"):
                        st.session_state.review_number += 1
                        st.session_state.show_answer = False
                        st.rerun()

with right_col:
    show_review_list()
