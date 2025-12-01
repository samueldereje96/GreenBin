# models/history_action.py
from datetime import datetime

class HistoryAction:
    def __init__(self, action_type, data, timestamp=None):
        self.action_type = action_type
        self.data = data
        self.timestamp = timestamp if timestamp else datetime.now()

    def to_dict(self):
        return {
            "action_type": self.action_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }

    @staticmethod
    def from_dict(d):
        from datetime import datetime
        return HistoryAction(
            action_type=d["action_type"],
            data=d["data"],
            timestamp=datetime.fromisoformat(d["timestamp"])
        )
