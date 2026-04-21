import streamlit as st
import pandas as pd
import random
import re

# --- 1. データの読み込み ---
@st.cache_data
def load_data():
    try:
        # 古文用のCSV（レベルなし版）を読み込む
        df = pd.read_csv('kobun_v2.csv', on_bad_lines='skip', engine='python', encoding='utf-8-sig')
        return df
    except FileNotFoundError:
        return None

df = load_data()

# --- 2. 画面設定 ---
st.set_page_config(page_title="ほぼ🐰網羅の古文単語", layout="centered")

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
    </style>
    """, unsafe_allow_html=True)

st.title("🌿 なんとかしよう古文単語")

if df is None:
    st.error("⚠️ 'kobun_v2.csv' が見つかりません。")
    st.stop()

# --- 3. セッション状態の初期化 ---
if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.score = 0
    # 最初から全単語をシャッフル
    st.session_state.questions = df.sample(frac=1).reset_index(drop=True)
    st.session_state.new_ques = True
    st.session_state.answered = False

# サイドバーに進捗を表示
st.sidebar.header("📊 学習状況")
st.sidebar.write(f"**総単語数:** {len(st.session_state.questions)}語")
if st.session_state.idx > 0:
    accuracy = (st.session_state.score / st.session_state.idx) * 100
    st.sidebar.metric("正答率", f"{accuracy:.1f}%")

# --- 4. クイズ本編 ---
if st.session_state.idx < len(st.session_state.questions):
    row = st.session_state.questions.iloc[st.session_state.idx]
    st.progress((st.session_state.idx + 1) / len(st.session_state.questions))
    
    correct_list = [a.strip() for a in str(row['all_answers']).split(',')]
    dummy_list = [d.strip() for d in str(row['dummy_pool']).split(',')]

    if st.session_state.new_ques:
        display_correct = random.choice(correct_list)
        display_dummies = random.sample(dummy_list, min(len(dummy_list), 3))
        choices = [display_correct] + display_dummies
        random.shuffle(choices)
        st.session_state.shuffled_choices = choices
        st.session_state.new_ques = False
        st.session_state.answered = False

    st.write(f"### 第 {st.session_state.idx + 1} 問： 下の傍線部の意味は？")
    
    sentence = str(row['sentence']) if pd.notna(row.get('sentence')) else ""
    target = str(row['question'])
    
    highlighted_html = f'<span class="highlight-green">{target}</span>'
    highlighted_sentence = sentence.replace(target, highlighted_html) if target in sentence else f"（例文なし） {highlighted_html}"

    st.markdown(f"""
        <div style="background-color:#f0f4f0; padding:25px; border-radius:10px; border-left:10px solid #2e7d32; margin-bottom:20px;">
            <p style="font-size:24px; color:#333; font-family: 'Sawarabi Mincho', serif;">{highlighted_sentence}</p>
        </div>
    """, unsafe_allow_html=True)

    for choice in st.session_state.shuffled_choices:
        if st.button(choice, use_container_width=True, disabled=st.session_state.answered):
            st.session_state.answered = True
            if choice in correct_list:
                st.session_state.last_result = "correct"
                st.session_state.score += 1
            else:
                st.session_state.last_result = "incorrect"
            st.rerun()

    if st.session_state.answered:
        if st.session_state.last_result == "correct":
            st.success(f"✨ **正解！**")
        else:
            st.error(f"❌ **不正解...**")
        
        st.write(f"**【「{target}」の主な意味】**")
        st.info(", ".join(correct_list))

        with st.expander("📖 現代語訳・出典を見る", expanded=True):
            st.write(f"**現代語訳:**\n{row['translation']}")
            if pd.notna(row.get('exam_info')):
                st.write(f"**出典:** {row['exam_info']}")

        if st.button("次の問題へ 👉", type="primary"):
            st.session_state.idx += 1
            st.session_state.new_ques = True
            st.session_state.answered = False
            st.rerun()
else:
    st.balloons()
    st.write("## 🎉 全問終了！")
    if st.button("もう一度最初から解く"):
        del st.session_state.idx # 状態をリセット
        st.rerun()
