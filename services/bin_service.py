import sys
import os
import json
from data_structures.linked_list import LinkedList
from models.bin import Bin
from services.history_service import HistoryService

# make file path robust relative to project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(PROJECT_ROOT, "data", "bins.json")

class BinService:
    def __init__(self, file_path=DATA_FILE):
        self.file_path = file_path
        self.bins = LinkedList()
        self.load_bins()
        self.history = HistoryService()

    def load_bins(self):
        """Read JSON file and populate the LinkedList using Bin.from_dict"""
        if not os.path.exists(self.file_path):
            return

        try:
            with open(self.file_path, "r") as f:
                raw = f.read().strip()
                if not raw:
                    return
                data = json.loads(raw)
                for item in data:
                    # use from_dict or explicit keywords
                    b = Bin.from_dict(item)
                    self.bins.append(b)
        except json.JSONDecodeError:
            # empty or corrupted file — ignore for now
            return

    def save_bins(self):
        """Convert LinkedList back to JSON using each bin.to_dict()"""
        data = [b.to_dict() for b in self.bins]
        # ensure data folder exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

    def add_bin(self, location, fill=0.0, x=0.0, y=0.0, bin_type="household"):
        new_id = len(self.bins) + 1
        b = Bin(
            id=new_id,
            location=location,
            x=x,
            y=y,
            fill_level=fill,
            bin_type=bin_type    
        )
        self.bins.append(b)
        self.save_bins()
        self.history.push_action("bin", "add_bin", b.to_dict())
        return b

    def update_bin(self, bin_id, new_level):
        b = self.bins.find(lambda node: node.id == bin_id)
        if b is not None:
            old_level = b.fill_level
            b.fill_level = new_level
            # optional: clamp to [0,100]
            if b.fill_level < 0:
                b.fill_level = 0
            if b.fill_level > 100:
                b.fill_level = 100
            self.save_bins()
            self.history.push_action("bin", "update_bin", {
                "id": bin_id,
                "old_level": old_level,
                "new_level": b.fill_level
            })
            return True
        return False

    def remove_bin(self, bin_id):
        # Get bin data before removing for history
        bin_to_remove = self.bins.find(lambda node: node.id == bin_id)
        removed = self.bins.remove(lambda node: node.id == bin_id)
        if removed:
            self.save_bins()
            if bin_to_remove:
                self.history.push_action("bin", "remove_bin", bin_to_remove.to_dict())
        return removed
    
    def undo_last(self):
        last_action = self.history.pop_action("bin")
        if not last_action:
            return None

        if last_action["type"] == "add_bin":
            data = last_action["data"]
            bin_id = data["id"]
            # remove the bin that was added
            self.bins.remove(lambda node: node.id == bin_id)
            self.save_bins()
            return f"Undid adding Bin {bin_id}"
        
        elif last_action["type"] == "update_bin":
            data = last_action["data"]
            bin_id = data["id"]
            old_level = data["old_level"]
            # restore the old fill level
            b = self.bins.find(lambda node: node.id == bin_id)
            if b is not None:
                b.fill_level = old_level
                self.save_bins()
                return f"Restored Bin {bin_id} to {old_level}%"
        
        elif last_action["type"] == "remove_bin":
            data = last_action["data"]
            # re-add the bin that was removed
            b = Bin.from_dict(data)
            self.bins.append(b)
            self.save_bins()
            return f"Restored deleted Bin {b.id}"

        return False
    def get_bin_by_id(self, bin_id):
        """Return a bin object by its ID"""
        for b in self.bins:
            if b.id == bin_id:
                return b
        return None

