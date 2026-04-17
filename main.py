import streamlit as st
import pandas as pd
import random

# 新しい形式のCSVを読み込む
df = pd.read_csv('kobun_v2.csv') 

st.title("なんとかしよう古文単語")

if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.questions = df.sample(frac=1).reset_index(drop=True)
    st.session_state.new_ques = True

if st.session_state.idx < len(st.session_state.questions):
    row = st.session_state.questions.iloc[st.session_state.idx]
    
    # 文字列をリストに変換
    correct_list = [a.strip() for a in str(row['all_answers']).split(',')]
    dummy_list = [d.strip() for d in str(row['dummy_pool']).split(',')]

    if st.session_state.new_ques:
        # 正解候補からランダムに1つ、ダミーから3つ選んでシャッフル
        display_correct = random.choice(correct_list)
        display_dummies = random.sample(dummy_list, 3)
        
        st.session_state.shuffled_choices = [display_correct] + display_dummies
        random.shuffle(st.session_state.shuffled_choices)
        st.session_state.new_ques = False
        st.session_state.answered = False

    st.subheader(f"第 {st.session_state.idx + 1} 問: **{row['question']}**")

    for choice in st.session_state.shuffled_choices:
        if st.button(choice, use_container_width=True, disabled=st.session_state.answered):
            st.session_state.answered = True
            # ここが重要：選んだ選択肢が正解リストのどれかに一致するか判定
            if choice in correct_list:
                st.success(f"✨ 正解！「{row['question']}」の意味：{', '.join(correct_list)}")
                st.session_state.score += 1
            else:
                st.error(f"❌ 不正解。正解は：{', '.join(correct_list)}")

    if st.session_state.answered:
        if st.button("次の単語へ"):
            st.session_state.idx += 1
            st.session_state.new_ques = True
            st.rerun()
