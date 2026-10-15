import streamlit as st
from database.connection import SessionLocal
from repositories.post_repository import PostRepository

def render_post_management():
    st.subheader("📚 Kho nội dung")
    db = SessionLocal()
    posts = PostRepository.get_all(db)
    db.close()
    for p in posts:
        st.write(f"**[{p.status}] {p.title}**")
        st.write(p.content)
