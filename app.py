%%writefile app.py

!pip install streamlit

import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="RPG", page_icon="⚔️")

# -----------------------------
# 初期化
# -----------------------------
if "player" not in st.session_state:
    st.session_state.player = {
        "名前": "(˙𐃷˙)",
        "レベル": 1,
        "HP": 50,
        "最大HP": 50,
        "攻撃力": 20,
        "経験値": 0,
        "所持金": 100
    }

if "map" not in st.session_state:
    st.session_state.map = random.choices(
        ["戦闘", "ショップ", "宝箱", "回復", "何もない"],
        weights=[40, 10, 15, 10, 25],
        k=50
    )

if "position" not in st.session_state:
    st.session_state.position = 0

if "mode" not in st.session_state:
    st.session_state.mode = "map"

if "enemy" not in st.session_state:
    st.session_state.enemy = None

player = st.session_state.player

# -----------------------------
# 敵データ
# -----------------------------
data = {
    "敵の名前": [
        "(´・ω・`)",
        "( ｀ー´)ノ",
        "('ω')",
        "('Д')",
        "(/・ω・)/",
        "(˙𐃷˙(˙𐃷˙)˙𐃷˙)"
    ],
    "HP": [20, 30, 10, 5, 40, 150],
    "攻撃": [3, 7, 5, 15, 20, 50],
    "経験値": [15, 25, 10, 15, 45, 80]
}

df = pd.DataFrame(data)

# -----------------------------
# サイドバー
# -----------------------------
st.sidebar.title("プレイヤー")

st.sidebar.write("Lv", player["レベル"])
st.sidebar.write("HP", f'{player["HP"]}/{player["最大HP"]}')
st.sidebar.write("攻撃", player["攻撃力"])
st.sidebar.write("経験値", player["経験値"])
st.sidebar.write("所持金", f'{player["所持金"]} G')

# -----------------------------
# レベルアップ
# -----------------------------
def levelup():

    while player["経験値"] >= 100:

        player["経験値"] -= 100
        player["レベル"] += 1
        player["最大HP"] += 10
        player["HP"] = player["最大HP"]
        player["攻撃力"] += 5

        st.success("🎉 レベルアップ！")

# -----------------------------
# 敵生成
# -----------------------------
def create_enemy(boss=False):

    if boss:
        e = df.iloc[-1].to_dict()
    else:
        e = df.iloc[random.randint(0, len(df)-2)].to_dict()

    return {
        "名前": e["敵の名前"],
        "HP": e["HP"],
        "最大HP": e["HP"],
        "攻撃": e["攻撃"],
        "経験値": e["経験値"],
        "boss": boss
    }

# -----------------------------
# 戦闘開始
# -----------------------------
def start_battle(boss=False):

    st.session_state.enemy = create_enemy(boss)
    st.session_state.mode = "battle"

# -----------------------------
# 戦闘
# -----------------------------
def battle():

    enemy = st.session_state.enemy

    st.header(enemy["名前"])

    st.progress(enemy["HP"] / enemy["最大HP"])

    st.write(
        f'敵HP : {enemy["HP"]}/{enemy["最大HP"]}'
    )

    if st.button("⚔️ 攻撃"):

        damage = random.randint(
            player["攻撃力"]-5,
            player["攻撃力"]+5
        )

        enemy["HP"] -= damage

        st.success(f"{damage}ダメージ！")

        # 撃破
        if enemy["HP"] <= 0:

            money = random.randint(20, 60)

            player["所持金"] += money
            player["経験値"] += enemy["経験値"]

            levelup()

            st.success(f"{enemy['名前']}を倒した！")
            st.success(f"{money}G獲得！")

            st.session_state.enemy = None

            # ボスだったらクリア
            if enemy["boss"]:
                st.session_state.mode = "clear"
            else:
                st.session_state.mode = "map"
                st.session_state.position += 1

            st.rerun()

        # 敵攻撃
        if enemy["boss"]:

            total = 0

            for i in range(2):

                d = random.randint(1, enemy["攻撃"])

                total += d
                player["HP"] -= d

            st.error(
                f"🐺 ケルベロスの2連攻撃！ {total}ダメージ！"
            )

        else:

            d = random.randint(1, enemy["攻撃"])

            player["HP"] -= d

            st.error(f"{d}ダメージ！")

        # ゲームオーバー
        if player["HP"] <= 0:

            st.session_state.mode = "gameover"

        st.rerun()

# -----------------------------
# ショップ
# -----------------------------
def shop():

    st.subheader("🏪 ショップ")

    st.write("何を買いますか？")

    col1, col2 = st.columns(2)

    with col1:

        if st.button("❤️ HP全回復 (50G)"):

            if player["所持金"] >= 50:

                player["所持金"] -= 50
                player["HP"] = player["最大HP"]

                st.success("HPが全回復した！")

            else:

                st.error("お金が足りない！")

    with col2:

        if st.button("⚔️ 攻撃力+5 (80G)"):

            if player["所持金"] >= 80:

                player["所持金"] -= 80
                player["攻撃力"] += 5

                st.success("攻撃力が5上がった！")

            else:

                st.error("お金が足りない！")

    if st.button("次へ"):

        st.session_state.position += 1
        st.session_state.mode = "map"

        st.rerun()


# -----------------------------
# 宝箱
# -----------------------------
def treasure():

    st.subheader("📦 宝箱")

    r = random.randint(1, 3)

    if r == 1:

        g = random.randint(30, 100)

        player["所持金"] += g

        st.success(f"{g}G手に入れた！")

    elif r == 2:

        player["攻撃力"] += 3

        st.success("攻撃力が3上がった！")

    else:

        player["HP"] = player["最大HP"]

        st.success("HPが全回復した！")

    if st.button("次へ "):

        st.session_state.position += 1
        st.session_state.mode = "map"

        st.rerun()


# -----------------------------
# 回復
# -----------------------------
def heal():

    st.subheader("❤️ 回復ポイント")

    h = random.randint(10, 30)

    player["HP"] += h

    if player["HP"] > player["最大HP"]:

        player["HP"] = player["最大HP"]

    st.success(f"{h}回復した！")

    if st.button("次へ  "):

        st.session_state.position += 1
        st.session_state.mode = "map"

        st.rerun()


# -----------------------------
# マップ
# -----------------------------
def map_event():

    st.title("🗺️ マップ")

    st.write(f"### {st.session_state.position+1} / 50 マス")

    # ゴール
    if st.session_state.position >= 50:

        st.success("ゴールに到着！")

        if st.button("👹 ラスボスへ"):

            start_battle(True)

            st.rerun()

        return

    event = st.session_state.map[st.session_state.position]

    st.write("イベント：", event)

    if event == "戦闘":

        if st.button("戦闘開始"):

            start_battle()

            st.rerun()

    elif event == "ショップ":

        shop()

    elif event == "宝箱":

        treasure()

    elif event == "回復":

        heal()

    else:

        st.info("何もなかった…")

        if st.button("次のマスへ"):

            st.session_state.position += 1

            st.rerun()

# -----------------------------
# メイン画面
# -----------------------------
if st.session_state.mode == "map":

    map_event()

elif st.session_state.mode == "battle":

    battle()

elif st.session_state.mode == "gameover":

    st.title("💀 ゲームオーバー")

    st.error("あなたは倒れてしまった...")

    if st.button("もう一度遊ぶ"):

        for key in list(st.session_state.keys()):
            del st.session_state[key]

        st.rerun()

elif st.session_state.mode == "clear":

    st.title("🏆 ゲームクリア！")

    st.balloons()

    st.success("ケルベロスを倒した！")

    st.write("### 最終ステータス")

    st.write("レベル :", player["レベル"])
    st.write("HP :", player["HP"], "/", player["最大HP"])
    st.write("攻撃力 :", player["攻撃力"])
    st.write("経験値 :", player["経験値"])
    st.write("所持金 :", player["所持金"], "G")

    if st.button("最初から遊ぶ"):

        for key in list(st.session_state.keys()):
            del st.session_state[key]

        st.rerun()
