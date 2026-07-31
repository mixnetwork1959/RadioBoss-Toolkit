# ==========================================
# Broadcast Scheduler
# Version 3.0.0
# scheduler_controller.py
# ==========================================

from schedule_engine import ScheduleEngine
from analyzer import Analyzer


class SchedulerController:

    def __init__(self, events):
        self.events = events
        self.week_offset = 0

        self.engine = ScheduleEngine()

    # --------------------------------------
    # Current Data
    # --------------------------------------

    def get_runtimes(self):

        runtimes = self.engine.generate(
            self.events,
            self.week_offset
        )

        analyzer = Analyzer(runtimes)

        return analyzer.analyze()

    # --------------------------------------
    # Navigation
    # --------------------------------------

    def current_week(self):

        self.week_offset = 0

        return self.get_runtimes()

    def previous_week(self):

        self.week_offset -= 1

        return self.get_runtimes()

    def next_week(self):

        self.week_offset += 1

        return self.get_runtimes()

    def refresh(self):

        return self.get_runtimes()

    # --------------------------------------
    # Information
    # --------------------------------------

    def get_week_offset(self):

        return self.week_offset