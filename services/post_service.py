from database.connection import SessionLocal
from repositories.post_repository import PostRepository
from services.content_generator import ContentGenerator

class PostService:
    @staticmethod
    def create_ai_post(data: dict):
        gen = ContentGenerator()
        ai_res = gen.generate_post(data["topic"], data["tone"], data["length"], data["language"], data["keywords"])
        db = SessionLocal()
        post = PostRepository.create(db, {
            "title": ai_res["title"],
            "content": ai_res["content"],
            "hashtag": ai_res["hashtag"],
            "cta": ai_res["cta"],
            "platform_target": data["platform"],
            "status": "PENDING_APPROVAL"
        })
        db.close()
        return {"post_id": post.id, **ai_res}
