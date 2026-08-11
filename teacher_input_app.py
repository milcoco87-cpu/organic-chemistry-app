import streamlit as st
import pandas as pd
import csv
import os


# =========================================================
# パス設定
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_PATH = os.path.join(BASE_DIR, "compounds.csv")
MASTER_CSV_PATH = os.path.join(BASE_DIR, "compound_master.csv")
MAP_CSV_PATH = os.path.join(BASE_DIR, "compound_chart_map.csv")
REACTION_CSV_PATH = os.path.join(BASE_DIR, "reactions.csv")

IMAGE_DIR = os.path.join(BASE_DIR, "images")


# =========================================================
# compounds.csv がなければ作成
# =========================================================

if not os.path.exists(CSV_PATH):
    with open(
        CSV_PATH,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:
        writer = csv.writer(f)
        writer.writerow([
            "compound_id",
            "name_ja",
            "name_en",
            "formula",
            "image",
            "memo"
        ])


# =========================================================
# reactions.csv がなければ作成
# =========================================================

if not os.path.exists(REACTION_CSV_PATH):
    with open(
        REACTION_CSV_PATH,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:
        writer = csv.writer(f)
        writer.writerow([
            "reaction_id",
            "reactant_id",
            "product_id",
            "condition",
            "reaction_type",
            "memo"
        ])


# =========================================================
# Streamlit画面設定
# =========================================================

st.set_page_config(
    page_title="教材データ入力",
    page_icon="🧪",
    layout="wide"
)


# =========================================================
# 次の未登録化合物を取得
# =========================================================

next_id = ""
next_name_ja = ""
next_name_en = ""

if os.path.exists(CSV_PATH) and os.path.exists(MASTER_CSV_PATH):

    df_registered = pd.read_csv(CSV_PATH)
    master_df = pd.read_csv(MASTER_CSV_PATH)

    registered_ids = (
        df_registered["compound_id"]
        .astype(str)
        .tolist()
    )

    unregistered_master = master_df[
        ~master_df["compound_id"].isin(registered_ids)
    ]

    if not unregistered_master.empty:
        next_row = unregistered_master.iloc[0]

        next_id = next_row["compound_id"]
        next_name_ja = next_row["name_ja"]
        next_name_en = next_row["name_en"]

# =========================================================
# 化合物データ登録
# =========================================================

st.title("🧪 教材データ入力アプリ")

st.write("有機化合物の教材データを登録します。")

st.subheader("化合物を登録")

compound_id = st.text_input(
    "compound_id",
    value=next_id
)

name_ja = st.text_input(
    "化合物名（日本語）",
    value=next_name_ja
)

name_en = st.text_input(
    "化合物名（英語）",
    value=next_name_en
)

formula = st.text_input(
    "分子式",
    placeholder="例：C2H6O"
)

image = st.file_uploader(
    "構造式画像",
    type=["png", "jpg", "jpeg"]
)
memo = st.text_area(
    "メモ",
    placeholder="例：OとNaは結合線で結ばない"
)
if st.button("登録する"):

    if not compound_id or not name_ja or not name_en:
        st.error("compound_id、日本語名、英語名は入力してください。")

    else:
        existing_ids = []

        if os.path.exists(CSV_PATH):
            df_existing = pd.read_csv(CSV_PATH)
            existing_ids = df_existing["compound_id"].astype(str).tolist()

        if compound_id in existing_ids:
            st.error(f"{compound_id} はすでに登録されています。")

        else:
            image_filename = ""

            if image is not None:
                os.makedirs(IMAGE_DIR, exist_ok=True)

                extension = os.path.splitext(image.name)[1].lower()
                image_filename = f"{name_en}{extension}"
                image_path = os.path.join(IMAGE_DIR, image_filename)

                with open(image_path, "wb") as f:
                    f.write(image.getbuffer())

            with open(
                CSV_PATH,
                "a",
                newline="",
                encoding="utf-8-sig"
            ) as f:
                writer = csv.writer(f)

                writer.writerow([
                    compound_id,
                    name_ja,
                    name_en,
                    formula,
                    image_filename,
                    memo
                ])

            st.success("登録しました！")

            st.write("compound_id：", compound_id)
            st.write("日本語名：", name_ja)
            st.write("英語名：", name_en)
            st.write("分子式：", formula)
            st.write("メモ：", memo)

            if image is not None:
                st.image(image, caption=name_ja, width=300)

st.divider()
st.subheader("登録済み化合物一覧")

if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
    df["image_status"] = df["image"].apply(
    lambda x: "✅ あり" if pd.notna(x) and str(x).strip() != "" else "⚠️ なし"
)
    df = df.sort_values("compound_id")

    if len(df) > 0:
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
# =========================================================
# 登録進捗の表示
# =========================================================

        # 系統図に含まれる初期95件
        base_total = 95
        base_ids = [f"cmp_{i:03d}" for i in range(1, base_total + 1)]

        registered_ids = df["compound_id"].astype(str).tolist()

        # 初期95件のうち登録済みのもの
        registered_base_ids = [
            compound_id
            for compound_id in registered_ids
            if compound_id in base_ids
        ]

        # 初期95件のうち未登録のもの
        unregistered_ids = [
            compound_id
            for compound_id in base_ids
            if compound_id not in registered_ids
        ]

        # 96番以降の追加化合物
        additional_count = len([
            compound_id
            for compound_id in registered_ids
            if compound_id not in base_ids
        ])

        st.write(
            f"系統図対象：{len(registered_base_ids)} / {base_total} 件"
        )

        st.write(
            f"追加化合物：{additional_count} 件"
        )

        st.write(
            f"データベース全体：{len(df)} 件"
        )

    if unregistered_ids:
        next_id = unregistered_ids[0]

        master_df = pd.read_csv(MASTER_CSV_PATH)

        next_row = master_df[
            master_df["compound_id"] == next_id
        ]

        if not next_row.empty:
            next_name_ja = next_row.iloc[0]["name_ja"]
            next_name_en = next_row.iloc[0]["name_en"]

            st.info(
                f"次の未登録：{next_id} "
                f"｜{next_name_ja} "
                f"｜{next_name_en}"
            )
        else:
            st.info(f"次の未登録ID：{next_id}")

        missing_image_count = (df["image_status"] == "⚠️ なし").sum()

        if missing_image_count > 0:
            st.warning(f"構造式画像が未登録：{missing_image_count} 件")
        else:
            st.success("すべての化合物に構造式画像が登録されています。")

    else:
        st.info("まだ化合物は登録されていません。")

# =========================================================
# 登録済み化合物の編集
# =========================================================

st.divider()
st.subheader("✏️ 登録済み化合物を編集")

if os.path.exists(CSV_PATH):
    edit_df = pd.read_csv(CSV_PATH)

    if len(edit_df) > 0:

        # 検索欄
        search_word = st.text_input(
            "編集する化合物を検索",
            placeholder="ID、日本語名、英語名の一部を入力"
        )

        # 検索結果を絞り込む
        if search_word:
            search_lower = search_word.lower()

            filtered_df = edit_df[
                edit_df["compound_id"].astype(str).str.lower().str.contains(
                    search_lower, na=False
                )
                |
                edit_df["name_ja"].astype(str).str.contains(
                    search_word, na=False
                )
                |
                edit_df["name_en"].astype(str).str.lower().str.contains(
                    search_lower, na=False
                )
            ]
        else:
            filtered_df = edit_df

        if len(filtered_df) > 0:

            # 候補表示用の文字列を作る
            options = []

            for _, row in filtered_df.iterrows():
                options.append(
                    f"{row['compound_id']} ｜ "
                    f"{row['name_ja']} ｜ "
                    f"{row['name_en']}"
                )

            selected_option = st.selectbox(
                "編集する化合物",
                options
            )

            # 選択した compound_id を取り出す
            selected_id = selected_option.split(" ｜ ")[0]

            selected_row = edit_df[
                edit_df["compound_id"] == selected_id
            ].iloc[0]

            # NaN対策
            current_formula = (
                ""
                if pd.isna(selected_row["formula"])
                else str(selected_row["formula"])
            )
            current_memo = (
                ""
                if pd.isna(selected_row["memo"])
                else str(selected_row["memo"])
            )
            current_image = (
                ""
                if pd.isna(selected_row["image"])
                else str(selected_row["image"])
            )

            st.write(f"**compound_id：{selected_id}**")

            edit_name_ja = st.text_input(
                "日本語名",
                value=str(selected_row["name_ja"]),
                key=f"edit_name_ja_{selected_id}"
            )

            edit_name_en = st.text_input(
                "英語名",
                value=str(selected_row["name_en"]),
                key=f"edit_name_en_{selected_id}"
            )

            edit_formula = st.text_input(
                "分子式",
                value=current_formula,
                key=f"edit_formula_{selected_id}"
            )
            edit_memo = st.text_area(
                "メモ",
                value=current_memo,
                key=f"edit_memo_{selected_id}"
            )


            if current_image:
                st.write(f"現在の画像：{current_image}")
            else:
                st.warning("構造式画像はまだ登録されていません。")

            new_image = st.file_uploader(
                "構造式画像を追加・変更",
                type=["png", "jpg", "jpeg"],
                key=f"edit_image_{selected_id}"
            )

            if st.button(
                "更新する",
                key=f"update_{selected_id}"
            ):

                # 画像を変更しない場合は現在の画像名をそのまま使う
                image_filename = current_image

                # 新しい画像が選ばれた場合
                if new_image is not None:

                    os.makedirs(
                        IMAGE_DIR,
                        exist_ok=True
                    )

                    # 英語名を画像ファイル名に使用
                    extension = os.path.splitext(new_image.name)[1].lower()
                    image_filename = f"{edit_name_en}{extension}"  

                    image_path = os.path.join(
                        IMAGE_DIR,
                        image_filename
                    )

                    with open(image_path, "wb") as f:
                        f.write(new_image.getbuffer())

                # CSV上の該当行を更新
                row_index = edit_df[
                    edit_df["compound_id"] == selected_id
                ].index[0]

                edit_df.loc[row_index, "name_ja"] = edit_name_ja
                edit_df.loc[row_index, "name_en"] = edit_name_en
                edit_df.loc[row_index, "formula"] = edit_formula
                edit_df.loc[row_index, "image"] = image_filename
                edit_df.loc[row_index, "memo"] = edit_memo

                # CSVを書き直す
                edit_df.to_csv(
                    CSV_PATH,
                    index=False,
                    encoding="utf-8-sig"
                )

                st.success(
                    f"{selected_id} を更新しました！"
                )

                st.rerun()

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

    if os.path.exists(CSV_PATH):

        compound_df = pd.read_csv(CSV_PATH)

        if len(compound_df) > 0:

            # 表示用の候補
            compound_options = []

            for _, row in compound_df.iterrows():
                compound_options.append(
                    f"{row['compound_id']} ｜ {row['name_ja']}"
                )

            reactant_option = st.selectbox(
                "反応物",
                compound_options,
                key="reaction_reactant"
            )

            product_option = st.selectbox(
                "生成物",
                compound_options,
                key="reaction_product"
            )

            condition = st.text_input(
                "反応条件",
                placeholder="例：酸化、加熱、濃硫酸など",
                key="reaction_condition"
            )

            reaction_type = st.text_input(
                "反応の種類",
                placeholder="例：酸化、還元、付加、脱離、エステル化",
                key="reaction_type"
            )

            reaction_memo = st.text_area(
                "メモ",
                placeholder="注意点や補足",
                key="reaction_memo"
            )

            # 選択文字列からIDだけ取り出す
            reactant_id = reactant_option.split(" ｜ ")[0]
            product_id = product_option.split(" ｜ ")[0]

            # 次のreaction_idを作る
            next_reaction_number = 1

            if os.path.exists(REACTION_CSV_PATH):
                reaction_df = pd.read_csv(REACTION_CSV_PATH)

                if len(reaction_df) > 0:
                    reaction_numbers = (
                        reaction_df["reaction_id"]
                        .astype(str)
                        .str.replace("rxn_", "", regex=False)
                        .astype(int)
                    )

                    next_reaction_number = reaction_numbers.max() + 1

            reaction_id = f"rxn_{next_reaction_number:03d}"

            st.write(f"次の反応ID：**{reaction_id}**")

            if st.button(
                "反応を登録する",
                key="register_reaction"
            ):

                with open(
                    REACTION_CSV_PATH,
                    "a",
                    newline="",
                    encoding="utf-8-sig"
                ) as f:

                    writer = csv.writer(f)

                    writer.writerow([
                        reaction_id,
                        reactant_id,
                        product_id,
                        condition,
                        reaction_type,
                        reaction_memo
                    ])

                st.success(
                    f"{reaction_id} を登録しました！"
                )

                st.rerun()

        else:
            st.info(
                "先に化合物を登録してください。"
            )
# =========================================================
# 登録済み反応一覧
# =========================================================

st.divider()
st.subheader("登録済み反応一覧")

if os.path.exists(REACTION_CSV_PATH):
    reaction_df = pd.read_csv(REACTION_CSV_PATH)

    if len(reaction_df) > 0:

        compound_df = pd.read_csv(CSV_PATH)

        # compound_id → 日本語名 の対応表
        compound_name_map = dict(
            zip(
                compound_df["compound_id"],
                compound_df["name_ja"]
            )
        )

        display_reaction_df = reaction_df.copy()

        display_reaction_df["reactant_name"] = (
            display_reaction_df["reactant_id"]
            .map(compound_name_map)
        )

        display_reaction_df["product_name"] = (
            display_reaction_df["product_id"]
            .map(compound_name_map)
        )

        display_reaction_df = display_reaction_df[
            [
                "reaction_id",
                "reactant_name",
                "condition",
                "product_name",
                "reaction_type",
                "memo"
            ]
        ]

        st.dataframe(
            display_reaction_df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("まだ反応は登録されていません。")

# =========================================================
# 登録済み反応の編集
# =========================================================

st.divider()
st.subheader("登録済み反応の編集")

if os.path.exists(REACTION_CSV_PATH):
    edit_reaction_df = pd.read_csv(REACTION_CSV_PATH)
    compound_df = pd.read_csv(CSV_PATH)

    if len(edit_reaction_df) > 0:

        # compound_id → 日本語名
        compound_name_map = dict(
            zip(
                compound_df["compound_id"],
                compound_df["name_ja"]
            )
        )

        # 検索用に名前を追加
        edit_reaction_df["reactant_name"] = (
            edit_reaction_df["reactant_id"]
            .map(compound_name_map)
        )

        edit_reaction_df["product_name"] = (
            edit_reaction_df["product_id"]
            .map(compound_name_map)
        )

        search_reaction = st.text_input(
            "編集する反応を検索",
            placeholder="反応ID、反応物名、生成物名の一部を入力",
            key="reaction_edit_search"
        )

        if search_reaction:
            filtered_reactions = edit_reaction_df[
                edit_reaction_df["reaction_id"]
                .astype(str)
                .str.contains(
                    search_reaction,
                    case=False,
                    na=False
                )
                |
                edit_reaction_df["reactant_name"]
                .astype(str)
                .str.contains(
                    search_reaction,
                    case=False,
                    na=False
                )
                |
                edit_reaction_df["product_name"]
                .astype(str)
                .str.contains(
                    search_reaction,
                    case=False,
                    na=False
                )
            ]
        else:
            filtered_reactions = edit_reaction_df

        if len(filtered_reactions) > 0:

            reaction_options = []

            for _, row in filtered_reactions.iterrows():
                reaction_options.append(
                    f"{row['reaction_id']} ｜ "
                    f"{row['reactant_name']} → "
                    f"{row['product_name']}"
                )

            selected_reaction_option = st.selectbox(
                "編集する反応",
                reaction_options,
                key="reaction_edit_select"
            )

            selected_reaction_id = (
                selected_reaction_option
                .split(" ｜ ")[0]
            )

            selected_reaction_row = edit_reaction_df[
                edit_reaction_df["reaction_id"]
                == selected_reaction_id
            ].iloc[0]

            st.write(
                f"**reaction_id：{selected_reaction_id}**"
            )

            edit_condition = st.text_input(
                "反応条件",
                value=""
                if pd.isna(selected_reaction_row["condition"])
                else str(
                    selected_reaction_row["condition"]
                ),
                key=f"edit_condition_{selected_reaction_id}"
            )

            # 化合物の選択肢
            compound_options = []

            for _, row in compound_df.iterrows():
                compound_options.append(
                    f"{row['compound_id']} ｜ {row['name_ja']}"
                )

            # 現在登録されている反応物
            current_reactant_id = selected_reaction_row["reactant_id"]

            reactant_index = next(
                i for i, option in enumerate(compound_options)
                if option.startswith(current_reactant_id)
            )

            edit_reactant_option = st.selectbox(
                "反応物",
                compound_options,
                index=reactant_index,
                key=f"edit_reactant_{selected_reaction_id}"
            )

            edit_reactant_id = edit_reactant_option.split(" ｜ ")[0]


            # 現在登録されている生成物
            current_product_id = selected_reaction_row["product_id"]

            product_index = next(
                i for i, option in enumerate(compound_options)
                if option.startswith(current_product_id)
            )

            edit_product_option = st.selectbox(
                "生成物",
                compound_options,
                index=product_index,
                key=f"edit_product_{selected_reaction_id}"
            )

            edit_product_id = edit_product_option.split(" ｜ ")[0]

            edit_reaction_type = st.text_input(
                "反応の種類",
                value=""
                if pd.isna(selected_reaction_row["reaction_type"])
                else str(
                    selected_reaction_row["reaction_type"]
                ),
                key=f"edit_reaction_type_{selected_reaction_id}"
            )

            edit_reaction_memo = st.text_area(
                "メモ",
                value=""
                if pd.isna(selected_reaction_row["memo"])
                else str(
                    selected_reaction_row["memo"]
                ),
                key=f"edit_reaction_memo_{selected_reaction_id}"
            )

            if st.button(
                "反応を更新する",
                key=f"update_reaction_{selected_reaction_id}"
            ):

                row_index = edit_reaction_df[
                    edit_reaction_df["reaction_id"]
                    == selected_reaction_id
                ].index[0]

                edit_reaction_df.loc[
                    row_index,
                    "reactant_id"
                ] = edit_reactant_id

                edit_reaction_df.loc[
                    row_index,
                    "product_id"
                ] = edit_product_id

                edit_reaction_df.loc[
                    row_index,
                    "condition"
                ] = edit_condition

                edit_reaction_df.loc[
                    row_index,
                    "reaction_type"
                ] = edit_reaction_type

                edit_reaction_df.loc[
                    row_index,
                    "memo"
                ] = edit_reaction_memo

                # 表示用に追加した列は保存しない
                save_reaction_df = edit_reaction_df[
                    [
                        "reaction_id",
                        "reactant_id",
                        "product_id",
                        "condition",
                        "reaction_type",
                        "memo"
                    ]
                ]

                save_reaction_df.to_csv(
                    REACTION_CSV_PATH,
                    index=False,
                    encoding="utf-8-sig"
                )

                st.success(
                    f"{selected_reaction_id} を更新しました！"
                )

                st.rerun()

        else:
            st.warning(
                "検索条件に一致する反応がありません。"
            )

    else:
        st.info(
            "まだ編集できる反応が登録されていません。"
        )