class Bin:
    def __init__(self, id, location, x, y, fill_level, bin_type="household", capacity=100):
        """
        bin_id: unique identifier
        location: string or coordinates
        bin_type: 'general', 'recycling', 'industrial', etc.
        capacity: maximum capacity
        fill_level: current fill percentage (0-100)
        """
        self.id = id
        self.location = location
        self.fill_level = fill_level
        self.x = x
        self.y = y
        self.bin_type = bin_type
        self.capacity = capacity

    def update_fill(self, amount):
        """Update fill level by amount, keep within 0-100"""
        self.fill_level += amount
        if self.fill_level > self.capacity:
            self.fill_level = self.capacity
        elif self.fill_level < 0:
            self.fill_level = 0

    def to_dict(self):
        """Convert to dict for JSON storage"""
        return {
            "id": self.id,
            "location": self.location,
            "bin_type": self.bin_type,
            "capacity": self.capacity,
            "fill_level": self.fill_level,
            "x": self.x,
            "y": self.y
        }

    @staticmethod
    def from_dict(data):
        """Create Bin from dict"""
        return Bin(
            id=data["id"],
            location=data["location"],
            bin_type=data.get("bin_type", "household"),
            capacity=data.get("capacity", 100),
            fill_level=data.get("fill_level", 0),
            x = data.get("x"),
            y = data.get("y")
        )

    def __lt__(self, other):
        return self.id < other.id
