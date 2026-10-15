from sqlalchemy.orm import Session
from database.models import PostModel

class PostRepository:
    @staticmethod
    def create(db: Session, data: dict):
        post = PostModel(**data)
        db.add(post)
        db.commit()
        db.refresh(post)
        return post

    @staticmethod
    def get_all(db: Session):
        return db.query(PostModel).all()
