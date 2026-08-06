import streamlit as st
from gtts import gTTS
import os
import tempfile

# 1. 网页基本设置
st.set_page_config(page_title="私人配音跟读教练", page_icon="🎙️", layout="centered")

st.title("🎙️ 私人配音跟读教练 - 第一步：文本切分与谷歌原声")
st.write("把你的英文小故事贴在下面，系统会帮你自动切成单句卡片，点击即可听谷歌纯正发音！")

# 2. 文本输入框
default_text = "Today is a great day. I woke up early in the morning, and the air was fresh. I really enjoy this quiet moment."
story_text = st.text_area("把英文小故事贴在这里：", value=default_text, height=150)

# 3. 简单的切句逻辑（按句号、问号、感叹号切分）
def split_sentences(text):
    import re
    # 用正则按 . ! ? 切分，并过滤掉空行
    raw_sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in raw_sentences if s.strip()]

if st.button("🚀 开始切分句子", type="primary"):
    if story_text:
        sentences = split_sentences(story_text)
        st.session_state['sentences'] = sentences
        st.success(f"成功切分出 {len(sentences)} 个句子！")
    else:
        st.warning("请先输入一些英文内容哦！")

# 4. 展示单句卡片并提供谷歌语音朗读
if 'sentences' in st.session_state:
    st.markdown("---")
    st.subheader("📖 句子练习卡片")
    
    for i, sentence in enumerate(st.session_state['sentences']):
        # 用卡片容器把每一句包起来
        with st.container():
            st.markdown(f"**第 {i+1} 句**: {sentence}")
            
	# 替换原来生成谷歌语音的那几行
            if st.button(f"🔊 听谷歌原声 #{i+1}", key=f"btn_{i}"):
                try:
                    # 尝试生成谷歌语音
                    tts = gTTS(text=sentence, lang='en', slow=False)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                        temp_filename = fp.name
                        tts.save(temp_filename)
                    
                    # 播放音频
                    st.audio(temp_filename, format="audio/mp3", autoplay=True)
                    
                except Exception as e:
                    # 如果网络卡顿报错，网页会友好地提示，而不是直接崩溃
                    st.error(f"网络开小差啦，刚才这句生成失败，再点一次试试吧！(错误信息: {e})")
            
            st.markdown("---")