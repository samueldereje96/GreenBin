# models/vehicle.py
class Vehicle:
    def __init__(self, vid, x, y, capacity=100):
        self.id = vid           # vehicle ID
        self.x = x              # current X coordinate
        self.y = y              # current Y coordinate
        self.capacity = capacity
        self.load = 0           # current load
        self.current_node = (x, y)  # tuple of current position
        self.available = True
        self.target_bin = None  # bin currently assigned
        self.target_facility = None # facility currently assigned
        self.current_route = [] # path to the bin
        self.total_distance = 0 # total distance traveled

    def assign_route(self, path, target_bin):
        self.current_route = path
        self.target_bin = target_bin
        self.available = False

    def finish_route(self):
        self.current_route = []
        self.target_bin = None
        self.available = True

    def to_dict(self):
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "capacity": self.capacity,
            "load": self.load,
            "current_node": self.current_node,
            "available": self.available,
            "target_bin": self.target_bin.to_dict() if self.target_bin else None,
            "target_facility": self.target_facility.to_dict() if self.target_facility else None, # Assuming Facility has to_dict
            "current_route": self.current_route,
            "dist_to_bin": getattr(self, "dist_to_bin", 0),
            "dist_to_facility": getattr(self, "dist_to_facility", 0),
            "dist_return": getattr(self, "dist_return", 0),
            "total_distance": getattr(self, "total_distance", 0)
        }

    @classmethod
    def from_dict(cls, data):
        v = cls(data["id"], data["x"], data["y"], data.get("capacity", 100))
        v.load = data.get("load", 0)
        v.current_node = tuple(data.get("current_node", (data["x"], data["y"])))
        v.available = data.get("available", True)
        
        if data.get("target_bin"):
            from models.bin import Bin
            v.target_bin = Bin.from_dict(data["target_bin"])
        
        # We skip facility reconstruction for now as it's not critical for basic state
        # or we can add it if needed.
            
        v.current_route = data.get("current_route", [])
        v.dist_to_bin = data.get("dist_to_bin", 0)
        v.dist_to_facility = data.get("dist_to_facility", 0)
        v.dist_return = data.get("dist_return", 0)
        v.total_distance = data.get("total_distance", 0)
        return v
