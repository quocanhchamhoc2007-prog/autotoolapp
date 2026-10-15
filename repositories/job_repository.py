from sqlalchemy.orm import Session
from database.models import ScheduledJobModel

class JobRepository:
    @staticmethod
    def create(db: Session, data: dict) -> ScheduledJobModel:
        job = ScheduledJobModel(**data)
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def get_pending_jobs(db: Session):
        return db.query(ScheduledJobModel).filter(ScheduledJobModel.status == "PENDING").all()

    @staticmethod
    def update_status(db: Session, job_id: int, status: str, error: str = None):
        job = db.query(ScheduledJobModel).filter(ScheduledJobModel.id == job_id).first()
        if job:
            job.status = status
            if error:
                job.error_message = error
            db.commit()
        return job