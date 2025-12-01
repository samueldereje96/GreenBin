import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
import json
from models.facility import Facility
from data_structures.avl_trees import FacilityAVLTree


class FacilityService:
    def __init__(self, file_path="data/facilities.json"):
        self.file_path = file_path
        
        # AVL tree sorted by ID initially
        self.tree = FacilityAVLTree(key=lambda f: f.id)

        self.load_facilities()

    # -------------------- LOAD --------------------

    def load_facilities(self):
        """Load all facilities from JSON into AVL tree."""
        if not os.path.exists(self.file_path):
            return  # No file yet

        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                for item in data:
                    fac = Facility(
                        id=item["id"],
                        name=item["name"],
                        location=item["location"],
                        x=item["x"],
                        y=item["y"],
                        type=item["type"],
                        capacity=item["capacity"],
                        efficiency=item["efficiency"],
                    )
                    self.tree.insert(fac)
        except json.JSONDecodeError:
            pass  # File exists but is empty or corrupted

    # -------------------- SAVE --------------------

    def save_facilities(self):
        """Save AVL tree contents back to JSON."""
        facilities = self.tree.inorder()  # sorted list

        data = [
            {
                "id": f.id,
                "name": f.name,
                "location": f.location,
                "x": f.x,
                "y": f.y,
                "type": f.type,
                "capacity": f.capacity,
                "efficiency": f.efficiency,
            }
            for f in facilities
        ]

        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

    # -------------------- CRUD --------------------

    def add_facility(self, name, location, x, y, type, capacity, efficiency):
        """Create a new facility with auto-increment ID."""
        # ID = max ID + 1
        facilities = self.tree.inorder()
        new_id = facilities[-1].id + 1 if facilities else 1

        fac = Facility(new_id, name, location, x, y, type, capacity, efficiency)
        self.tree.insert(fac)
        self.save_facilities()
        return fac

    def update_facility(self, fac_id, **updates):
        """Update any field in the facility."""
        facility = self.tree.search(fac_id)
        if not facility:
            return False

        # Update only provided fields
        for key, value in updates.items():
            if hasattr(facility, key):
                setattr(facility, key, value)

        # Rebuild tree only if sorting key changed
        self.save_facilities()
        return True

    # ------- DELETE (requires AVL delete later) -------
    # For now we'll implement a simple workaround:
    # Remove by rebuilding the tree without the facility.

    def remove_facility(self, fac_id):
        """Delete a facility by ID (temporary implementation)."""
        facilities = self.tree.inorder()
        new_list = [f for f in facilities if f.id != fac_id]

        if len(new_list) == len(facilities):
            return False  # Not found

        # Rebuild AVL tree
        self.tree = FacilityAVLTree(key=self.tree.key)
        for fac in new_list:
            self.tree.insert(fac)

        self.save_facilities()
        return True

    # -------------------- SEARCH --------------------

    def get_by_id(self, fac_id):
        return self.tree.search(fac_id)

    def get_all(self):
        return self.tree.inorder()

    # -------------------- SORTING STRATEGY --------------------

    def sort_by(self, attribute):
        """Rebuild AVL tree with a new sorting key."""

        key_func = {
            "id": lambda f: f.id,
            "name": lambda f: f.name.lower(),
            "type": lambda f: f.type,
            "capacity": lambda f: f.capacity,
            "efficiency": lambda f: f.efficiency,
        }.get(attribute)

        if not key_func:
            raise ValueError("Invalid sorting attribute")

        # rebuild AVL tree using new key
        facilities = self.tree.inorder()
        self.tree = FacilityAVLTree(key=key_func)

        for fac in facilities:
            self.tree.insert(fac)
    def remove_facility(self, fac_id):
        found = self.tree.search(fac_id)
        if not found:
            return False

        self.tree.delete(fac_id)
        self.save_facilities()
        return True
    def search_by_name(self, name):
        """Case-insensitive name search."""
        name = name.lower()
        return [f for f in self.tree.inorder() if name in f.name.lower()]
    def search_by_type(self, type_name):
        """Search facilities by type."""
        return [f for f in self.tree.inorder() if f.type == type_name]


    def search_by_efficiency_range(self, min_e, max_e):
        return [f for f in self.tree.inorder() if min_e <= f.efficiency <= max_e]


    def search_by_capacity_range(self, min_c, max_c):
        return [f for f in self.tree.inorder() if min_c <= f.capacity <= max_c]
    # services/facility_service.py

    def get_all_facilities(self):
        """Return a list of all facilities in the AVL tree."""
        facilities = []

        def in_order_traversal(node):
            if node is None:
                return
            in_order_traversal(node.left)
            facilities.append(node.value)  # assuming node.value is Facility object
            in_order_traversal(node.right)

        in_order_traversal(self.tree.root)  # assuming your tree has root
        return facilities


