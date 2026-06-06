import streamlit as st
import os
import glob
import re
import base64

st.set_page_config(page_title="我的知识库", layout="wide", page_icon="📚")

def parse_note(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    title = os.path.basename(path).replace(".md", "")
    tags, date = [], ""
    match_tags = re.search(r"tags:\s*\[(.+?)\]", content)
    match_date = re.search(r"date:\s*(.+)", content)
    if match_tags:
        tags = [t.strip() for t in match_tags.group(1).split(",")]
    if match_date:
        date = match_date.group(1).strip()
    body = re.sub(r"^---[\s\S]+?---\n", "", content).strip()
    return {"title": title, "tags": tags, "date": date, "body": body, "raw": content}

def show_pdf(path):
    with open(path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f"""
        <iframe
            src="data:application/pdf;base64,{base64_pdf}"
            width="100%" height="700px"
            style="border: none; border-radius: 8px;">
        </iframe>
    """
    st.components.v1.html(pdf_display, height=720)

notes_data = sorted(
    [parse_note(p) for p in glob.glob("data/notes/*.md")],
    key=lambda x: x["date"],
    reverse=True
)

pdf_files = sorted(glob.glob("data/reports/*.pdf"), reverse=True)

# 侧边栏
st.sidebar.title("📚 我的知识库")
page = st.sidebar.radio("导航", ["🔍 全部笔记", "🏆 成果展示", "📄 报告中心"])

all_tags = sorted({t for n in notes_data for t in n["tags"]})
st.sidebar.divider()
st.sidebar.subheader("标签筛选")
selected_tags = st.sidebar.multiselect("选择标签", all_tags)

# 全部笔记页
if page == "🔍 全部笔记":
    st.title("🔍 全部笔记")
    query = st.text_input("搜索笔记", placeholder="输入关键词...")

    filtered = notes_data
    if selected_tags:
        filtered = [n for n in filtered if any(t in n["tags"] for t in selected_tags)]
    if query:
        filtered = [n for n in filtered if query.lower() in n["raw"].lower()]

    st.caption(f"共 {len(filtered)} 篇笔记")
    for note in filtered:
        with st.expander(f"{note['title']}　{note['date']}"):
            if note["tags"]:
                st.caption("标签：" + " · ".join(note["tags"]))
            st.markdown(note["body"])

# 成果展示页
elif page == "🏆 成果展示":
    st.title("🏆 成果展示")
    achievements = [n for n in notes_data if "成果" in n["tags"]]
    if not achievements:
        st.info("还没有成果笔记，给笔记加上 tags: [成果] 就会出现在这里。")
    for note in achievements:
        st.subheader(note["title"])
        if note["date"]:
            st.caption(note["date"])
        st.markdown(note["body"])
        st.divider()

# 报告中心页
elif page == "📄 报告中心":
    st.title("📄 报告中心")

    if not pdf_files:
        st.info("还没有 PDF 报告，请上传至 data/reports/ 文件夹。")
    else:
        # 左侧选择报告，右侧展示
        col1, col2 = st.columns([1, 3])

        with col1:
            st.subheader("报告列表")
            file_names = [os.path.basename(p) for p in pdf_files]
            selected = st.radio("选择报告", file_names, label_visibility="collapsed")

        with col2:
            selected_path = f"data/reports/{selected}"
            st.subheader(selected.replace(".pdf", "").replace("_", " "))

            # 下载按钮
            with open(selected_path, "rb") as f:
                st.download_button(
                    label="下载 PDF",
                    data=f,
                    file_name=selected,
                    mime="application/pdf"
                )

            # 内嵌预览
            show_pdf(selected_path)
