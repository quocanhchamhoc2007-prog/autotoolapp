from apscheduler.schedulers.background import BackgroundScheduler
class SchedulerService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()

scheduler_service = SchedulerService()
