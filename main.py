import streamlit as st
import pandas as pd
import random

# --- 1. データの読み込み ---
@st.cache_data
def load_data():
    try:
        # header=None にして1行目から読み込み
        df = pd.read_csv(
            'kobun350.csv', 
            engine='python', 
            encoding='utf-8-sig',
            header=None
        )
        # 1行目がヘッダー（英語など）の場合に除外する処理
        first_cell = str(df.iloc[0, 0]).lower()
        if "question" in first_cell or "単語" in first_cell:
            df = df.iloc[1:].reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"CSV読み込みエラー: {e}")
        return None

df = load_data()

# --- 2. 画面設定 ---
st.set_page_config(page_title="古文 意地でも覚える350語", layout="centered")

st.markdown("""
    <style>
    .stMarkdown p { line-height: 1.7; }
    .main { background-color: #fdfaf5; }
    .highlight-green {
        color: #2e7d32; 
        font-weight: bold; 
        border-bottom: 2px solid #2e7d32;
    }
    /* スマホでボタンを押しやすく */
    .stButton button {
        font-size: 16px !important;
        min-height: 3.5em;
        margin-bottom: 5px;
    }
    /* 例文ボックスの調整 */
    .sentence-box {
        background-color: #f0f4f0; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 8px solid #2e7d32; 
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("古文 意地でも覚える350語")

if df is None:
    st.error("⚠️ 'kobun350.csv' が見つかりません。GitHubのファイル名を確認してください。")
    st.stop()

# --- 3. セッション状態の初期化 ---
if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.questions = df.sample(frac=1).reset_index(drop=True)
    st.session_state.new_ques = True
    st.session_state.answered = False

# 進捗表示
st.sidebar.header("📊 学習状況")
st.sidebar.write(f"進捗: {st.session_state.idx} / {len(st.session_state.questions)}")

# --- 4. クイズ本編 ---
if st.session_state.idx < len(st.session_state.questions):
    row = st.session_state.questions.iloc[st.session_state.idx]
    st.progress((st.session_state.idx + 1) / len(st.session_state.questions))
    
    # データの取得（空白を空文字に変換）
    target = str(row[0]).strip()
    all_answers_raw = str(row[1]).strip()
    dummy_pool_raw = str(row[2]).strip()
    
    # 例文と訳の取得処理（pd.isnaを使って確実に空判定）
    sentence = str(row[3]).strip() if pd.notna(row[3]) else ""
    translation = str(row[4]).strip() if pd.notna(row[4]) else ""

    correct_list = [a.strip() for a in all_answers_raw.split(',')]
    dummy_list = [d.strip() for d in dummy_pool_raw.split(',')]

    if st.session_state.new_ques:
        display_correct = random.choice(correct_list)
        # ダミーを最大3つ抽出
        display_dummies = random.sample(dummy_list, min(len(dummy_list), 3))
        choices = [display_correct] + display_dummies
        random.shuffle(choices)
        st.session_state.shuffled_choices = choices
        st.session_state.new_ques = False
        st.session_state.answered = False

    st.write(f"### 第 {st.session_state.idx + 1} 問")
    
    # 例文の表示判定
    highlighted_html = f'<span class="highlight-green">{target}</span>'
    
    # sentenceが空、または "nan" という文字列でない場合
    if sentence and sentence.lower() != "nan":
        if target in sentence:
            display_text = sentence.replace(target, highlighted_html)
        else:
            # ターゲットが見つからない場合も例文を表示
            display_text = f"{sentence}<br><small>(語句: {highlighted_html})</small>"
    else:
        display_text = f"（単語） {highlighted_html}"

    st.markdown(f"""
        <div class="sentence-box">
            <p style="font-size:22px; color:#333; font-family: 'serif';">{display_text}</p>
        </div>
    """, unsafe_allow_html=True)

    # 選択肢ボタン
    for choice in st.session_state.shuffled_choices:
        if st.button(choice, use_container_width=True, disabled=st.session_state.answered):
            st.session_state.answered = True
            st.session_state.last_result = "correct" if choice in correct_list else "incorrect"
            if st.session_state.last_result == "correct":
                st.session_state.score += 1
            st.rerun()

    # 回答後の処理
    if st.session_state.answered:
        if st.session_state.last_result == "correct":
            st.success("✨ 正解！")
        else:
            st.error("❌ 不正解...")
        
        st.info(f"**「{target}」の主な意味:**\n{', '.join(correct_list)}")

        if translation and translation.lower() != "nan":
            with st.expander("📖 現代語訳を見る", expanded=True):
                st.write(translation)

        if st.button("次の問題へ 👉", type="primary"):
            st.session_state.idx += 1
            st.session_state.new_ques = True
            st.session_state.answered = False
            st.rerun()
else:
    st.balloons()
    st.write("## 🎉 350語全問終了！")
    accuracy = (st.session_state.score / len(st.session_state.questions)) * 100
    st.metric("最終正答率", f"{accuracy:.1f}%")
    
    if st.button("もう一度最初から（シャッフル）"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
