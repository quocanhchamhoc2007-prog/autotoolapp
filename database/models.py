from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    hashtag = Column(String(255), nullable=True)
    cta = Column(Text, nullable=True)
    platform = Column(String(50), nullable=True)
    platform_target = Column(String(50), nullable=True)
    
    # --- CÁC TRƯỜNG TỰ ĐỘNG HÓA & AI ---
    target_word_count = Column(Integer, default=800)
    actual_word_count = Column(Integer, default=0)
    auto_publish_enabled = Column(Boolean, default=False)
    publish_status = Column(String(50), default="AI_GENERATED")
    status = Column(String(50), default="AI_GENERATED") # <--- Bổ sung thêm cột status để khớp với giao diện

    # Thông tin hình ảnh minh họa
    image_url = Column(Text, nullable=True)
    image_source_url = Column(Text, nullable=True)
    image_provider = Column(String(50), nullable=True)
    image_license = Column(String(100), nullable=True)
    image_attribution = Column(Text, nullable=True)
    image_alt_text = Column(Text, nullable=True)
    image_analysis = Column(Text, nullable=True)
    image_relevance_score = Column(Float, default=0.0)

    # Thông tin xuất bản mạng xã hội
    external_post_id = Column(String(100), nullable=True)
    published_url = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

PostModel = Post