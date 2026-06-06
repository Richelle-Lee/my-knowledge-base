import streamlit as st
import os
import glob
import re

st.set_page_config(page_title="我的知识库", layout="wide")
st.title("📚 我的个人知识库")

def parse_note(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    title = os.path.basename(path).replace(".md", "")
    tags = []
    body = content
    # 解析 YAML front matter 里的 tags
    match = re.search(r"tags:\s*\[(.+?)\]", content)
    if match:
        tags = [t.strip() for t in match.group(1).split(",")]
    # 去掉 front matter 展示正文
    body = re.sub(r"^---[\s\S]+?---\n", "", content).strip()
    return {"title": title, "tags": tags, "body": body, "raw": content}

notes_data = [parse_note(p) for p in glob.glob("data/notes/*.md")]

# 侧边栏：标签筛选
all_tags = sorted({t for n in notes_data for t in n["tags"]})
st.sidebar.header("标签筛选")
selected_tags = st.sidebar.multiselect("选择标签", all_tags)

# 主区域：关键词搜索
query = st.text_input("🔍 搜索笔记", placeholder="输入关键词...")

# 过滤逻辑
filtered = notes_data
if selected_tags:
    filtered = [n for n in filtered if any(t in n["tags"] for t in selected_tags)]
if query:
    filtered = [n for n in filtered if query.lower() in n["raw"].lower()]

st.caption(f"共找到 {len(filtered)} 篇笔记")

for note in filtered:
    with st.expander(note["title"]):
        if note["tags"]:
            st.caption("标签：" + " · ".join(note["tags"]))
        st.markdown(note["body"])
