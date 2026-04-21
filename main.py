import streamlit as st
import pandas as pd
import random

# --- 1. データの読み込み ---
@st.cache_data
def load_data():
    try:
        # header=None にすることで、1行目から確実に読み込みます
        df = pd.read_csv(
            'kobun350.csv', 
            engine='python', 
            encoding='utf-8-sig',
            header=None
        )
        # もし1行目がヘッダー（question等）だった場合、それを除外する処理
        if "question" in str(df.iloc[0, 0]).lower():
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
    .stMarkdown p { line-height: 1.9; }
    .main { background-color: #fdfaf5; }
    .highlight-green {
        color: #2e7d32; 
        font-weight: bold; 
        border-bottom: 2px solid #2e7d32;
        padding-bottom: 2px;
    }
    .stButton button {
        font-size: 18px !important;
        height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("古文 意地でも覚える350語")

if df is None:
    st.error("⚠️ 'kobun350.csv' が見つかりません。GitHubにアップロードされているか確認してください。")
    st.stop()

# --- 3. セッション状態の初期化 ---
if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.questions = df.sample(frac=1).reset_index(drop=True)
    st.session_state.new_ques = True
    st.session_state.answered = False

# サイドバーに進捗を表示
st.sidebar.header("📊 学習状況")
st.sidebar.write(f"進捗: {st.session_state.idx} / {len(st.session_state.questions)}")
if st.session_state.idx > 0:
    accuracy = (st.session_state.score / st.session_state.idx) * 100
    st.sidebar.metric("正答率", f"{accuracy:.1f}%")

# --- 4. クイズ本編 ---
if st.session_state.idx < len(st.session_state.questions):
    row = st.session_state.questions.iloc[st.session_state.idx]
    st.progress((st.session_state.idx + 1) / len(st.session_state.questions))
    
    # 【重要】列番号でデータを取得
    # 0:単語, 1:正解, 2:ダミー, 3:例文, 4:訳
    target = str(row[0])
    all_answers_raw = str(row[1])
    dummy_pool_raw = str(row[2])
    sentence = str(row[3])
    translation = str(row[4])

    correct_list = [a.strip() for a in all_answers_raw.split(',')]
    dummy_list = [d.strip() for d in dummy_pool_raw.split(',')]

    if st.session_state.new_ques:
        display_correct = random.choice(correct_list)
        display_dummies = random.sample(dummy_list, min(len(dummy_list), 3))
        choices = [display_correct] + display_dummies
        random.shuffle(choices)
        st.session_state.shuffled_choices = choices
        st.session_state.new_ques = False
        st.session_state.answered = False

    st.write(f"### 第 {st.session_state.idx + 1} 問")
    
    # 例文のハイライト
    highlighted_html = f'<span class="highlight-green">{target}</span>'
    if target in sentence and sentence != "nan":
        highlighted_sentence = sentence.replace(target, highlighted_html)
    else:
        highlighted_sentence = f"（単語） {highlighted_html}"

    st.markdown(f"""
        <div style="background-color:#f0f4f0; padding:25px; border-radius:10px; border-left:10px solid #2e7d32; margin-bottom:20px;">
            <p style="font-size:24px; color:#333; font-family: 'serif';">{highlighted_sentence}</p>
        </div>
    """, unsafe_allow_html=True)

    # 選択肢ボタン
    for choice in st.session_state.shuffled_choices:
        if st.button(choice, use_container_width=True, disabled=st.session_state.answered):
            st.session_state.answered = True
            if choice in correct_list:
                st.session_state.last_result = "correct"
                st.session_state.score += 1
            else:
                st.session_state.last_result = "incorrect"
            st.rerun()

    # 回答後の表示
    if st.session_state.answered:
        if st.session_state.last_result == "correct":
            st.success("✨ 正解！")
        else:
            st.error("❌ 不正解...")
        
        st.write(f"**「{target}」の主な意味:**")
        st.info(", ".join(correct_list))

        if translation != "nan":
            with st.expander("📖 現代語訳を見る", expanded=True):
                st.write(translation)

        if st.button("次の問題へ 👉", type="primary"):
            st.session_state.idx += 1
            st.session_state.new_ques = True
            st.session_state.answered = False
            st.rerun()
else:
    st.balloons()
    st.write("## 🎉 350語全問終了！お疲れ様でした！")
    accuracy = (st.session_state.score / len(st.session_state.questions)) * 100
    st.metric("最終正答率", f"{accuracy:.1f}%")
    
    if st.button("もう一度最初から解く"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
