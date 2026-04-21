import streamlit as st
import pandas as pd
import random

@st.cache_data
def load_data():
    try:
        # namesを指定することでCSVのヘッダー名に依存しないようにします
        df = pd.read_csv(
            'kobun350.csv', 
            engine='python', 
            encoding='utf-8-sig',
            header=0,
            names=['question', 'all_answers', 'dummy_pool', 'sentence', 'translation']
        )
        return df
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return None

df = load_data()

st.set_page_config(page_title="古文 意地でも覚える350語", layout="centered")

# CSS
st.markdown("""
    <style>
    .stMarkdown p { line-height: 1.9; }
    .highlight-green { color: #2e7d32; font-weight: bold; border-bottom: 2px solid #2e7d32; }
    .stButton button { font-size: 18px !important; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

st.title("古文 意地でも覚える350語")

if df is None:
    st.error("⚠️ 'kobun350.csv' が見つかりません。GitHubにアップロードされているか確認してください。")
    st.stop()

if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.questions = df.sample(frac=1).reset_index(drop=True)
    st.session_state.new_ques = True
    st.session_state.answered = False

# 進捗表示
st.sidebar.write(f"進捗: {st.session_state.idx} / {len(st.session_state.questions)}")

if st.session_state.idx < len(st.session_state.questions):
    row = st.session_state.questions.iloc[st.session_state.idx]
    
    # データの分割処理
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

    st.write(f"### 第 {st.session_state.idx + 1} 問")
    
    target = str(row['question'])
    sentence = str(row['sentence']) if pd.notna(row['sentence']) else ""
    
    highlighted_html = f'<span class="highlight-green">{target}</span>'
    highlighted_sentence = sentence.replace(target, highlighted_html) if target in sentence else f"（単語） {highlighted_html}"

    st.markdown(f"""
        <div style="background-color:#f0f4f0; padding:25px; border-radius:10px; border-left:10px solid #2e7d32; margin-bottom:20px;">
            <p style="font-size:24px; color:#333;">{highlighted_sentence}</p>
        </div>
    """, unsafe_allow_html=True)

    for choice in st.session_state.shuffled_choices:
        if st.button(choice, use_container_width=True, disabled=st.session_state.answered):
            st.session_state.answered = True
            st.session_state.last_result = "correct" if choice in correct_list else "incorrect"
            if st.session_state.last_result == "correct":
                st.session_state.score += 1
            st.rerun()

    if st.session_state.answered:
        if st.session_state.last_result == "correct":
            st.success("✨ 正解！")
        else:
            st.error("❌ 不正解...")
        
        st.info(f"**「{target}」の意味:** {', '.join(correct_list)}")
        with st.expander("📖 現代語訳"):
            st.write(row['translation'])

        if st.button("次の問題へ 👉", type="primary"):
            st.session_state.idx += 1
            st.session_state.new_ques = True
            st.session_state.answered = False
            st.rerun()
else:
    st.balloons()
    st.write("## 🎉 全問終了！")
    if st.button("もう一度最初から"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
