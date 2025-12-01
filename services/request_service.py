# services/request_service.py
import os
import json
from models.request import Request
from data_structures.queue import Queue  # your custom queue
from services.history_service import HistoryService

class RequestService:
    def __init__(self, file_path="data/requests.json"):
        self.file_path = file_path
        self.queue = Queue()  # custom queue
        self.history = HistoryService()  # stack-based history per category
        self.load_requests()

    def load_requests(self):
        """Load requests from JSON file into the queue"""
        if not os.path.exists(self.file_path):
            return
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                for item in data:
                    req = Request.from_dict(item)
                    self.queue.enqueue(req)
        except json.JSONDecodeError:
            pass  # empty or corrupted file

    def save_requests(self):
        """Save all requests to JSON"""
        data = [req.to_dict() for req in self.queue.items]  # assuming Queue has .items
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

    def _get_next_id(self):
        """Generate next request ID"""
        if not self.queue.items:
            return 1
        max_id = max((r.id for r in self.queue.items if r.id is not None), default=0)
        return max_id + 1

    def add_request(self, user, bin_id, request_type):
        """Add a new request"""
        new_id = self._get_next_id()
        req = Request(user=user, bin_id=bin_id, request_type=request_type, id=new_id, status="pending")
        self.queue.enqueue(req)
        self.save_requests()
        # Push undo info with category
        self.history.push_action("request", "add_request", req.to_dict())
        return req

    def process_request(self, request_id):
        """Process a request - removes it from queue and logs to history"""
        from services.bin_service import BinService  # Local import to avoid circular dependency
        bin_service = BinService()

        for req in self.queue.items:
            if req.id == request_id:
                # Store request data before removing
                req.status = "processed"
                request_data = req.to_dict()
                
                # Enrich with bin details
                bin_obj = bin_service.get_bin_by_id(req.bin_id)
                if bin_obj:
                    request_data["bin_location"] = bin_obj.location
                    request_data["bin_type"] = bin_obj.bin_type
                    request_data["bin_x"] = bin_obj.x
                    request_data["bin_y"] = bin_obj.y
                
                # Remove from queue
                self.queue.items = [r for r in self.queue.items if r.id != request_id]
                self.save_requests()
                
                # Log to history
                self.history.push_action("request", "process_request", request_data)
                return True
        return False

    def cancel_request(self, request_id):
        """Cancel a request - removes it from queue and logs to history"""
        for req in self.queue.items:
            if req.id == request_id:
                # Store request data before removing
                req.status = "cancelled"
                request_data = req.to_dict()
                
                # Remove from queue
                self.queue.items = [r for r in self.queue.items if r.id != request_id]
                self.save_requests()
                
                # Log to history
                self.history.push_action("request", "cancel_request", request_data)
                return True
        return False

    def undo_last(self):
        """Undo last request action"""
        last_action = self.history.pop_action("request")
        if not last_action:
            return False

        action_type = last_action["type"]
        data = last_action["data"]

        if action_type == "add_request":
            # Remove the request from the queue
            request_id = data["id"]
            self.queue.items = [r for r in self.queue.items if r.id != request_id]
            self.save_requests()
            return True

        elif action_type == "process_request":
            # Restore request back to queue with pending status
            data["status"] = "pending"
            req = Request.from_dict(data)
            self.queue.enqueue(req)
            self.save_requests()
            return True

        elif action_type == "cancel_request":
            # Restore request back to queue with pending status
            data["status"] = "pending"
            req = Request.from_dict(data)
            self.queue.enqueue(req)
            self.save_requests()
            return True

        return False

    def get_all_requests(self):
        """Return list of all requests"""
        return list(self.queue.items)

    def get_request_by_id(self, request_id):
        """Get a specific request by ID"""
        for req in self.queue.items:
            if req.id == request_id:
                return req
        return None

    def get_requests_by_status(self, status):
        """Get all requests with a specific status"""
        return [req for req in self.queue.items if req.status == status]

