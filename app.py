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
# 途中経過の保存・復元（モード別）
# =========================
# 進捗は「系統図 × 出題範囲 × 出題モード」ごとに別保存する。
# カスタムA/Bは系統図をまたぐため、系統図部分は共通キーにする。
# 氏名は保存しない。
#
# 保存先：
# 1) URL query parameter = 今開いているモードの即時復元用
# 2) browser localStorage = 各モードの複数進捗をまとめて保持
PROGRESS_PARAM = "progress"
PROGRESS_VERSION = 3
LOCAL_STORAGE_KEY = "organic_chemistry_quiz_progress_slots_v3"


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
        if data.get("v") not in {1, 2, PROGRESS_VERSION}:
            return None
        return data
    except Exception:
        return None


def get_query_progress_value():
    value = st.query_params.get(PROGRESS_PARAM)
    if isinstance(value, list):
        value = value[0] if value else None
    return value


def make_progress_slot_key(chart, selected_range_value, style):
    """設定ごとの保存スロット名。カスタムは系統図に依存しない。"""
    chart_part = "CUSTOM" if selected_range_value in {"カスタムA", "カスタムB"} else str(chart)
    return f"{chart_part}||{selected_range_value}||{style}"


def normalize_bool_for_signature(value):
    if pd.isna(value):
        return False
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "on"}


def custom_definition_signature(selected_range_value):
    """カスタムA/Bの反応構成が変わったかを検知する署名。"""
    if selected_range_value not in {"カスタムA", "カスタムB"}:
        return ""

    col = "custom_a" if selected_range_value == "カスタムA" else "custom_b"
    selected_ids = sorted(
        reactions_df.loc[
            reactions_df[col].apply(normalize_bool_for_signature),
            "reaction_id",
        ].dropna().astype(str).tolist()
    )

    import hashlib
    raw = "|".join(selected_ids).encode("utf-8")
    return hashlib.sha1(raw).hexdigest()


# ---------------------------------------------------------
# ブラウザ localStorage 用 Streamlit Components V2
# ---------------------------------------------------------
try:
    _components_v2 = st.components.v2
    _has_components_v2 = hasattr(_components_v2, "component")
except Exception:
    _components_v2 = None
    _has_components_v2 = False


if _has_components_v2:
    _progress_storage_component = st.components.v2.component(
        "organic_quiz_progress_storage_slots",
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
                }
                setStateValue("stored", stored);
                setStateValue("available", available);
                setStateValue("ready", true);
                return;
            }

            if (action === "set") {
                try {
                    window.localStorage.setItem(storageKey, data.value ?? "");
                } catch (e) {}
                return;
            }

            if (action === "remove") {
                try {
                    window.localStorage.removeItem(storageKey);
                } catch (e) {}
            }
        }
        """,
    )
else:
    _progress_storage_component = None


# ---------------------------------------------------------
# Apple Pencil / 指で書ける手書きキャンバス
# ---------------------------------------------------------
# 「答えを見る」のrerunでは同じquestionTokenなので内容を復元し、
# 次の問題へ進んでquestionTokenが変わった瞬間に自動で白紙にする。
# 保存先はsessionStorageのみ。成績・進捗データには含めない。
if _has_components_v2:
    _handwriting_component = st.components.v2.component(
        "organic_quiz_handwriting_canvas",
        html=r"""
        <div class="handwriting-wrap">
            <div class="handwriting-head">
                <span class="handwriting-title">【手書きメモ】</span>
                <button id="clear-handwriting" type="button">手書きを消す</button>
            </div>
            <div class="handwriting-caption">指で自由に書けます。Apple Pencilでも入力できます。</div>
            <canvas id="handwriting-canvas"></canvas>
        </div>
        """,
        css=r"""
        .handwriting-wrap {
            width: 100%;
            height: 100%;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            font-family: var(--st-font);

            /* iPad SafariでApple Pencil操作を文字選択と誤認させない */
            user-select: none;
            -webkit-user-select: none;
            -webkit-touch-callout: none;
            touch-action: none;
        }

        .handwriting-wrap * {
            user-select: none;
            -webkit-user-select: none;
            -webkit-touch-callout: none;
        }

        .handwriting-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 8px;
            margin-bottom: 3px;
        }

        .handwriting-title {
            font-size: 24px;
            font-weight: 700;
            color: var(--st-text-color);
        }

        .handwriting-caption {
            font-size: 13px;
            color: var(--st-text-color);
            opacity: 0.65;
            margin-bottom: 6px;
        }

        #clear-handwriting {
            min-height: 32px;
            padding: 4px 10px;
            border: 1px solid rgba(49, 51, 63, 0.25);
            border-radius: 7px;
            background: transparent;
            color: var(--st-text-color);
            font-size: 13px;
        }

        #handwriting-canvas {
            display: block;
            width: 100%;
            flex: 1 1 auto;
            min-height: 190px;
            border: 2px solid #777777;
            border-radius: 8px;
            background: #ffffff;
            box-sizing: border-box;

            /* Pencil/指のジェスチャーをキャンバス専用にする */
            touch-action: none;
            user-select: none;
            -webkit-user-select: none;
            -webkit-touch-callout: none;
            cursor: crosshair;
        }
        """,
        js=r"""
        export default function(component) {
            const { parentElement, data } = component;
            const canvas = parentElement.querySelector("#handwriting-canvas");
            const clearButton = parentElement.querySelector("#clear-handwriting");
            const handwritingWrap = parentElement.querySelector(".handwriting-wrap");
            const ctx = canvas.getContext("2d", {
                alpha: false,
                desynchronized: true,
            });

            // iPad SafariがApple Pencil操作をテキスト選択・長押しメニューとして
            // 解釈しないよう、手書きエリア内だけブラウザ標準動作を止める。
            const preventSelection = (event) => {
                event.preventDefault();
            };

            handwritingWrap.addEventListener("selectstart", preventSelection);
            handwritingWrap.addEventListener("dragstart", preventSelection);
            handwritingWrap.addEventListener("contextmenu", preventSelection);

            const storageKey = "organic_quiz_handwriting_current_v1";
            const questionToken = String(data?.questionToken ?? "");
            const dpr = Math.max(window.devicePixelRatio || 1, 1);

            let drawing = false;
            let activePointerId = null;
            let lastX = 0;
            let lastY = 0;
            let resizeObserver = null;

            function readStored() {
                try {
                    const raw = window.sessionStorage.getItem(storageKey);
                    if (!raw) return null;
                    const stored = JSON.parse(raw);
                    if (stored?.token !== questionToken) return null;
                    return stored?.image ?? null;
                } catch (e) {
                    return null;
                }
            }

            function saveCanvas() {
                if (!questionToken) return;
                try {
                    window.sessionStorage.setItem(
                        storageKey,
                        JSON.stringify({
                            token: questionToken,
                            image: canvas.toDataURL("image/png"),
                        })
                    );
                } catch (e) {
                    // 一時保存できない環境でも手書き自体は使える。
                }
            }

            function clearStoredIfNewQuestion() {
                try {
                    const raw = window.sessionStorage.getItem(storageKey);
                    if (!raw) return;
                    const stored = JSON.parse(raw);
                    if (stored?.token !== questionToken) {
                        window.sessionStorage.removeItem(storageKey);
                    }
                } catch (e) {
                    try {
                        window.sessionStorage.removeItem(storageKey);
                    } catch (_) {}
                }
            }

            function clearCanvas(save = true) {
                ctx.save();
                ctx.setTransform(1, 0, 0, 1, 0, 0);
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "#ffffff";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.restore();
                if (save) saveCanvas();
            }

            function restoreImage(imageData) {
                if (!imageData) {
                    clearCanvas(false);
                    return;
                }

                const img = new Image();
                img.onload = () => {
                    clearCanvas(false);
                    ctx.drawImage(img, 0, 0, canvas.width / dpr, canvas.height / dpr);
                };
                img.src = imageData;
            }

            function resizeCanvas() {
                // サイズ変更前の現在画像を確保。
                let currentImage = null;
                try {
                    currentImage = canvas.toDataURL("image/png");
                } catch (e) {}

                const rect = canvas.getBoundingClientRect();
                const cssWidth = Math.max(rect.width, 1);
                const cssHeight = Math.max(rect.height, 260);

                const newWidth = Math.round(cssWidth * dpr);
                const newHeight = Math.round(cssHeight * dpr);

                if (canvas.width === newWidth && canvas.height === newHeight) return;

                canvas.width = newWidth;
                canvas.height = newHeight;
                ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
                ctx.lineCap = "round";
                ctx.lineJoin = "round";
                ctx.miterLimit = 2;
                ctx.strokeStyle = "#111111";
                ctx.lineWidth = 2.3;

                const savedImage = readStored() || currentImage;
                restoreImage(savedImage);
            }

            function pointFromEvent(event) {
                const rect = canvas.getBoundingClientRect();
                return {
                    x: event.clientX - rect.left,
                    y: event.clientY - rect.top,
                };
            }

            function pointerDown(event) {
                event.preventDefault();

                // 前のストロークが万一残っていても、必ずここで完全終了させる。
                if (drawing) {
                    drawing = false;
                    activePointerId = null;
                    ctx.closePath();
                }

                activePointerId = event.pointerId;

                try {
                    canvas.setPointerCapture(event.pointerId);
                } catch (e) {}

                const p = pointFromEvent(event);

                drawing = true;
                lastX = p.x;
                lastY = p.y;

                // Pencilを置くたびに必ず新しいストロークを開始する。
                ctx.beginPath();
                ctx.moveTo(lastX, lastY);

                // タップだけでも点が残るよう、ごく短い線を描く。
                ctx.lineWidth = 2.3;
                ctx.lineTo(lastX + 0.01, lastY + 0.01);
                ctx.stroke();
            }

            function drawSample(sample) {
                const p = pointFromEvent(sample);

                // 化学の走り書き用途なので、筆圧や補間は使わず軽さ優先。
                ctx.lineWidth = 2.3;
                ctx.lineTo(p.x, p.y);
                ctx.stroke();

                lastX = p.x;
                lastY = p.y;
            }


            function pointerMove(event) {
                if (!drawing) return;
                if (activePointerId !== null && event.pointerId !== activePointerId) return;

                event.preventDefault();

                // Apple Pencilは細かいイベントを全部処理すると重くなるため、
                // その時点の最新位置だけ描く。指・マウスも同じ軽量処理。
                let sample = event;

                if (typeof event.getCoalescedEvents === "function") {
                    const coalesced = event.getCoalescedEvents();
                    if (coalesced && coalesced.length > 0) {
                        sample = coalesced[coalesced.length - 1];
                    }
                }

                drawSample(sample);
            }

            function finishStroke(event, drawLastPoint = true) {
                if (!drawing) return;

                if (
                    activePointerId !== null
                    && event.pointerId !== undefined
                    && event.pointerId !== activePointerId
                ) {
                    return;
                }

                event.preventDefault();

                if (drawLastPoint) {
                    try {
                        drawSample(event);
                    } catch (e) {}
                }

                drawing = false;
                ctx.closePath();

                // iPad Safari任せにせず、Pencilのpointer captureを明示的に解放。
                if (activePointerId !== null) {
                    try {
                        if (canvas.hasPointerCapture(activePointerId)) {
                            canvas.releasePointerCapture(activePointerId);
                        }
                    } catch (e) {}
                }

                activePointerId = null;
                saveCanvas();
            }


            function pointerUp(event) {
                finishStroke(event, true);
            }


            function pointerCancel(event) {
                // cancel時は余計な終端線を描かず終了だけする。
                finishStroke(event, false);
            }

            clearStoredIfNewQuestion();
            resizeCanvas();

            const saved = readStored();
            if (saved) {
                restoreImage(saved);
            } else {
                clearCanvas(false);
            }

            canvas.addEventListener("pointerdown", pointerDown, { passive: false });
            canvas.addEventListener("pointermove", pointerMove, { passive: false });
            canvas.addEventListener("pointerup", pointerUp, { passive: false });
            canvas.addEventListener("pointercancel", pointerCancel, { passive: false });

            // pointerleaveではストローク終了させない。
            // Apple Pencilのhover/境界挙動をSafariがpointerleaveとして送る場合があるため。

            clearButton.onclick = () => {
                clearCanvas(true);
            };

            resizeObserver = new ResizeObserver(() => resizeCanvas());
            resizeObserver.observe(canvas);

            return () => {
                canvas.removeEventListener("pointerdown", pointerDown);
                canvas.removeEventListener("pointermove", pointerMove);
                canvas.removeEventListener("pointerup", pointerUp);
                canvas.removeEventListener("pointercancel", pointerCancel);

                handwritingWrap.removeEventListener("selectstart", preventSelection);
                handwritingWrap.removeEventListener("dragstart", preventSelection);
                handwritingWrap.removeEventListener("contextmenu", preventSelection);

                if (resizeObserver) resizeObserver.disconnect();
            };
        }
        """,
    )
else:
    _handwriting_component = None


def show_handwriting_space(question_token):
    """現在の問題専用の手書きスペースを表示する。"""
    if _handwriting_component is None:
        st.info("この環境では手書きスペースを利用できません。")
        return

    _handwriting_component(
        data={"questionToken": question_token},
        key="handwriting_canvas",
        width="stretch",
        height=450,
    )


def load_browser_registry():
    """localStorageから全モード分の保存レジストリを読む。"""
    if _progress_storage_component is None:
        return {"v": 1, "last_slot": None, "slots": {}}, True, False

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
        key="progress_storage_registry_reader",
    )

    if not bool(result.ready):
        return None, False, bool(result.available)

    registry = {"v": 1, "last_slot": None, "slots": {}}
    if result.stored:
        try:
            loaded = json.loads(result.stored)
            if isinstance(loaded, dict):
                registry["last_slot"] = loaded.get("last_slot")
                slots = loaded.get("slots", {})
                if isinstance(slots, dict):
                    registry["slots"] = slots
        except Exception:
            pass

    return registry, True, bool(result.available)


# 同じStreamlit実行内で、同一内容のlocalStorage書き込みを
# 複数回マウントしないための一時セット。
# モジュールはrerunごとに再実行されるので、次の画面更新では自然に空になる。
_registry_writer_digests_used = set()


def write_registry_to_browser(registry):
    # ブラウザ保存と同時に、現在のStreamlitセッション内でも最新版を保持する。
    # モード変更直後はこのキャッシュから読み出すため、手動リロードが不要になる。
    st.session_state.progress_registry_cache = {
        "v": registry.get("v", 1),
        "last_slot": registry.get("last_slot"),
        "slots": dict(registry.get("slots", {})),
    }

    if _progress_storage_component is None:
        return

    registry_text = json.dumps(
        registry,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    import hashlib
    digest = hashlib.sha1(registry_text.encode("utf-8")).hexdigest()[:16]

    # 同じ1回の画面実行中に、まったく同じ進捗を再保存しようとした場合は
    # StreamlitDuplicateElementKey を避けるため2回目以降をスキップする。
    if digest in _registry_writer_digests_used:
        return

    _registry_writer_digests_used.add(digest)

    _progress_storage_component(
        data={
            "action": "set",
            "storageKey": LOCAL_STORAGE_KEY,
            "value": registry_text,
        },
        key=f"progress_storage_registry_writer_{digest}",
    )


def get_progress_from_registry(registry, chart, range_value, style):
    if not registry:
        return None, None

    slot_key = make_progress_slot_key(chart, range_value, style)
    encoded = registry.get("slots", {}).get(slot_key)
    progress = decode_progress(encoded)

    if not progress:
        return None, encoded

    # カスタム内容が先生アプリで変更されていたら、その保存だけ無効にする。
    expected_sig = custom_definition_signature(range_value)
    saved_sig = progress.get("custom_sig", "")
    if range_value in {"カスタムA", "カスタムB"} and saved_sig != expected_sig:
        return None, encoded

    return progress, encoded


def remove_current_slot_from_registry(registry, chart, range_value, style):
    slot_key = make_progress_slot_key(chart, range_value, style)
    updated = {
        "v": 1,
        "last_slot": registry.get("last_slot") if registry else None,
        "slots": dict((registry or {}).get("slots", {})),
    }
    updated["slots"].pop(slot_key, None)
    if updated.get("last_slot") == slot_key:
        updated["last_slot"] = None
    return updated


# ---------------------------------------------------------
# 起動時：まずブラウザの全モード進捗を読む
# ---------------------------------------------------------
loaded_browser_progress_registry, browser_storage_ready, browser_storage_available = (
    load_browser_registry()
)

if not browser_storage_ready:
    st.caption("保存済みの進捗を確認しています…")
    st.stop()

# ブラウザから読み込んだ全モード進捗は、最初の1回だけsession_stateへ取り込む。
# 以後、問題を進めてlocalStorageへ保存するときはこのキャッシュも同時更新する。
# これにより、モード切替時に手動リロードしなくても最新進捗を参照できる。
if "progress_registry_cache" not in st.session_state:
    st.session_state.progress_registry_cache = loaded_browser_progress_registry

browser_progress_registry = st.session_state.progress_registry_cache

# URLに有効な進捗があれば、今開いているモードとして最優先。
query_progress_value = get_query_progress_value()
query_saved_progress = decode_progress(query_progress_value)

# URLがない新規起動では、前回最後に使ったスロットを初期選択にする。
initial_saved_progress = query_saved_progress
if initial_saved_progress is None and browser_progress_registry:
    last_slot = browser_progress_registry.get("last_slot")
    if last_slot:
        encoded = browser_progress_registry.get("slots", {}).get(last_slot)
        candidate = decode_progress(encoded)
        if candidate:
            # カスタム構成が変わっていないことも確認する。
            candidate_range = candidate.get("range")
            if (
                candidate_range not in {"カスタムA", "カスタムB"}
                or candidate.get("custom_sig", "") == custom_definition_signature(candidate_range)
            ):
                initial_saved_progress = candidate

saved_chart = (initial_saved_progress or {}).get("chart")
saved_range = (initial_saved_progress or {}).get("range")
saved_style = (initial_saved_progress or {}).get("style")

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

# 現在選択中の設定に対応する保存進捗を取得。
saved_progress, selected_slot_encoded = get_progress_from_registry(
    browser_progress_registry,
    selected_chart,
    selected_range,
    selected_question_style,
)

# URLの進捗が現在の選択と一致する場合は、URL側を優先する。
if query_saved_progress and (
    query_saved_progress.get("chart") == selected_chart
    and query_saved_progress.get("range") == selected_range
    and query_saved_progress.get("style") == selected_question_style
):
    if (
        selected_range not in {"カスタムA", "カスタムB"}
        or query_saved_progress.get("custom_sig", "")
        == custom_definition_signature(selected_range)
    ):
        saved_progress = query_saved_progress
        selected_slot_encoded = query_progress_value


# =========================
# 系統図・範囲・出題モードを切り替えたら、その設定専用の進捗へ切替
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
    # 以前のモードの保存は消さず、新しく選んだモード専用の進捗へ切り替える。
    st.session_state.selected_chart = selected_chart
    st.session_state.selected_question_style = selected_question_style
    st.session_state.selected_range = selected_range

    current_registry = st.session_state.get(
        "progress_registry_cache",
        browser_progress_registry or {"v": 1, "last_slot": None, "slots": {}},
    )

    slot_progress, slot_encoded = get_progress_from_registry(
        current_registry,
        selected_chart,
        selected_range,
        selected_question_style,
    )

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
    st.session_state.review_current_candidate = None
    st.session_state.progress_restored_once = False

    if slot_progress and isinstance(slot_progress.get("seed"), int):
        st.session_state.run_seed = slot_progress["seed"]
        st.query_params[PROGRESS_PARAM] = slot_encoded

        # この実行の後半で、そのモードの保存済み進捗をそのまま復元する。
        # ここで余計な st.rerun() を挟まないことで、
        # プルダウン変更直後に手動リロードなしで画面を切り替えられる。
        saved_progress = slot_progress
        selected_slot_encoded = slot_encoded
    else:
        st.session_state.run_seed = secrets.randbits(63)
        saved_progress = None
        selected_slot_encoded = None

        if PROGRESS_PARAM in st.query_params:
            del st.query_params[PROGRESS_PARAM]

    for state_key in ["quiz_items", "two_questions", "custom_questions"]:
        st.session_state.pop(state_key, None)

    # st.selectbox の変更自体で Streamlit はすでに再実行されているため、
    # ここでは st.rerun() しない。
    # 後続の問題生成 → restore_saved_progress_once() まで同じ実行内で進める。



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
        "custom_sig": custom_definition_signature(selected_range),
    }
    encoded = encode_progress(data)
    st.query_params[PROGRESS_PARAM] = encoded

    slot_key = make_progress_slot_key(
        selected_chart,
        selected_range,
        selected_question_style,
    )
    current_registry = st.session_state.get(
        "progress_registry_cache",
        browser_progress_registry or {"v": 1, "last_slot": None, "slots": {}},
    )

    updated_registry = {
        "v": 1,
        "last_slot": slot_key,
        "slots": dict((current_registry or {}).get("slots", {})),
    }
    updated_registry["slots"][slot_key] = encoded
    write_registry_to_browser(updated_registry)


def reset_run_from_beginning():
    """現在選択中のモードだけを1問目からやり直す。他モードの進捗は残す。"""
    if PROGRESS_PARAM in st.query_params:
        del st.query_params[PROGRESS_PARAM]

    current_registry = st.session_state.get(
        "progress_registry_cache",
        browser_progress_registry or {"v": 1, "last_slot": None, "slots": {}},
    )

    updated_registry = remove_current_slot_from_registry(
        current_registry,
        selected_chart,
        selected_range,
        selected_question_style,
    )
    write_registry_to_browser(updated_registry)

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


def get_handwriting_question_token():
    """
    「答えを見る」では変化せず、次の問題に進んだときだけ変わるトークン。
    これを手書きキャンバスの一時保存キー判定に使う。
    """
    slot_key = make_progress_slot_key(
        selected_chart,
        selected_range,
        selected_question_style,
    )

    if st.session_state.mode == "normal":
        quiz_number = st.session_state.get("quiz_number", 0)
        quiz_items = st.session_state.get("quiz_items", [])

        if 0 <= quiz_number < len(quiz_items):
            item = quiz_items[quiz_number]
            return (
                f"{slot_key}|normal|{quiz_number}|"
                f"{item.get('question_id')}|{item.get('hidden_part')}"
            )

    else:
        review_number = st.session_state.get("review_number", 0)
        review_list = st.session_state.get("review_list", [])
        candidate = st.session_state.get("review_current_candidate")

        if (
            0 <= review_number < len(review_list)
            and isinstance(candidate, dict)
        ):
            review_item = review_list[review_number]
            return (
                f"{slot_key}|review|{review_number}|"
                f"{review_item.get('item_type')}|{review_item.get('item_id')}|"
                f"{candidate.get('question_id')}|{candidate.get('hidden_part')}"
            )

    return f"{slot_key}|no-active-question"


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

            save_info_col, save_button_col = st.columns([4, 1])

            with save_info_col:
                st.caption(
                    "途中で終了しても、次回はこの続きから再開できます。"
                )

            with save_button_col:
                if st.button(
                    "ここまで保存",
                    key="btn_manual_save_normal",
                    use_container_width=True,
                ):
                    persist_progress()
                    st.success("ここまでの進捗を保存しました。")

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

            save_info_col, save_button_col = st.columns([4, 1])

            with save_info_col:
                st.caption(
                    "途中で終了しても、次回はこの続きから再開できます。"
                )

            with save_button_col:
                if st.button(
                    "ここまで保存",
                    key="btn_manual_save_review",
                    use_container_width=True,
                ):
                    persist_progress()
                    st.success("ここまでの進捗を保存しました。")

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
    # 上半分：復習リスト
    with st.container(
        height=320,
        border=True,
        key="review_scroll",
    ):
        show_review_list()

    # 下半分：現在の問題だけに使う手書きスペース
    with st.container(
        height=560,
        border=True,
        key="handwriting_area",
    ):
        show_handwriting_space(
            get_handwriting_question_token()
        )
