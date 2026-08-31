import pandas as pd
import streamlit as st
import random
import re
import json
import base64
import zlib
import secrets
from datetime import datetime, timezone, timedelta


# =========================
# CSV読み込み
# =========================

compounds_df = pd.read_csv("compounds.csv")
reactions_df = pd.read_csv("reactions.csv")
chart_map_df = pd.read_csv("compound_chart_map.csv")

# 旧CSVでも動くように、追加列がなければ補う
if "range_level" not in compounds_df.columns:
    compounds_df["range_level"] = ""

if "custom_a" not in reactions_df.columns:
    reactions_df["custom_a"] = False

if "custom_b" not in reactions_df.columns:
    reactions_df["custom_b"] = False



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
    div[data-testid="stSelectbox"] label p,
    div[data-testid="stTextInput"] label p {
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
    }

    /* 化合物ボックスの中身を上下中央にそろえる */
    div[class*="st-key-compound_"] > div[data-testid="stVerticalBlock"] {
        min-height: 99px;
        justify-content: center;
    }

    /* 「？」だけのときもボックス中央に置く */
    div[class*="st-key-compound_"] .blank {
        min-height: 95px;
        display: flex;
        align-items: center;
        justify-content: center;
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
    .question-prompt {
        font-size: 18px;
        margin-left: 16px;
        color: #1f5f99;
        font-weight: 600;
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

        div[data-testid="stSelectbox"] label p,
        div[data-testid="stTextInput"] label p {
            font-size: 16px !important;
        }

        div[class*="st-key-compound_"] {
            min-height: 92px !important;
        }

        div[class*="st-key-compound_"] > div[data-testid="stVerticalBlock"] {
            min-height: 86px !important;
            justify-content: center !important;
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

        .question-number,
        .question-prompt {
            font-size: 15px !important;
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

range_options = [
    "炭化水素まで",
    "エステルまで",
    "芳香族まで",
    "全部",
    "カスタムA",
    "カスタムB",
]


# =========================
# 途中経過の保存・復元
# =========================
# 進捗は2か所に保存する。
# 1) URL query parameter:
#    Wi-Fi切断・Streamlit再接続・リロード時の復元用
# 2) ブラウザ localStorage:
#    タブ/ブラウザを閉じて、同じ端末・同じブラウザで開き直した場合の復元用
#
# 氏名は保存しない。
#
# localStorage との通信には、iframe型の components.html() ではなく
# Streamlit Components V2 の双方向コンポーネントを使う。
PROGRESS_PARAM = "progress"
PROGRESS_VERSION = 2
LOCAL_STORAGE_KEY = "organic_chemistry_quiz_progress_v2"


def encode_progress(data):
    raw = json.dumps(
        data,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    compressed = zlib.compress(raw, level=9)
    return base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")


def decode_progress(value):
    if not value:
        return None
    try:
        padding = "=" * (-len(value) % 4)
        compressed = base64.urlsafe_b64decode(value + padding)
        data = json.loads(zlib.decompress(compressed).decode("utf-8"))

        # 直前版(v1)のURL進捗も読めるようにする。
        if data.get("v") not in {1, PROGRESS_VERSION}:
            return None

        return data
    except Exception:
        return None


def get_query_progress_value():
    value = st.query_params.get(PROGRESS_PARAM)
    if isinstance(value, list):
        value = value[0] if value else None
    return value


# ---------------------------------------------------------
# ブラウザ localStorage 用 Streamlit Components V2
# ---------------------------------------------------------
# Streamlitが古く Components V2 を持たない場合でも、
# アプリ本体はURL保存だけで動き続けるようフォールバックする。
try:
    _components_v2 = st.components.v2
    _has_components_v2 = hasattr(_components_v2, "component")
except Exception:
    _components_v2 = None
    _has_components_v2 = False


if _has_components_v2:
    _progress_storage_component = st.components.v2.component(
        "organic_quiz_progress_storage",
        js=r"""
        export default function(component) {
            const { data, setStateValue } = component;
            const storageKey = data.storageKey;
            const action = data.action;

            if (action === "load") {
                let stored = null;
                let available = true;

                try {
                    stored = window.localStorage.getItem(storageKey);
                } catch (e) {
                    available = false;
                    stored = null;
                }

                // stored/availableを先に送り、readyを最後に送る。
                setStateValue("stored", stored);
                setStateValue("available", available);
                setStateValue("ready", true);
                return;
            }

            if (action === "set") {
                try {
                    window.localStorage.setItem(storageKey, data.value ?? "");
                } catch (e) {
                    // 保存不可でもクイズ本体は止めない。
                }
                return;
            }

            if (action === "remove") {
                try {
                    window.localStorage.removeItem(storageKey);
                } catch (e) {
                    // 削除不可でもクイズ本体は止めない。
                }
            }
        }
        """,
    )
else:
    _progress_storage_component = None


def load_browser_progress_value():
    """
    localStorageを1回読み、(値, 読み込み完了, 利用可否)を返す。

    Components V2 がない環境では「読み込み完了・利用不可」として返し、
    URL保存だけでアプリを継続する。
    """
    if _progress_storage_component is None:
        return None, True, False

    result = _progress_storage_component(
        data={
            "action": "load",
            "storageKey": LOCAL_STORAGE_KEY,
        },
        default={
            "stored": None,
            "available": True,
            "ready": False,
        },
        on_stored_change=lambda: None,
        on_available_change=lambda: None,
        on_ready_change=lambda: None,
        key="progress_storage_reader",
    )

    return (
        result.stored,
        bool(result.ready),
        bool(result.available),
    )


def write_progress_to_browser(encoded_progress):
    """現在の進捗をlocalStorageへ保存する。"""
    if _progress_storage_component is None:
        return

    import hashlib
    digest = hashlib.sha1(
        encoded_progress.encode("utf-8")
    ).hexdigest()[:16]

    _progress_storage_component(
        data={
            "action": "set",
            "storageKey": LOCAL_STORAGE_KEY,
            "value": encoded_progress,
        },
        key=f"progress_storage_writer_{digest}",
    )


def clear_progress_from_browser():
    """localStorageの保存済み進捗を削除する。"""
    if _progress_storage_component is None:
        return

    _progress_storage_component(
        data={
            "action": "remove",
            "storageKey": LOCAL_STORAGE_KEY,
        },
        key="progress_storage_clearer",
    )


def clear_saved_progress():
    """URLとブラウザの両方から進捗を削除する。"""
    if PROGRESS_PARAM in st.query_params:
        del st.query_params[PROGRESS_PARAM]
    clear_progress_from_browser()


# ---------------------------------------------------------
# 起動時の復元
# ---------------------------------------------------------
# URLに進捗がある場合はそれを最優先する。
query_progress_value = get_query_progress_value()
saved_progress = decode_progress(query_progress_value)

# URLに有効な進捗がない「新しいブラウザセッション」のときだけ、
# localStorageを確認する。
if saved_progress is None:
    browser_progress_value, browser_storage_ready, browser_storage_available = (
        load_browser_progress_value()
    )

    if not browser_storage_ready:
        # 読み込み完了時にsetStateValue()がStreamlitをrerunする。
        st.caption("保存済みの進捗を確認しています…")
        st.stop()

    saved_progress = decode_progress(browser_progress_value)

    # localStorageから復元できたらURLにも戻す。
    if saved_progress is not None and browser_progress_value:
        st.query_params[PROGRESS_PARAM] = browser_progress_value


# 保存済みの設定が現在の選択肢として有効なら、最初からそこを表示する。
saved_chart = (saved_progress or {}).get("chart")
saved_range = (saved_progress or {}).get("range")
saved_style = (saved_progress or {}).get("style")

chart_index = chart_types.index(saved_chart) if saved_chart in chart_types else 0
range_index = range_options.index(saved_range) if saved_range in range_options else 3
style_index = question_styles.index(saved_style) if saved_style in question_styles else 0

st.title("有機化合物 系統図トレーニング")

name_col, chart_col, range_col, mode_col = st.columns([2, 1, 1.4, 1])

with name_col:
    student_name = st.text_input(
        "氏名",
        key="student_name_input",
        placeholder="例：山田 花子",
    )

with chart_col:
    selected_chart = st.selectbox(
        "系統図",
        chart_types,
        index=chart_index,
    )

with range_col:
    selected_range = st.selectbox(
        "出題範囲",
        range_options,
        index=range_index,
    )

with mode_col:
    selected_question_style = st.selectbox(
        "出題モード",
        question_styles,
        index=style_index,
    )


# =========================
# 系統図を切り替えたらクイズ状態をリセット
# =========================

if "selected_chart" not in st.session_state:
    st.session_state.selected_chart = selected_chart

if "selected_question_style" not in st.session_state:
    st.session_state.selected_question_style = selected_question_style

if "selected_range" not in st.session_state:
    st.session_state.selected_range = selected_range

# 1回の問題順を再現するための乱数シード。
# 保存済み進捗があれば同じシードを使う。
if "run_seed" not in st.session_state:
    if saved_progress and isinstance(saved_progress.get("seed"), int):
        st.session_state.run_seed = saved_progress["seed"]
    else:
        st.session_state.run_seed = secrets.randbits(63)

if (
    st.session_state.selected_chart != selected_chart
    or st.session_state.selected_question_style != selected_question_style
    or st.session_state.selected_range != selected_range
):
    st.session_state.selected_chart = selected_chart
    st.session_state.selected_question_style = selected_question_style
    st.session_state.selected_range = selected_range

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
    st.session_state.run_range = ""
    st.session_state.run_seed = secrets.randbits(63)
    st.session_state.review_current_candidate = None

    if "quiz_items" in st.session_state:
        del st.session_state.quiz_items

    if "two_questions" in st.session_state:
        del st.session_state.two_questions

    if "custom_questions" in st.session_state:
        del st.session_state.custom_questions

    clear_saved_progress()
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
# 選択した系統図・出題範囲の化合物IDを取得
# =========================

def normalize_range_level(value):
    if pd.isna(value):
        return None

    value_text = str(value).strip()

    if value_text.endswith(".0"):
        value_text = value_text[:-2]

    if value_text in {"1", "2", "3"}:
        return int(value_text)

    return None


compounds_df["range_level_normalized"] = (
    compounds_df["range_level"].apply(normalize_range_level)
)

chart_compound_ids = set(
    chart_map_df[
        chart_map_df["chart_type"] == selected_chart
    ]["compound_id"]
)

range_level_map = {
    "炭化水素まで": 1,
    "エステルまで": 2,
    "芳香族まで": 3,
}

if selected_range in range_level_map:
    max_level = range_level_map[selected_range]

    allowed_compound_ids = set(
        compounds_df[
            compounds_df["range_level_normalized"].notna()
            & (
                compounds_df["range_level_normalized"]
                <= max_level
            )
        ]["compound_id"]
    )

    selected_compound_ids = (
        chart_compound_ids
        & allowed_compound_ids
    )

elif selected_range in {"カスタムA", "カスタムB"}:
    # カスタムは脂肪族・芳香族をまたいでよいので、系統図は無視する
    selected_compound_ids = set(
        compounds_df["compound_id"]
        .dropna()
        .astype(str)
    )

else:
    # 「全部」は選択した系統図内をすべて出題対象にする
    selected_compound_ids = chart_compound_ids

# =========================
# reactions.csv から反応のつながりを作る
# =========================

def normalize_custom(value):
    if pd.isna(value):
        return False

    if isinstance(value, bool):
        return value

    return (
        str(value)
        .strip()
        .lower()
        in {"true", "1", "yes", "on"}
    )


reactions_df["custom_a_normalized"] = (
    reactions_df["custom_a"].apply(normalize_custom)
)

reactions_df["custom_b_normalized"] = (
    reactions_df["custom_b"].apply(normalize_custom)
)

connections = []

for _, row in reactions_df.iterrows():

    if (
        row["reactant_id"] in selected_compound_ids
        and row["product_id"] in selected_compound_ids
    ):
        # カスタム時だけ、選択したA/Bの反応に限定
        if (
            selected_range == "カスタムA"
            and not row["custom_a_normalized"]
        ):
            continue

        if (
            selected_range == "カスタムB"
            and not row["custom_b_normalized"]
        ):
            continue

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


def make_custom_single_questions():
    """カスタムで選んだ1反応を、そのまま1本問題として使う。"""
    custom_questions = {}

    for connection in connections:
        question_id = f"custom_one_{connection['reaction']}"

        custom_questions[question_id] = {
            "id": question_id,
            "layout": "two",
            "before": connection["from"],
            "condition1": connection["reaction"],
            "after": connection["to"],
        }

    return custom_questions


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
    # 同じ run_seed なら、リロード後も同じ問題順を完全再現する。
    rng = random.Random(st.session_state.run_seed)

    # カスタム：
    # 選んだ反応は基本1回ずつ使う。
    # つながっている反応どうしは、重複しない範囲で2反応問題にまとめる。
    # 何を隠すかは問題ごとにランダムに1か所だけ選ぶ。
    if selected_range in {"カスタムA", "カスタムB"}:
        st.session_state.custom_questions = {}

        if len(connections) == 0:
            return []

        # 反応順をランダム化して、同じ反応を2回使わないようにペアを作る
        shuffled_connections = connections.copy()
        rng.shuffle(shuffled_connections)

        used_reaction_ids = set()
        custom_problem_defs = []

        for first_connection in shuffled_connections:
            first_reaction_id = first_connection["reaction"]

            if first_reaction_id in used_reaction_ids:
                continue

            # first の生成物から続く、未使用の反応を候補にする
            pair_candidates = [
                second_connection
                for second_connection in shuffled_connections
                if (
                    second_connection["reaction"] not in used_reaction_ids
                    and second_connection["reaction"] != first_reaction_id
                    and first_connection["to"] == second_connection["from"]
                    and first_connection["from"] != second_connection["to"]
                )
            ]

            # つながる反応があれば2反応問題にまとめる
            if pair_candidates:
                second_connection = rng.choice(pair_candidates)

                question_id = (
                    f"custom_pair_{first_reaction_id}_"
                    f"{second_connection['reaction']}"
                )

                st.session_state.custom_questions[question_id] = {
                    "id": question_id,
                    "layout": "three",
                    "before": first_connection["from"],
                    "condition1": first_reaction_id,
                    "answer": first_connection["to"],
                    "condition2": second_connection["reaction"],
                    "after": second_connection["to"],
                }

                custom_problem_defs.append(
                    {
                        "question_id": question_id,
                        "layout": "three",
                    }
                )

                used_reaction_ids.add(first_reaction_id)
                used_reaction_ids.add(second_connection["reaction"])

            else:
                # つながる相手がなければ1反応問題
                question_id = f"custom_one_{first_reaction_id}"

                st.session_state.custom_questions[question_id] = {
                    "id": question_id,
                    "layout": "two",
                    "before": first_connection["from"],
                    "condition1": first_reaction_id,
                    "after": first_connection["to"],
                }

                custom_problem_defs.append(
                    {
                        "question_id": question_id,
                        "layout": "two",
                    }
                )

                used_reaction_ids.add(first_reaction_id)

        items = []

        for problem_def in custom_problem_defs:
            if problem_def["layout"] == "two":
                if selected_question_style == "構造式モード":
                    hidden_part = rng.choice(
                        ["before", "after"]
                    )
                else:
                    hidden_part = rng.choice(
                        ["before", "condition1", "after"]
                    )

            else:
                if selected_question_style == "構造式モード":
                    hidden_part = rng.choice(
                        ["before", "answer", "after"]
                    )
                else:
                    hidden_part = rng.choice(
                        all_hidden_parts
                    )

            items.append(
                {
                    "question_id": problem_def["question_id"],
                    "hidden_part": hidden_part,
                    "layout": problem_def["layout"],
                }
            )

        rng.shuffle(items)
        return items

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
        for compound_id in sorted(selected_compound_ids):
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
            rng.choice(candidates)
            for _, candidates in sorted(candidates_by_compound.items())
        ]

        rng.shuffle(items)
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

    rng.shuffle(items)
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

if "run_range" not in st.session_state:
    st.session_state.run_range = ""

if "review_current_candidate" not in st.session_state:
    st.session_state.review_current_candidate = None


def restore_saved_progress_once():
    """query parameter から session_state へ進捗を1回だけ復元する。"""
    if st.session_state.get("progress_restored_once"):
        return

    st.session_state.progress_restored_once = True

    if not saved_progress:
        return


    # 設定が一致している場合だけ復元する。
    if not (
        saved_progress.get("chart") == selected_chart
        and saved_progress.get("range") == selected_range
        and saved_progress.get("style") == selected_question_style
    ):
        return

    st.session_state.mode = saved_progress.get("mode", "normal")
    st.session_state.quiz_number = max(0, int(saved_progress.get("q", 0)))
    st.session_state.show_answer = bool(saved_progress.get("answer", False))
    st.session_state.review_number = max(0, int(saved_progress.get("rq", 0)))
    st.session_state.finished_once = bool(saved_progress.get("finished", False))
    st.session_state.completed_at = saved_progress.get("completed")

    restored_review = []
    for item in saved_progress.get("review", []):
        if not isinstance(item, list) or len(item) < 2:
            continue
        item_type = "compound" if item[0] == "c" else "reaction"
        restored_review.append(
            {
                "item_type": item_type,
                "item_id": item[1],
                "question_id": item[2] if len(item) >= 3 else None,
                "hidden_part": item[3] if len(item) >= 4 else None,
            }
        )
    st.session_state.review_list = restored_review

    candidate = saved_progress.get("review_candidate")
    if isinstance(candidate, list) and len(candidate) == 2:
        st.session_state.review_current_candidate = {
            "question_id": candidate[0],
            "hidden_part": candidate[1],
        }
    else:
        st.session_state.review_current_candidate = None


def persist_progress():
    """氏名を除いた現在の進捗をURLへ保存する。"""
    review_compact = []
    for item in st.session_state.get("review_list", []):
        kind = "c" if item.get("item_type") == "compound" else "r"
        review_compact.append(
            [
                kind,
                item.get("item_id"),
                item.get("question_id"),
                item.get("hidden_part"),
            ]
        )

    current_candidate = st.session_state.get("review_current_candidate")
    candidate_compact = None
    if current_candidate:
        candidate_compact = [
            current_candidate.get("question_id"),
            current_candidate.get("hidden_part"),
        ]

    data = {
        "v": PROGRESS_VERSION,
        "seed": int(st.session_state.run_seed),
        "q": int(st.session_state.get("quiz_number", 0)),
        "mode": st.session_state.get("mode", "normal"),
        "rq": int(st.session_state.get("review_number", 0)),
        "review": review_compact,
        "review_candidate": candidate_compact,
        "chart": selected_chart,
        "range": selected_range,
        "style": selected_question_style,
        "answer": bool(st.session_state.get("show_answer", False)),
        "finished": bool(st.session_state.get("finished_once", False)),
        "completed": st.session_state.get("completed_at"),
    }
    encoded = encode_progress(data)
    st.query_params[PROGRESS_PARAM] = encoded
    write_progress_to_browser(encoded)


def reset_run_from_beginning():
    """保存済みの進捗を捨てて、新しい1周を1問目から始める。"""
    clear_saved_progress()
    st.session_state.mode = "normal"
    st.session_state.run_seed = secrets.randbits(63)
    st.session_state.quiz_items = make_quiz_items()
    st.session_state.quiz_number = 0
    st.session_state.show_answer = False
    st.session_state.review_list = []
    st.session_state.review_number = 0
    st.session_state.review_current_candidate = None
    st.session_state.finished_once = False
    st.session_state.completed_at = None
    st.session_state.run_name = ""
    st.session_state.run_chart = ""
    st.session_state.run_question_style = ""
    st.session_state.run_range = ""
    persist_progress()


restore_saved_progress_once()
# 1問目をまだ解いていない状態でも、選択した系統図・範囲・モードを保存する。
persist_progress()


def lock_run_info():
    """その回の氏名・系統・出題モードを固定する。"""
    if st.session_state.run_name == "":
        st.session_state.run_name = st.session_state.student_name_input.strip()

    if st.session_state.run_chart == "":
        if selected_range in {"カスタムA", "カスタムB"}:
            st.session_state.run_chart = (
                f"{selected_range}（脂肪族・芳香族混在可）"
            )
        else:
            st.session_state.run_chart = selected_chart

    if st.session_state.run_question_style == "":
        st.session_state.run_question_style = selected_question_style

    if st.session_state.run_range == "":
        st.session_state.run_range = selected_range


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

    if st.session_state.get("run_range"):
        certificate_lines.append(
            f"**出題範囲：{st.session_state.run_range}**"
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
                    '<div class="co-reactant-arrow">--→</div>'
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
                    '<div class="co-reactant-arrow">--→</div>'
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

        memo = clean_reaction_memo(reaction["memo"])

        # 化合物を問う問題では、反応メモは問題成立に必要な情報として
        # 出題時から表示する（例：同時に○○も生成）。
        # 反応条件そのものを問うときだけ、答えを漏らさないよう
        # 答え表示後にメモを見せる。
        if memo and (hidden_part != key or st.session_state.show_answer):
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

    if (
        isinstance(question_id, str)
        and (
            question_id.startswith("custom_one_")
            or question_id.startswith("custom_pair_")
        )
    ):
        return st.session_state.custom_questions[question_id]

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

        if len(st.session_state.quiz_items) == 0:
            if selected_range in {"カスタムA", "カスタムB"}:
                st.warning(
                    f"{selected_range}には反応が選択されていません。"
                    " 先生アプリで反応を選んで保存してください。"
                )
            else:
                st.warning(
                    "この出題範囲には問題がありません。"
                    " 先生アプリの出題範囲設定を確認してください。"
                )

        elif st.session_state.quiz_number >= len(
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
                    st.session_state.review_current_candidate = None
                    persist_progress()
                    st.rerun()

            else:
                show_completion_certificate()

            if st.button("最初からやり直す"):
                reset_run_from_beginning()
                st.rerun()

        else:
            quiz_item = st.session_state.quiz_items[
                st.session_state.quiz_number
            ]

            question = get_question_by_id(
                quiz_item["question_id"]
            )

            hidden_part = quiz_item["hidden_part"]

            if hidden_part in ["before", "answer", "after"]:
                if selected_question_style == "構造式モード":
                    prompt_text = "「？」の構造式を書いてください。"
                else:
                    prompt_text = "「？」の化合物名と構造式の両方を答えてください。"
            else:
                prompt_text = "反応名・反応条件を答えてください。"

            st.html(
                f'<span class="label-subtitle">【問題】</span>'
                f'<span class="question-number"> '
                f"({st.session_state.quiz_number + 1}"
                f" / {len(st.session_state.quiz_items)})</span>"
                f'<span class="question-prompt">{prompt_text}</span>'
            )

            show_question(question, hidden_part)

            if st.button("答えを見る", key="btn_answer"):
                if st.session_state.student_name_input.strip() == "":
                    st.warning("氏名を入力してから始めてください。")
                else:
                    lock_run_info()
                    st.session_state.show_answer = True
                    persist_progress()
                    st.rerun()


            if st.session_state.show_answer:
                st.html('<div class="self-rating-title">【自己評価】</div>')

                space1, col1, col2, col3, space2 = st.columns([1, 2, 2, 2, 1])
                with col1:
                    if st.button("できた", key="btn_good"):
                        st.session_state.quiz_number += 1
                        st.session_state.show_answer = False
                        persist_progress()
                        st.rerun()

                with col2:
                    if st.button("微妙", key="btn_mid"):
                        st.session_state.quiz_number += 1
                        st.session_state.show_answer = False
                        persist_progress()
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
                        persist_progress()
                        st.rerun()
    else:
        if len(st.session_state.review_list) == 0:
            show_completion_certificate()

            if st.button("最初からやり直す"):
                reset_run_from_beginning()
                st.rerun()

        else:
            if st.session_state.review_number >= len(
                st.session_state.review_list
            ):
                st.session_state.review_number = 0
                review_cycle_rng = random.Random(
                    f"{st.session_state.run_seed}:review-cycle:"
                    f"{len(st.session_state.review_list)}"
                )
                review_cycle_rng.shuffle(st.session_state.review_list)
                st.session_state.review_current_candidate = None
                persist_progress()

            review_item = st.session_state.review_list[
                st.session_state.review_number
            ]

            candidates = find_review_candidates(review_item)

            # 「答えを見る」のrerunや接続切れで、同じ復習問題が
            # 別の問題へすり替わらないよう現在候補を固定する。
            selected_candidate = st.session_state.get("review_current_candidate")

            if selected_candidate not in candidates:
                different_candidates = [
                    candidate
                    for candidate in candidates
                    if candidate["question_id"] != review_item.get("question_id")
                ]

                review_rng = random.Random(
                    f"{st.session_state.run_seed}:{review_item['item_type']}:"
                    f"{review_item['item_id']}:{st.session_state.review_number}"
                )

                if len(different_candidates) > 0:
                    selected_candidate = review_rng.choice(different_candidates)
                else:
                    selected_candidate = review_rng.choice(candidates)

                st.session_state.review_current_candidate = selected_candidate
                persist_progress()

            question = get_question_by_id(
                selected_candidate["question_id"]
            )

            hidden_part = selected_candidate["hidden_part"]

            if hidden_part in ["before", "answer", "after"]:
                if st.session_state.get("run_question_style") == "構造式モード":
                    prompt_text = "「？」の構造式を書いてください。"
                else:
                    prompt_text = "「？」の化合物名と構造式の両方を答えてください。"
            else:
                prompt_text = "反応名・反応条件を答えてください。"

            st.html(
                f'<span class="label-subtitle">復習</span>'
                f'<span class="question-number"> '
                f"{st.session_state.review_number + 1}"
                f" / {len(st.session_state.review_list)}</span>"
                f'<span class="question-prompt">{prompt_text}</span>'
            )

            show_question(question, hidden_part)
            if st.button("答えを見る", key="btn_answer"):
                if st.session_state.student_name_input.strip() == "":
                    st.warning("氏名を入力してから始めてください。")
                else:
                    lock_run_info()
                    st.session_state.show_answer = True
                    persist_progress()
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
                        st.session_state.review_current_candidate = None

                        if st.session_state.review_number >= len(
                            st.session_state.review_list
                        ):
                            st.session_state.review_number = 0

                        persist_progress()
                        st.rerun()

                with col2:
                    if st.button("微妙", key="btn_mid"):
                        st.session_state.review_number += 1
                        st.session_state.show_answer = False
                        st.session_state.review_current_candidate = None
                        persist_progress()
                        st.rerun()

                with col3:
                    if st.button("できなかった", key="btn_bad"):
                        st.session_state.review_number += 1
                        st.session_state.show_answer = False
                        st.session_state.review_current_candidate = None
                        persist_progress()
                        st.rerun()

with right_col:
    with st.container(
        height=850,
        border=True,
        key="review_scroll",
    ):
        show_review_list()
