import streamlit as st
from database.connection import SessionLocal
from database.models import PostModel

def render_dashboard():
    st.title("📊 Bảng điều khiển AutoPost AI")
    db = SessionLocal()
    total = db.query(PostModel).count()
    db.close()
    st.metric("Tổng số bài viết", total)
