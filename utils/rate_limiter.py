import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, limit: int, per: int):
        self.limit = limit  # Максимальна кількість запитів
        self.per = per  # За певний проміжок часу (у секундах)
        self.requests = defaultdict(list)

    def is_allowed(self, user_id: int) -> bool:
        now = time.time()
        self.requests[user_id] = [t for t in self.requests[user_id] if t > now - self.per]

        if len(self.requests[user_id]) < self.limit:
            self.requests[user_id].append(now)
            return True
        return False

    def get_retry_after(self, user_id: int) -> int:
        if user_id not in self.requests or not self.requests[user_id]:
            return 0
        return int(self.per - (time.time() - self.requests[user_id][0]))
