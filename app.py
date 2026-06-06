import streamlit as st
import os
import glob

st.set_page_config(page_title="我的知识库", layout="wide")
st.title("📚 我的个人知识库")

query = st.text_input("🔍 搜索笔记", placeholder="输入关键词...")

notes = glob.glob("data/notes/*.md")

if not notes:
    st.info("暂无笔记，请在 data/notes/ 文件夹添加 Markdown 文件。")
else:
    matched = []
    for path in notes:
        with open(path, encoding="utf-8") as f:
            content = f.read()
        if not query or query.lower() in content.lower():
            title = os.path.basename(path).replace(".md", "")
            matched.append((title, content))

    st.caption(f"共找到 {len(matched)} 篇笔记")

    for title, content in matched:
        with st.expander(title):
            st.markdown(content)
