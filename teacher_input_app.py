import base64
import io
import os

import pandas as pd
import requests
import streamlit as st


# =========================================================
# Streamlit画面設定
# =========================================================

st.set_page_config(
    page_title="教材データ入力",
    page_icon="🧪",
    layout="wide"
)


# =========================================================
# 基本設定
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MASTER_CSV_PATH = os.path.join(BASE_DIR, "compound_master.csv")

# GitHub上の保存先
DEFAULT_REPO = "milcoco87-cpu/organic-chemistry-app"
DEFAULT_BRANCH = "main"

COMPOUNDS_PATH = "compounds.csv"
REACTIONS_PATH = "reactions.csv"
IMAGE_DIR = "images"

COMPOUND_COLUMNS = [
    "compound_id",
    "name_ja",
    "name_en",
    "formula",
    "image",
    "memo",
    "range_level",
]

REACTION_COLUMNS = [
    "reaction_id",
    "reactant_id",
    "product_id",
    "condition",
    "reaction_type",
    "memo",
    "custom_a",
    "custom_b",
]


# =========================================================
# GitHub設定
# =========================================================

def get_secret(name, default=None):
    try:
        return st.secrets[name]
    except Exception:
        return default


GITHUB_TOKEN = get_secret("GITHUB_TOKEN")
GITHUB_REPO = get_secret("GITHUB_REPO", DEFAULT_REPO)
GITHUB_BRANCH = get_secret("GITHUB_BRANCH", DEFAULT_BRANCH)

if not GITHUB_TOKEN:
    st.error(
        "GitHub保存用の設定がまだありません。"
        " Streamlit の Secrets に GITHUB_TOKEN を登録してください。"
    )
    st.code(
        'GITHUB_TOKEN = "github_pat_..."\\n'
        f'GITHUB_REPO = "{DEFAULT_REPO}"\\n'
        f'GITHUB_BRANCH = "{DEFAULT_BRANCH}"'
    )
    st.stop()


API_BASE = f"https://api.github.com/repos/{GITHUB_REPO}"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


# =========================================================
# GitHub共通処理
# =========================================================

def github_request(method, url, **kwargs):
    response = requests.request(
        method,
        url,
        headers=HEADERS,
        timeout=30,
        **kwargs,
    )

    if not response.ok:
        detail = response.text
        raise RuntimeError(
            f"GitHub API エラー ({response.status_code})\\n{detail}"
        )

    return response


def read_github_bytes(path):
    """GitHub上のファイルをbytesで取得。存在しなければNone。"""
    response = requests.get(
        f"{API_BASE}/contents/{path}",
        headers=HEADERS,
        params={"ref": GITHUB_BRANCH},
        timeout=30,
    )

    if response.status_code == 404:
        return None

    if not response.ok:
        raise RuntimeError(
            f"GitHubから {path} を読めませんでした "
            f"({response.status_code})\\n{response.text}"
        )

    data = response.json()
    return base64.b64decode(data["content"])


def bytes_to_dataframe(data, columns):
    if data is None or len(data) == 0:
        return pd.DataFrame(columns=columns)

    text = data.decode("utf-8-sig")
    if not text.strip():
        return pd.DataFrame(columns=columns)

    df = pd.read_csv(io.StringIO(text))

    for col in columns:
        if col not in df.columns:
            df[col] = ""

    return df[columns].copy()


def dataframe_to_csv_bytes(df, columns):
    clean_df = df[columns].copy()

    text = clean_df.to_csv(
        index=False,
        lineterminator="\n",
    )

    # Excel等でも扱いやすいようBOM付きUTF-8
    return ("\ufeff" + text).encode("utf-8")


def load_compounds():
    return bytes_to_dataframe(
        read_github_bytes(COMPOUNDS_PATH),
        COMPOUND_COLUMNS,
    )


def load_reactions():
    return bytes_to_dataframe(
        read_github_bytes(REACTIONS_PATH),
        REACTION_COLUMNS,
    )


def commit_files(files, message, max_retries=4):
    """
    files = {
        "compounds.csv": b"...",
        "images/ethanol.png": b"...",
    }

    複数ファイルを1回のGitHubコミットでまとめて保存する。

    GitHub側のmainブランチが保存直前に更新された場合、
    422 "Update is not a fast forward" が返ることがあるため、
    最新HEADを取り直して自動再試行する。
    """

    # blobはブランチHEADに依存しないので最初に1回だけ作成
    blobs = []

    for file_path, content in files.items():
        blob = github_request(
            "POST",
            f"{API_BASE}/git/blobs",
            json={
                "content": base64.b64encode(content).decode("ascii"),
                "encoding": "base64",
            },
        ).json()

        blobs.append(
            {
                "path": file_path,
                "mode": "100644",
                "type": "blob",
                "sha": blob["sha"],
            }
        )

    last_error = None

    for attempt in range(max_retries):

        # 毎回、最新のmainブランチ先頭を取り直す
        ref_response = requests.get(
            f"{API_BASE}/git/ref/heads/{GITHUB_BRANCH}",
            headers=HEADERS,
            timeout=30,
        )

        if not ref_response.ok:
            raise RuntimeError(
                f"GitHub API エラー ({ref_response.status_code})\n"
                f"{ref_response.text}"
            )

        parent_commit_sha = ref_response.json()["object"]["sha"]

        parent_commit = github_request(
            "GET",
            f"{API_BASE}/git/commits/{parent_commit_sha}",
        ).json()

        base_tree_sha = parent_commit["tree"]["sha"]

        new_tree = github_request(
            "POST",
            f"{API_BASE}/git/trees",
            json={
                "base_tree": base_tree_sha,
                "tree": blobs,
            },
        ).json()

        new_commit = github_request(
            "POST",
            f"{API_BASE}/git/commits",
            json={
                "message": message,
                "tree": new_tree["sha"],
                "parents": [parent_commit_sha],
            },
        ).json()

        # ref更新だけは422を自前で判定して再試行する
        update_response = requests.patch(
            f"{API_BASE}/git/refs/heads/{GITHUB_BRANCH}",
            headers=HEADERS,
            json={
                "sha": new_commit["sha"],
                "force": False,
            },
            timeout=30,
        )

        if update_response.ok:
            return new_commit["sha"]

        if (
            update_response.status_code == 422
            and "fast forward" in update_response.text.lower()
        ):
            last_error = update_response.text
            # 別処理が先にmainを更新したので、
            # 最新HEADからコミットを作り直して再試行
            continue

        raise RuntimeError(
            f"GitHub API エラー ({update_response.status_code})\n"
            f"{update_response.text}"
        )

    raise RuntimeError(
        "GitHub側の更新とタイミングが重なったため保存できませんでした。"
        "もう一度「登録する／更新する」を押してください。\n"
        f"{last_error or ''}"
    )


# =========================================================
# マスターデータ
# =========================================================

if os.path.exists(MASTER_CSV_PATH):
    master_df = pd.read_csv(
        MASTER_CSV_PATH,
        dtype={"compound_id": str},
    )
else:
    st.error("compound_master.csv が見つかりません。")
    st.stop()

master_df["compound_id"] = master_df["compound_id"].astype(str)


# =========================================================
# GitHub上の現在データを取得
# =========================================================

try:
    df_registered = load_compounds()
    reaction_df = load_reactions()
except Exception as e:
    st.error("GitHubから教材データを取得できませんでした。")
    st.exception(e)
    st.stop()

df_registered["compound_id"] = (
    df_registered["compound_id"]
    .fillna("")
    .astype(str)
)

reaction_df["reaction_id"] = (
    reaction_df["reaction_id"]
    .fillna("")
    .astype(str)
)


# =========================================================
# 次の未登録化合物
# =========================================================

registered_ids = df_registered["compound_id"].tolist()

unregistered_master = master_df[
    ~master_df["compound_id"].isin(registered_ids)
]

next_id = ""
next_name_ja = ""
next_name_en = ""

if not unregistered_master.empty:
    next_row = unregistered_master.iloc[0]
    next_id = str(next_row["compound_id"])
    next_name_ja = str(next_row["name_ja"])
    next_name_en = str(next_row["name_en"])


# =========================================================
# 新規登録フォーム用 session_state
# =========================================================

if "new_compound_id" not in st.session_state:
    st.session_state.new_compound_id = next_id

if "new_name_ja" not in st.session_state:
    st.session_state.new_name_ja = next_name_ja

if "new_name_en" not in st.session_state:
    st.session_state.new_name_en = next_name_en

if "master_lookup_message" not in st.session_state:
    st.session_state.master_lookup_message = ""


def fill_names_from_master():
    """compound_id変更時にマスターから日本語名・英語名を自動取得。"""
    compound_id = st.session_state.new_compound_id.strip()

    matched = master_df[
        master_df["compound_id"] == compound_id
    ]

    if not matched.empty:
        row = matched.iloc[0]

        st.session_state.new_name_ja = (
            ""
            if pd.isna(row["name_ja"])
            else str(row["name_ja"])
        )

        st.session_state.new_name_en = (
            ""
            if pd.isna(row["name_en"])
            else str(row["name_en"])
        )

        st.session_state.master_lookup_message = (
            "✅ compound_master.csv から化合物名を取得しました。"
        )

    else:
        # マスター外の追加化合物も登録できるよう、名前欄は手入力可能
        st.session_state.new_name_ja = ""
        st.session_state.new_name_en = ""
        st.session_state.master_lookup_message = (
            "ℹ️ この compound_id は compound_master.csv にありません。"
            " 追加化合物として名称を手入力できます。"
        )


# =========================================================
# タイトル
# =========================================================

st.title("🧪 教材データ入力アプリ")

st.caption(
    "登録・編集したデータと構造式画像は、"
    "GitHub の教材リポジトリへ直接保存されます。"
)


# =========================================================
# 化合物データ登録
# =========================================================

st.subheader("化合物を登録")

compound_id = st.text_input(
    "compound_id",
    key="new_compound_id",
    on_change=fill_names_from_master,
)

if st.session_state.master_lookup_message:
    st.caption(st.session_state.master_lookup_message)

name_ja = st.text_input(
    "化合物名（日本語）",
    key="new_name_ja",
)

name_en = st.text_input(
    "化合物名（英語）",
    key="new_name_en",
)

formula = st.text_input(
    "分子式",
    placeholder="例：C2H6O",
    key="new_formula",
)

image = st.file_uploader(
    "構造式画像",
    type=["png", "jpg", "jpeg"],
    key="new_image",
)

memo = st.text_area(
    "メモ",
    placeholder="例：OとNaは結合線で結ばない",
    key="new_memo",
)

if st.button(
    "登録する",
    type="primary",
    key="register_compound",
):

    compound_id = compound_id.strip()
    name_ja = name_ja.strip()
    name_en = name_en.strip()

    if not compound_id or not name_ja or not name_en:
        st.error(
            "compound_id、日本語名、英語名は入力してください。"
        )

    elif compound_id in registered_ids:
        st.error(
            f"{compound_id} はすでに登録されています。"
        )

    else:
        try:
            new_df = df_registered.copy()

            image_filename = ""
            files_to_commit = {}

            if image is not None:
                extension = os.path.splitext(image.name)[1].lower()

                # 既存仕様を維持：英語名を画像ファイル名にする
                image_filename = f"{name_en}{extension}"

                files_to_commit[
                    f"{IMAGE_DIR}/{image_filename}"
                ] = image.getvalue()

            new_row = pd.DataFrame(
                [
                    {
                        "compound_id": compound_id,
                        "name_ja": name_ja,
                        "name_en": name_en,
                        "formula": formula,
                        "image": image_filename,
                        "memo": memo,
                        "range_level": "",
                    }
                ]
            )

            new_df = pd.concat(
                [new_df, new_row],
                ignore_index=True,
            )

            files_to_commit[COMPOUNDS_PATH] = (
                dataframe_to_csv_bytes(
                    new_df,
                    COMPOUND_COLUMNS,
                )
            )

            commit_sha = commit_files(
                files_to_commit,
                f"Register compound {compound_id}",
            )

            st.success(
                f"{compound_id} をGitHubへ登録しました！"
            )

            st.caption(
                f"commit: {commit_sha[:7]}"
            )

            if image is not None:
                st.image(
                    image,
                    caption=name_ja,
                    width=300,
                )

            # 次回表示を最新データにする
            st.rerun()

        except Exception as e:
            st.error(
                "登録中にエラーが発生しました。"
            )
            st.exception(e)


# =========================================================
# 登録済み化合物一覧
# =========================================================

st.divider()
st.subheader("登録済み化合物一覧")

df = df_registered.copy()

if len(df) > 0:

    df["image_status"] = df["image"].apply(
        lambda x: (
            "✅ あり"
            if pd.notna(x) and str(x).strip() != ""
            else "⚠️ なし"
        )
    )

    df = df.sort_values("compound_id")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    # =====================================================
    # 登録進捗
    # =====================================================

    base_total = 95
    base_ids = [
        f"cmp_{i:03d}"
        for i in range(1, base_total + 1)
    ]

    registered_ids_now = (
        df["compound_id"]
        .astype(str)
        .tolist()
    )

    registered_base_ids = [
        compound_id
        for compound_id in registered_ids_now
        if compound_id in base_ids
    ]

    unregistered_ids = [
        compound_id
        for compound_id in base_ids
        if compound_id not in registered_ids_now
    ]

    additional_count = len(
        [
            compound_id
            for compound_id in registered_ids_now
            if compound_id not in base_ids
        ]
    )

    st.write(
        f"系統図対象："
        f"{len(registered_base_ids)} / {base_total} 件"
    )

    st.write(
        f"追加化合物：{additional_count} 件"
    )

    st.write(
        f"データベース全体：{len(df)} 件"
    )

    if unregistered_ids:
        next_missing_id = unregistered_ids[0]

        next_row = master_df[
            master_df["compound_id"] == next_missing_id
        ]

        if not next_row.empty:
            row = next_row.iloc[0]

            st.info(
                f"次の未登録：{next_missing_id} "
                f"｜{row['name_ja']} "
                f"｜{row['name_en']}"
            )
        else:
            st.info(
                f"次の未登録ID：{next_missing_id}"
            )

    missing_image_count = (
        df["image_status"] == "⚠️ なし"
    ).sum()

    if missing_image_count > 0:
        st.warning(
            f"構造式画像が未登録："
            f"{missing_image_count} 件"
        )
    else:
        st.success(
            "すべての化合物に構造式画像が登録されています。"
        )

else:
    st.info(
        "まだ化合物は登録されていません。"
    )


# =========================================================
# 出題範囲設定
# =========================================================

st.divider()
st.subheader("📚 出題範囲設定")

st.caption(
    "1＝炭化水素まで　／　2＝エステルまで　／　3＝芳香族まで"
)
st.caption(
    "1～3は化合物ごとに1つだけ選びます。"
    " 未設定のまま保存して、途中から続けることもできます。"
)

range_df = df_registered.copy()

if len(range_df) > 0:

    def normalize_range_level(value):
        if pd.isna(value):
            return ""

        value_text = str(value).strip()

        if value_text.endswith(".0"):
            value_text = value_text[:-2]

        if value_text in {"1", "2", "3"}:
            return value_text

        return ""

    range_df["range_level"] = (
        range_df["range_level"]
        .apply(normalize_range_level)
    )

    range_editor_df = (
        range_df[
            [
                "compound_id",
                "name_ja",
                "range_level",
            ]
        ]
        .sort_values("compound_id")
        .reset_index(drop=True)
    )

    range_editor_df["1"] = (
        range_editor_df["range_level"] == "1"
    )
    range_editor_df["2"] = (
        range_editor_df["range_level"] == "2"
    )
    range_editor_df["3"] = (
        range_editor_df["range_level"] == "3"
    )

    range_editor_df = range_editor_df[
        [
            "compound_id",
            "name_ja",
            "1",
            "2",
            "3",
        ]
    ]

    edited_range_df = st.data_editor(
        range_editor_df,
        use_container_width=True,
        hide_index=True,
        disabled=[
            "compound_id",
            "name_ja",
        ],
        column_config={
            "compound_id": st.column_config.TextColumn(
                "化合物ID"
            ),
            "name_ja": st.column_config.TextColumn(
                "化合物名"
            ),
            "1": st.column_config.CheckboxColumn(
                "1"
            ),
            "2": st.column_config.CheckboxColumn(
                "2"
            ),
            "3": st.column_config.CheckboxColumn(
                "3"
            ),
        },
        key="range_level_editor",
    )

    range_save_col, range_status_col = st.columns(
        [1, 3]
    )

    with range_save_col:
        save_range = st.button(
            "出題範囲を保存",
            type="primary",
            key="save_range_levels",
        )

    if save_range:

        selected_counts = (
            edited_range_df[
                ["1", "2", "3"]
            ]
            .fillna(False)
            .astype(bool)
            .sum(axis=1)
        )

        invalid_rows = edited_range_df[
            selected_counts > 1
        ]

        if len(invalid_rows) > 0:
            invalid_names = "、".join(
                invalid_rows["name_ja"]
                .astype(str)
                .tolist()
            )

            st.error(
                "1～3は1つの化合物につき1つだけ選んでください。"
                f" 複数選択：{invalid_names}"
            )

        else:
            try:
                save_df = df_registered.copy()

                level_map = {}

                for _, row in edited_range_df.iterrows():
                    level = ""

                    if bool(row["1"]):
                        level = "1"
                    elif bool(row["2"]):
                        level = "2"
                    elif bool(row["3"]):
                        level = "3"

                    level_map[
                        str(row["compound_id"])
                    ] = level

                save_df["range_level"] = (
                    save_df["compound_id"]
                    .astype(str)
                    .map(level_map)
                    .fillna("")
                )

                commit_sha = commit_files(
                    {
                        COMPOUNDS_PATH:
                        dataframe_to_csv_bytes(
                            save_df,
                            COMPOUND_COLUMNS,
                        )
                    },
                    "Update compound range levels",
                )

                st.success(
                    "出題範囲をGitHubへ保存しました！"
                )
                st.caption(
                    f"commit: {commit_sha[:7]}"
                )

                st.rerun()

            except Exception as e:
                st.error(
                    "出題範囲の保存中にエラーが発生しました。"
                )
                st.exception(e)

else:
    st.info(
        "出題範囲を設定できる化合物がありません。"
    )


# =========================================================
# 登録済み化合物の編集
# =========================================================

st.divider()
st.subheader("✏️ 登録済み化合物を編集")

edit_df = df_registered.copy()

if len(edit_df) > 0:

    search_word = st.text_input(
        "編集する化合物を検索",
        placeholder="ID、日本語名、英語名の一部を入力",
        key="compound_edit_search",
    )

    if search_word:
        search_lower = search_word.lower()

        filtered_df = edit_df[
            edit_df["compound_id"]
            .astype(str)
            .str.lower()
            .str.contains(
                search_lower,
                na=False,
            )
            |
            edit_df["name_ja"]
            .astype(str)
            .str.contains(
                search_word,
                na=False,
            )
            |
            edit_df["name_en"]
            .astype(str)
            .str.lower()
            .str.contains(
                search_lower,
                na=False,
            )
        ]

    else:
        filtered_df = edit_df

    if len(filtered_df) > 0:

        options = []

        for _, row in filtered_df.iterrows():
            options.append(
                f"{row['compound_id']} ｜ "
                f"{row['name_ja']} ｜ "
                f"{row['name_en']}"
            )

        selected_option = st.selectbox(
            "編集する化合物",
            options,
            key="compound_edit_select",
        )

        selected_id = (
            selected_option
            .split(" ｜ ")[0]
        )

        selected_row = edit_df[
            edit_df["compound_id"] == selected_id
        ].iloc[0]

        def safe_text(value):
            return (
                ""
                if pd.isna(value)
                else str(value)
            )

        current_formula = safe_text(
            selected_row["formula"]
        )

        current_memo = safe_text(
            selected_row["memo"]
        )

        current_image = safe_text(
            selected_row["image"]
        )

        st.write(
            f"**compound_id：{selected_id}**"
        )

        edit_name_ja = st.text_input(
            "日本語名",
            value=safe_text(
                selected_row["name_ja"]
            ),
            key=f"edit_name_ja_{selected_id}",
        )

        edit_name_en = st.text_input(
            "英語名",
            value=safe_text(
                selected_row["name_en"]
            ),
            key=f"edit_name_en_{selected_id}",
        )

        edit_formula = st.text_input(
            "分子式",
            value=current_formula,
            key=f"edit_formula_{selected_id}",
        )

        edit_memo = st.text_area(
            "メモ",
            value=current_memo,
            key=f"edit_memo_{selected_id}",
        )

        if current_image:
            st.write(
                f"現在の画像：{current_image}"
            )
        else:
            st.warning(
                "構造式画像はまだ登録されていません。"
            )

        new_image = st.file_uploader(
            "構造式画像を追加・変更",
            type=["png", "jpg", "jpeg"],
            key=f"edit_image_{selected_id}",
        )

        if st.button(
            "更新する",
            key=f"update_{selected_id}",
        ):

            try:
                image_filename = current_image
                files_to_commit = {}

                if new_image is not None:
                    extension = os.path.splitext(
                        new_image.name
                    )[1].lower()

                    image_filename = (
                        f"{edit_name_en}{extension}"
                    )

                    files_to_commit[
                        f"{IMAGE_DIR}/{image_filename}"
                    ] = new_image.getvalue()

                row_index = edit_df[
                    edit_df["compound_id"]
                    == selected_id
                ].index[0]

                edit_df.loc[
                    row_index,
                    "name_ja",
                ] = edit_name_ja

                edit_df.loc[
                    row_index,
                    "name_en",
                ] = edit_name_en

                edit_df.loc[
                    row_index,
                    "formula",
                ] = edit_formula

                edit_df.loc[
                    row_index,
                    "image",
                ] = image_filename

                edit_df.loc[
                    row_index,
                    "memo",
                ] = edit_memo

                files_to_commit[
                    COMPOUNDS_PATH
                ] = dataframe_to_csv_bytes(
                    edit_df,
                    COMPOUND_COLUMNS,
                )

                commit_sha = commit_files(
                    files_to_commit,
                    f"Update compound {selected_id}",
                )

                st.success(
                    f"{selected_id} をGitHub上で更新しました！"
                )

                st.caption(
                    f"commit: {commit_sha[:7]}"
                )

                st.rerun()

            except Exception as e:
                st.error(
                    "更新中にエラーが発生しました。"
                )
                st.exception(e)

    else:
        st.warning(
            "検索条件に一致する化合物がありません。"
        )

else:
    st.info(
        "まだ編集できる化合物が登録されていません。"
    )


# =========================================================
# 反応データ登録
# =========================================================

st.divider()
st.subheader("🔁 反応データ登録")

compound_df = df_registered.copy()

if len(compound_df) > 0:

    compound_options = []

    for _, row in compound_df.iterrows():
        compound_options.append(
            f"{row['compound_id']} ｜ {row['name_ja']}"
        )

    reactant_option = st.selectbox(
        "反応物",
        compound_options,
        key="reaction_reactant",
    )

    product_option = st.selectbox(
        "生成物",
        compound_options,
        key="reaction_product",
    )

    condition = st.text_input(
        "反応条件",
        placeholder="例：酸化、加熱、濃硫酸など",
        key="reaction_condition",
    )

    reaction_type = st.text_input(
        "反応の種類",
        placeholder="例：酸化、還元、付加、脱離、エステル化",
        key="reaction_type",
    )

    reaction_memo = st.text_area(
        "メモ",
        placeholder="注意点や補足",
        key="reaction_memo",
    )

    reactant_id = (
        reactant_option
        .split(" ｜ ")[0]
    )

    product_id = (
        product_option
        .split(" ｜ ")[0]
    )

    next_reaction_number = 1

    if len(reaction_df) > 0:

        valid_numbers = (
            reaction_df["reaction_id"]
            .astype(str)
            .str.extract(r"rxn_(\d+)")[0]
            .dropna()
        )

        if len(valid_numbers) > 0:
            next_reaction_number = (
                valid_numbers.astype(int).max()
                + 1
            )

    reaction_id = (
        f"rxn_{next_reaction_number:03d}"
    )

    st.write(
        f"次の反応ID：**{reaction_id}**"
    )

    if st.button(
        "反応を登録する",
        key="register_reaction",
    ):

        try:
            new_reaction_row = pd.DataFrame(
                [
                    {
                        "reaction_id": reaction_id,
                        "reactant_id": reactant_id,
                        "product_id": product_id,
                        "condition": condition,
                        "reaction_type": reaction_type,
                        "memo": reaction_memo,
                        "custom_a": False,
                        "custom_b": False,
                    }
                ]
            )

            new_reaction_df = pd.concat(
                [
                    reaction_df[REACTION_COLUMNS],
                    new_reaction_row,
                ],
                ignore_index=True,
            )

            commit_sha = commit_files(
                {
                    REACTIONS_PATH:
                    dataframe_to_csv_bytes(
                        new_reaction_df,
                        REACTION_COLUMNS,
                    )
                },
                f"Register reaction {reaction_id}",
            )

            st.success(
                f"{reaction_id} をGitHubへ登録しました！"
            )

            st.caption(
                f"commit: {commit_sha[:7]}"
            )

            st.rerun()

        except Exception as e:
            st.error(
                "反応登録中にエラーが発生しました。"
            )
            st.exception(e)

else:
    st.info(
        "先に化合物を登録してください。"
    )


# =========================================================
# 登録済み反応一覧
# =========================================================

st.divider()
st.subheader("登録済み反応一覧")

if len(reaction_df) > 0:

    compound_name_map = dict(
        zip(
            compound_df["compound_id"],
            compound_df["name_ja"],
        )
    )

    display_reaction_df = reaction_df.copy()

    display_reaction_df[
        "reactant_name"
    ] = (
        display_reaction_df[
            "reactant_id"
        ].map(compound_name_map)
    )

    display_reaction_df[
        "product_name"
    ] = (
        display_reaction_df[
            "product_id"
        ].map(compound_name_map)
    )

    display_reaction_df = (
        display_reaction_df[
            [
                "reaction_id",
                "reactant_name",
                "condition",
                "product_name",
                "reaction_type",
                "memo",
            ]
        ]
    )

    st.dataframe(
        display_reaction_df,
        use_container_width=True,
        hide_index=True,
    )

else:
    st.info(
        "まだ反応は登録されていません。"
    )


# =========================================================
# カスタム出題する反応の設定
# =========================================================

st.divider()
st.subheader("🎯 カスタム出題する反応")

st.caption(
    "クラスや授業進度に合わせて、カスタムA・カスタムBを別々に保存できます。"
)

custom_df = reaction_df.copy()

if len(custom_df) > 0:

    compound_name_map = dict(
        zip(
            df_registered["compound_id"],
            df_registered["name_ja"],
        )
    )

    def normalize_custom(value):
        if pd.isna(value):
            return False

        if isinstance(value, bool):
            return value

        return (
            str(value)
            .strip()
            .lower()
            in {
                "true",
                "1",
                "yes",
                "on",
            }
        )

    custom_editor_df = custom_df.copy()

    custom_editor_df[
        "reactant_name"
    ] = (
        custom_editor_df[
            "reactant_id"
        ].map(compound_name_map)
    )

    custom_editor_df[
        "product_name"
    ] = (
        custom_editor_df[
            "product_id"
        ].map(compound_name_map)
    )

    custom_editor_df["custom_a"] = (
        custom_editor_df["custom_a"]
        .apply(normalize_custom)
    )

    custom_editor_df["custom_b"] = (
        custom_editor_df["custom_b"]
        .apply(normalize_custom)
    )

    custom_editor_df = (
        custom_editor_df[
            [
                "reaction_id",
                "reactant_name",
                "condition",
                "product_name",
                "reaction_type",
                "custom_a",
                "custom_b",
            ]
        ]
        .sort_values("reaction_id")
        .reset_index(drop=True)
    )

    edited_custom_df = st.data_editor(
        custom_editor_df,
        use_container_width=True,
        hide_index=True,
        disabled=[
            "reaction_id",
            "reactant_name",
            "condition",
            "product_name",
            "reaction_type",
        ],
        column_config={
            "reaction_id": st.column_config.TextColumn(
                "反応ID"
            ),
            "reactant_name": st.column_config.TextColumn(
                "反応物"
            ),
            "condition": st.column_config.TextColumn(
                "反応条件"
            ),
            "product_name": st.column_config.TextColumn(
                "生成物"
            ),
            "reaction_type": st.column_config.TextColumn(
                "反応の種類"
            ),
            "custom_a": st.column_config.CheckboxColumn(
                "カスタムA"
            ),
            "custom_b": st.column_config.CheckboxColumn(
                "カスタムB"
            ),
        },
        key="custom_reaction_editor",
    )

    save_col, clear_a_col, clear_b_col = st.columns(
        [1.2, 1, 1]
    )

    with save_col:
        save_custom = st.button(
            "カスタムA・Bを保存",
            type="primary",
            key="save_custom_reactions",
        )

    with clear_a_col:
        clear_custom_a = st.button(
            "Aをすべて解除",
            key="clear_custom_a",
        )

    with clear_b_col:
        clear_custom_b = st.button(
            "Bをすべて解除",
            key="clear_custom_b",
        )

    if save_custom:
        try:
            save_reaction_df = reaction_df.copy()

            custom_a_map = dict(
                zip(
                    edited_custom_df[
                        "reaction_id"
                    ].astype(str),
                    edited_custom_df[
                        "custom_a"
                    ].fillna(False).astype(bool),
                )
            )

            custom_b_map = dict(
                zip(
                    edited_custom_df[
                        "reaction_id"
                    ].astype(str),
                    edited_custom_df[
                        "custom_b"
                    ].fillna(False).astype(bool),
                )
            )

            save_reaction_df["custom_a"] = (
                save_reaction_df[
                    "reaction_id"
                ]
                .astype(str)
                .map(custom_a_map)
                .fillna(False)
            )

            save_reaction_df["custom_b"] = (
                save_reaction_df[
                    "reaction_id"
                ]
                .astype(str)
                .map(custom_b_map)
                .fillna(False)
            )

            commit_sha = commit_files(
                {
                    REACTIONS_PATH:
                    dataframe_to_csv_bytes(
                        save_reaction_df,
                        REACTION_COLUMNS,
                    )
                },
                "Update custom A and B reactions",
            )

            st.success(
                "カスタムA・BをGitHubへ保存しました！"
            )
            st.caption(
                f"commit: {commit_sha[:7]}"
            )

            st.rerun()

        except Exception as e:
            st.error(
                "カスタム反応の保存中にエラーが発生しました。"
            )
            st.exception(e)

    if clear_custom_a:
        try:
            save_reaction_df = reaction_df.copy()
            save_reaction_df["custom_a"] = False

            commit_sha = commit_files(
                {
                    REACTIONS_PATH:
                    dataframe_to_csv_bytes(
                        save_reaction_df,
                        REACTION_COLUMNS,
                    )
                },
                "Clear custom A reactions",
            )

            st.success(
                "カスタムAをすべて解除しました！"
            )
            st.caption(
                f"commit: {commit_sha[:7]}"
            )

            st.rerun()

        except Exception as e:
            st.error(
                "カスタムA解除中にエラーが発生しました。"
            )
            st.exception(e)

    if clear_custom_b:
        try:
            save_reaction_df = reaction_df.copy()
            save_reaction_df["custom_b"] = False

            commit_sha = commit_files(
                {
                    REACTIONS_PATH:
                    dataframe_to_csv_bytes(
                        save_reaction_df,
                        REACTION_COLUMNS,
                    )
                },
                "Clear custom B reactions",
            )

            st.success(
                "カスタムBをすべて解除しました！"
            )
            st.caption(
                f"commit: {commit_sha[:7]}"
            )

            st.rerun()

        except Exception as e:
            st.error(
                "カスタムB解除中にエラーが発生しました。"
            )
            st.exception(e)

else:
    st.info(
        "カスタム設定できる反応がありません。"
    )


# =========================================================
# 登録済み反応の編集
# =========================================================

st.divider()
st.subheader("登録済み反応の編集")

edit_reaction_df = reaction_df.copy()
compound_df = df_registered.copy()

if (
    len(edit_reaction_df) > 0
    and len(compound_df) > 0
):

    compound_name_map = dict(
        zip(
            compound_df["compound_id"],
            compound_df["name_ja"],
        )
    )

    edit_reaction_df[
        "reactant_name"
    ] = (
        edit_reaction_df[
            "reactant_id"
        ].map(compound_name_map)
    )

    edit_reaction_df[
        "product_name"
    ] = (
        edit_reaction_df[
            "product_id"
        ].map(compound_name_map)
    )

    search_reaction = st.text_input(
        "編集する反応を検索",
        placeholder=(
            "反応ID、反応物名、"
            "生成物名の一部を入力"
        ),
        key="reaction_edit_search",
    )

    if search_reaction:

        filtered_reactions = edit_reaction_df[
            edit_reaction_df[
                "reaction_id"
            ]
            .astype(str)
            .str.contains(
                search_reaction,
                case=False,
                na=False,
            )
            |
            edit_reaction_df[
                "reactant_name"
            ]
            .astype(str)
            .str.contains(
                search_reaction,
                case=False,
                na=False,
            )
            |
            edit_reaction_df[
                "product_name"
            ]
            .astype(str)
            .str.contains(
                search_reaction,
                case=False,
                na=False,
            )
        ]

    else:
        filtered_reactions = (
            edit_reaction_df
        )

    if len(filtered_reactions) > 0:

        reaction_options = []

        for _, row in (
            filtered_reactions.iterrows()
        ):
            reaction_options.append(
                f"{row['reaction_id']} ｜ "
                f"{row['reactant_name']} → "
                f"{row['product_name']}"
            )

        selected_reaction_option = (
            st.selectbox(
                "編集する反応",
                reaction_options,
                key="reaction_edit_select",
            )
        )

        selected_reaction_id = (
            selected_reaction_option
            .split(" ｜ ")[0]
        )

        selected_reaction_row = (
            edit_reaction_df[
                edit_reaction_df[
                    "reaction_id"
                ]
                == selected_reaction_id
            ].iloc[0]
        )

        st.write(
            f"**reaction_id："
            f"{selected_reaction_id}**"
        )

        def reaction_safe_text(value):
            return (
                ""
                if pd.isna(value)
                else str(value)
            )

        edit_condition = st.text_input(
            "反応条件",
            value=reaction_safe_text(
                selected_reaction_row[
                    "condition"
                ]
            ),
            key=(
                f"edit_condition_"
                f"{selected_reaction_id}"
            ),
        )

        compound_options = []

        for _, row in compound_df.iterrows():
            compound_options.append(
                f"{row['compound_id']} ｜ "
                f"{row['name_ja']}"
            )

        current_reactant_id = str(
            selected_reaction_row[
                "reactant_id"
            ]
        )

        reactant_index = next(
            (
                i
                for i, option
                in enumerate(
                    compound_options
                )
                if option.startswith(
                    current_reactant_id
                    + " ｜"
                )
            ),
            0,
        )

        edit_reactant_option = (
            st.selectbox(
                "反応物",
                compound_options,
                index=reactant_index,
                key=(
                    f"edit_reactant_"
                    f"{selected_reaction_id}"
                ),
            )
        )

        edit_reactant_id = (
            edit_reactant_option
            .split(" ｜ ")[0]
        )

        current_product_id = str(
            selected_reaction_row[
                "product_id"
            ]
        )

        product_index = next(
            (
                i
                for i, option
                in enumerate(
                    compound_options
                )
                if option.startswith(
                    current_product_id
                    + " ｜"
                )
            ),
            0,
        )

        edit_product_option = (
            st.selectbox(
                "生成物",
                compound_options,
                index=product_index,
                key=(
                    f"edit_product_"
                    f"{selected_reaction_id}"
                ),
            )
        )

        edit_product_id = (
            edit_product_option
            .split(" ｜ ")[0]
        )

        edit_reaction_type = st.text_input(
            "反応の種類",
            value=reaction_safe_text(
                selected_reaction_row[
                    "reaction_type"
                ]
            ),
            key=(
                f"edit_reaction_type_"
                f"{selected_reaction_id}"
            ),
        )

        edit_reaction_memo = st.text_area(
            "メモ",
            value=reaction_safe_text(
                selected_reaction_row[
                    "memo"
                ]
            ),
            key=(
                f"edit_reaction_memo_"
                f"{selected_reaction_id}"
            ),
        )

        if st.button(
            "反応を更新する",
            key=(
                f"update_reaction_"
                f"{selected_reaction_id}"
            ),
        ):

            try:
                save_reaction_df = (
                    reaction_df.copy()
                )

                row_index = (
                    save_reaction_df[
                        save_reaction_df[
                            "reaction_id"
                        ]
                        == selected_reaction_id
                    ].index[0]
                )

                save_reaction_df.loc[
                    row_index,
                    "reactant_id",
                ] = edit_reactant_id

                save_reaction_df.loc[
                    row_index,
                    "product_id",
                ] = edit_product_id

                save_reaction_df.loc[
                    row_index,
                    "condition",
                ] = edit_condition

                save_reaction_df.loc[
                    row_index,
                    "reaction_type",
                ] = edit_reaction_type

                save_reaction_df.loc[
                    row_index,
                    "memo",
                ] = edit_reaction_memo

                commit_sha = commit_files(
                    {
                        REACTIONS_PATH:
                        dataframe_to_csv_bytes(
                            save_reaction_df,
                            REACTION_COLUMNS,
                        )
                    },
                    (
                        "Update reaction "
                        f"{selected_reaction_id}"
                    ),
                )

                st.success(
                    f"{selected_reaction_id} "
                    "をGitHub上で更新しました！"
                )

                st.caption(
                    f"commit: {commit_sha[:7]}"
                )

                st.rerun()

            except Exception as e:
                st.error(
                    "反応更新中にエラーが発生しました。"
                )
                st.exception(e)

    else:
        st.warning(
            "検索条件に一致する反応がありません。"
        )

else:
    st.info(
        "まだ編集できる反応が登録されていません。"
    )
