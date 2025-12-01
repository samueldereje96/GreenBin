# services/history_service.py
import json
import os
from data_structures.stack import Stack  # your custom stack implementation

class HistoryService:
    def __init__(self, file_path="data/history.json"):
        self.file_path = file_path
        # Initialize stacks for each category
        self.history = {
            "request": Stack(),
            "bin": Stack(),
            "dispatch": Stack()
        }
        self.load_history()

    def push_action(self, category, action_type, data):
        """Push an action to the stack of a specific category"""
        if category not in self.history:
            self.history[category] = Stack()
        self.history[category].push({
            "type": action_type,
            "data": data
        })
        self.save_history()

    def pop_action(self, category):
        """Pop last action from a specific category"""
        if category in self.history and not self.history[category].is_empty():
            action = self.history[category].pop()
            self.save_history()
            return action
        return None

    def peek_last(self, category):
        """Peek last action from a specific category"""
        if category in self.history and not self.history[category].is_empty():
            return self.history[category].peek()
        return None

    def save_history(self):
        """Persist history to JSON"""
        # Convert each stack to a list for JSON serialization
        serializable_history = {category: stack.to_list() for category, stack in self.history.items()}
        with open(self.file_path, "w") as f:
            json.dump(serializable_history, f, indent=4)

    def load_history(self):
        """Load history from JSON"""
        if not os.path.exists(self.file_path):
            return
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                # Convert lists back into stack objects
                for category, actions in data.items():
                    stack = Stack()  # your stack implementation
                    for action in actions:
                        stack.push(action)
                    self.history[category] = stack
        except json.JSONDecodeError:
            self.history = { "request": Stack(), "bin": Stack(), "dispatch": Stack() }

    def get_stack(self, category):
        """Return the stack for a category"""
        return self.history.get(category)