import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base

DB_PATH = "posts.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Nếu file database cũ gây lỗi thiếu cột, tự động xóa nó đi để làm mới
if os.path.exists(DB_PATH):
    try:
        os.remove(DB_PATH)
        print("Đã tự động dọn dẹp cơ sở dữ liệu cũ.")
    except Exception as e:
        print(f"Không thể xóa file database cũ: {e}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Tạo mới hoàn toàn cơ sở dữ liệu và các bảng"""
    Base.metadata.create_all(bind=engine)
    print("Đã khởi tạo cơ sở dữ liệu mới thành công!")

# Tự động chạy khi khởi động