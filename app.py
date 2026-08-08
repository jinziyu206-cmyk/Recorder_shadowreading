import streamlit as st
from gtts import gTTS
import os
import tempfile

# 1. 网页基本设置
st.set_page_config(page_title="私人配音跟读教练", page_icon="🎙️", layout="centered")

st.title("🎙️ 私人配音跟读教练 - 语速调节与大字版")
st.write("把你的英文小故事贴在下面，自由调节语速，沉浸式跟读！")

# 2. 文本输入框
default_text = "Today is a great day. I woke up early in the morning, and the air was fresh. I really enjoy this quiet moment."
story_text = st.text_area("把英文小故事贴在这里：", value=default_text, height=150)

# 3. 新增：语速选择器（放在文本框下方、切分按钮上方）
speed_choice = st.radio(
    "选择朗读速度：", 
    ["正常速", "慢速 (适合逐句跟读)"], 
    horizontal=True
)
# 如果选择了慢速，gTTS 的 slow 参数设为 True（谷歌会自动开启慢速清晰朗读）
is_slow = True if "慢速" in speed_choice else False

# 4. 智能切句逻辑
def split_sentences(text):
    import re
    raw_sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in raw_sentences if s.strip()]

if st.button("🚀 开始切分句子", type="primary"):
    if story_text:
        sentences = split_sentences(story_text)
        st.session_state['sentences'] = sentences
        st.success(f"成功切分出 {len(sentences)} 个句子！")
    else:
        st.warning("请先输入一些英文内容哦！")

# 5. 展示单句卡片（加入录音组件）
if 'sentences' in st.session_state:
    st.markdown("---")
    st.subheader("📖 句子练习卡片")

    for i, sentence in enumerate(st.session_state['sentences']):
        with st.container():
            st.markdown(f"**第 {i + 1} 句**")
            st.markdown(f"<p style='font-size: 22px; font-weight: bold; color: #1f77b4;'>{sentence}</p>",
                        unsafe_allow_html=True)

            # --- 原声按钮保持不变 ---
            if st.button(f"🔊 听原声 #{i + 1}", key=f"btn_play_{i}"):
            # ... (原有的 gTTS 代码) ...

            # --- 新增：录音组件 ---
            st.markdown("**你的跟读：**")
            audio_data = mic_recorder(
                start_prompt="🔴 开始录音",
                stop_prompt="⏹️ 停止录音",
                key=f"rec_{i}"
            )

            # 如果录到了声音，自动回放
            if audio_data:
                st.audio(audio_data['bytes'], format="audio/wav")

            st.markdown("---")