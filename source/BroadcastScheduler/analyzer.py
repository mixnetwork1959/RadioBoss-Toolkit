# ==========================================
# Broadcast Scheduler
# Version 3.0.0
# analyzer.py
#
# Schedule Analyzer
# ==========================================

from collections import defaultdict


class Analyzer:

    def __init__(self, runtimes):
        self.runtimes = runtimes

    def analyze(self):

        print()
        print("=" * 45)
        print("Schedule Analyzer")
        print("=" * 45)

        self.detect_conflicts()

        print("=" * 45)
        print("Analysis finished")
        print("=" * 45)
        print()

        return self.runtimes

    def detect_conflicts(self):

        print("Checking for conflicts...")

        groups = defaultdict(list)

        for runtime in self.runtimes:
            runtime.conflict = False
            runtime.conflict_count = 0
            groups[runtime.start].append(runtime)

        unique_times = len(groups)

        conflicts = 0
        for start_time in sorted(groups.keys()):

            runtimes = groups[start_time]

            if len(runtimes) > 1:

                for runtime in runtimes:
                    runtime.conflict = True
                    runtime.conflict_count = len(runtimes)

                    conflicts += 1

        print()
        print(f"Conflicts found: {conflicts}")
