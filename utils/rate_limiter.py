from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, limit: int, interval_seconds: int):
        self.limit = limit
        self.interval = interval_seconds
        self.requests = defaultdict(list)

    async def is_allowed(self, user_id: int) -> bool:
        now = datetime.now()
        user_requests = self.requests[user_id]
        user_requests = [t for t in user_requests if now - t < timedelta(seconds=self.interval)]
        self.requests[user_id] = user_requests
        if len(user_requests) >= self.limit:
            return False
        user_requests.append(now)
        self.requests[user_id] = user_requests
        return True
