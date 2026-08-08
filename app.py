import streamlit as st
import tempfile
from google import genai
from streamlit_mic_recorder import mic_recorder

# 初始化客户端（会自动读取 st.secrets["GEMINI_API_KEY"]）
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


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

# 5. 展示单句卡片（包含原声与录音回放）
if 'sentences' in st.session_state:
    st.markdown("---")
    st.subheader("📖 句子练习卡片")

    for i, sentence in enumerate(st.session_state['sentences']):
        with st.container():
            st.markdown(f"**第 {i + 1} 句**")

            # 大字版句子显示
            st.markdown(
                f"<p style='font-size: 22px; font-weight: bold; color: #1f77b4;'>{sentence}</p>",
                unsafe_allow_html=True
            )

            # 听原声按钮
            if st.button(f"🔊 听原声 #{i + 1}", key=f"btn_play_{i}"):
                try:
                    tts = gTTS(text=sentence, lang='en', slow=is_slow)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                        temp_filename = fp.name
                        tts.save(temp_filename)
                    st.audio(temp_filename, format="audio/mp3", autoplay=True)
                except Exception as e:
                    st.error(f"网络开小差啦，再点一次试试吧！(错误信息: {e})")

            # 麦克风录音与回放组件
            st.markdown("**你的跟读：**")
            audio_data = mic_recorder(
                start_prompt="🔴 开始录音",
                stop_prompt="⏹️ 停止录音",
                key=f"rec_{i}"
            )

            # 如果录到了声音，自动回放
            if audio_data:
                st.audio(audio_data['bytes'], format="audio/wav")

                if st.button("✨ 让 AI 外教听听我的发音", key=f"ai_diag_{i}"):
                    with st.spinner("AI 正在认真听你的发音细节..."):
                        try:
                            # 1. 保存为临时音频文件
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                                f.write(audio_data['bytes'])
                                temp_audio_path = f.name

                            # 2. 上传文件到 Gemini
                            audio_file = client.files.upload(file=temp_audio_path)

                            # 3. 调用 gemini-2.5-flash 模型生成点评
                            prompt = f"""
                            你是一位亲切鼓励的英语口语私教。
                            这是标准原句："{sentence}"
                            这是学生读出来的音频文件。
                            请直接听这段音频，并简短给出建议：
                            1. 单词准确度（是否有读错）。
                            2. 语调与流利度。
                            3. 一句鼓励的话。
                            """

                            response = client.models.generate_content(
                                model='gemini-3.6-flash',  # 替换为最新的可用模型
                                contents=[prompt, audio_file]
                            )

                            # 4. 显示评价
                            st.info(f"**AI 外教点评**:\n\n {response.text}")

                        except Exception as e:
                            st.error(f"AI 诊断出错了，请再试一次。(错误信息: {e})")

            st.markdown("---")