import streamlit as st
import pandas as pd
import random

# --- 1. データの読み込み ---
@st.cache_data
def load_data():
    try:
        # ファイル名を 'kobun350.csv' に指定
        # encoding='utf-8-sig' はExcelで作ったCSVの文字化けを防ぎます
        df = pd.read_csv('kobun350.csv', on_bad_lines='skip', engine='python', encoding='utf-8-sig')
        return df
    except FileNotFoundError:
        return None

df = load_data()

# --- 2. 画面設定 ---
st.set_page_config(page_title="ほぼ🐰網羅の古文単語350", layout="centered")

# CSSでデザインを調整
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
    st.error("⚠️ 'kobun350.csv' が見つかりません。ファイル名が正しいか、プログラムと同じフォルダにあるか確認してください。")
    st.stop()

# --- 3. セッション状態の初期化 ---
if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.score = 0
    # 全単語をシャッフルしてクイズを生成
    st.session_state.questions = df.sample(frac=1).reset_index(drop=True)
    st.session_state.new_ques = True
    st.session_state.answered = False

# サイドバーに進捗を表示
st.sidebar.header("📊 学習状況")
st.sidebar.write(f"**総単語数:** {len(st.session_state.questions)}語")
if st.session_state.idx > 0:
    accuracy = (st.session_state.score / st.session_state.idx) * 100
    st.sidebar.metric("正答率", f"{accuracy:.1f}%")
    st.sidebar.write(f"進捗: {st.session_state.idx} / {len(st.session_state.questions)}")

# --- 4. クイズ本編 ---
if st.session_state.idx < len(st.session_state.questions):
    row = st.session_state.questions.iloc[st.session_state.idx]
    st.progress((st.session_state.idx + 1) / len(st.session_state.questions))
    
    # CSVの列名（question, all_answers, dummy_pool, sentence, translation）に基づき処理
    correct_list = [a.strip() for a in str(row['all_answers']).split(',')]
    dummy_list = [d.strip() for d in str(row['dummy_pool']).split(',')]

    if st.session_state.new_ques:
        # 正解の選択肢を1つ選ぶ
        display_correct = random.choice(correct_list)
        # ダミーを最大3つ選ぶ
        display_dummies = random.sample(dummy_list, min(len(dummy_list), 3))
        # 選択肢を混ぜる
        choices = [display_correct] + display_dummies
        random.shuffle(choices)
        st.session_state.shuffled_choices = choices
        st.session_state.new_ques = False
        st.session_state.answered = False

    st.write(f"### 第 {st.session_state.idx + 1} 問： 下の傍線部の意味は？")
    
    sentence = str(row['sentence']) if pd.notna(row.get('sentence')) else ""
    target = str(row['question'])
    
    # 例文内のキーワードをハイライト
    highlighted_html = f'<span class="highlight-green">{target}</span>'
    if target in sentence:
        highlighted_sentence = sentence.replace(target, highlighted_html)
    else:
        highlighted_sentence = f"（単語） {highlighted_html}"

    # 問題文の表示
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

    # 回答後の解説表示
    if st.session_state.answered:
        if st.session_state.last_result == "correct":
            st.success(f"✨ **正解！**")
        else:
            st.error(f"❌ **不正解...**")
        
        st.write(f"**【「{target}」の主な意味】**")
        st.info(", ".join(correct_list))

        with st.expander("📖 現代語訳を見る", expanded=True):
            st.write(f"{row['translation']}")

        if st.button("次の問題へ 👉", type="primary"):
            st.session_state.idx += 1
            st.session_state.new_ques = True
            st.session_state.answered = False
            st.rerun()
else:
    # 全問終了時
    st.balloons()
    st.write("## 🎉 350語全問終了！お疲れ様でした！")
    accuracy = (st.session_state.score / len(st.session_state.questions)) * 100
    st.metric("最終正答率", f"{accuracy:.1f}%")
    
    if st.button("もう一度最初から（シャッフルして再開）"):
        # セッションをクリアして再起動
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
