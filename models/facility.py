# models/facility.py

class Facility:
    def __init__(self,id,name,location,type,capacity,efficiency,x=None,y=None,operational_status="active",processing_cost=0.0):
        self.id = id
        self.name = name
        self.location = location
        self.type = type
        self.capacity = capacity
        self.efficiency = efficiency
        self.x = x
        self.y = y
        self.operational_status = operational_status
        self.processing_cost = processing_cost

    def __str__(self):
        return (
            f"{self.name} ({self.type}) - {self.location} "
            f"[Eff: {self.efficiency}] Cap: {self.capacity}"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "type": self.type,
            "capacity": self.capacity,
            "efficiency": self.efficiency,
            "x": self.x,
            "y": self.y,
            "operational_status": self.operational_status,
            "processing_cost": self.processing_cost,
        }

    @staticmethod
    def from_dict(d: dict):
        return Facility(
            id=d.get("id"),
            name=d.get("name"),
            location=d.get("location"),
            type=d.get("type"),
            capacity=d.get("capacity"),
            efficiency=d.get("efficiency"),
            x=d.get("x"),
            y=d.get("y"),
            operational_status=d.get("operational_status", "operational"),
            processing_cost=d.get("processing_cost", 0.0),
        )
