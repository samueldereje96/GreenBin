# import time

# class Request:
#     def __init__(self, id, user_id, bin_id, request_type, timestamp=None, status="pending"):
#         self.id = id
#         self.user_id = user_id          # Link to a User
#         self.bin_id = bin_id            # Link to a Bin
#         self.request_type = request_type  # e.g. "collect", "overflow", "maintenance"
#         self.status = status
#         self.timestamp = timestamp if timestamp else time.time()

#     def mark_processed(self):
#         self.status = "processed"

#     def mark_cancelled(self):
#         self.status = "cancelled"
#     def __repr__(self):
#             return f"Request({self.request_id}, User={self.user_id}, Bin={self.bin_id}, Type={self.request_type}, Status={self.status})"
# models/request.py
from datetime import datetime

class Request:
    def __init__(self, user, bin_id, request_type, id=None, status="pending", time=None):
        self.id = id
        self.user = user
        self.bin_id = bin_id
        self.request_type = request_type
        self.status = status  # pending, processed, cancelled
        self.time = time if time else datetime.now()

    def to_dict(self):
        return {
            "id": self.id,
            "user": self.user,
            "bin_id": self.bin_id,
            "request_type": self.request_type,
            "status": self.status,
            "time": self.time.isoformat()  # convert datetime to string for JSON
        }

    @staticmethod
    def from_dict(data):
        from datetime import datetime
        return Request(
            id=data.get("id"),
            user=data["user"],
            bin_id=data["bin_id"],
            request_type=data["request_type"],
            status=data.get("status", "pending"),
            time=datetime.fromisoformat(data["time"])
        )
