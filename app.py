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

# 5. 展示单句卡片（支持大字显示与带语速的谷歌原声）
if 'sentences' in st.session_state:
    st.markdown("---")
    st.subheader("📖 句子练习卡片")
    
    for i, sentence in enumerate(st.session_state['sentences']):
        with st.container():
            # 序号
            st.markdown(f"**第 {i+1} 句**")
            
            # 核心优化：用 HTML 标签将英文句子字号放大到 22px，并加粗显示
            st.markdown(
                f"<p style='font-size: 22px; font-weight: bold; color: #1f77b4; line-height: 1.5;'>{sentence}</p>", 
                unsafe_allow_html=True
            )
            
            # 生成谷歌语音 (应用刚才选定好的语速 is_slow)
            if st.button(f"🔊 听原声 #{i+1}", key=f"btn_{i}"):
                try:
                    tts = gTTS(text=sentence, lang='en', slow=is_slow)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                        temp_filename = fp.name
                        tts.save(temp_filename)
                    
                    st.audio(temp_filename, format="audio/mp3", autoplay=True)
                    
                except Exception as e:
                    st.error(f"网络开小差啦，再点一次试试吧！(错误信息: {e})")
            
            st.markdown("---")