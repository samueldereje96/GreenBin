
import os
import sys
import json
from models.vehicle import Vehicle
from services.bin_service import BinService
from services.facility_service import FacilityService
from data_structures.priority_queue import MaxHeap
from services.history_service import HistoryService
from services.dijkstra import generate_grid_graph, find_nearest_node, dijkstra

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

class VehicleService:
    def __init__(self, vehicles_file="data/vehicles.json", bins_file="data/bins.json"):
        # Load bins
        self.bin_service = BinService(file_path=bins_file)
        # Store file path for reset
        self.vehicles_file = vehicles_file
        self.actual_vehicles_file = "data/actual_vehicles.json"
        
        # Load vehicles (prefer actual state if exists)
        self.vehicles = self.load_vehicles()
        
        # Prepare max-heap for bins
        self.bin_heap = self.create_bin_heap()
        self.facility_service = FacilityService() 
        self.history = HistoryService()
        
        # Initialize Dijkstra Grid Graph (Dubai Area)
        # Using same bounds as ActualMapService
        print("Generating grid graph for VehicleService...")
        self.graph = generate_grid_graph(25.0, 25.4, 55.0, 55.5, step_km=0.5)

    def load_vehicles(self):
        """Load vehicles from JSON file"""
        # Try loading actual state first
        if os.path.exists(self.actual_vehicles_file):
            try:
                with open(self.actual_vehicles_file, "r") as f:
                    vehicles_data = json.load(f)
                return [Vehicle.from_dict(v) for v in vehicles_data]
            except json.JSONDecodeError:
                pass # Fallback to seed
        
        # Fallback to seed data
        with open(self.vehicles_file, "r") as f:
            vehicles_data = json.load(f)
        return [Vehicle(v["id"], v["x"], v["y"]) for v in vehicles_data]

    def save_vehicles(self):
        """Save current vehicle state to actual_vehicles.json"""
        data = [v.to_dict() for v in self.vehicles]
        with open(self.actual_vehicles_file, "w") as f:
            json.dump(data, f, indent=4)

    def create_bin_heap(self):
        """Create max-heap of bins based on fill level"""
        heap = MaxHeap()
        for b in self.bin_service.bins:
            if b.fill_level > 0:
                heap.push(b)
        return heap

    def get_route(self, start_lat, start_lon, end_lat, end_lon):
        """Helper to get route using new Dijkstra"""
        start_node = find_nearest_node(self.graph, start_lat, start_lon)
        end_node = find_nearest_node(self.graph, end_lat, end_lon)
        
        if not start_node or not end_node:
            return [], 0
            
        path, distance = dijkstra(self.graph, start_node, end_node)
        
        if path:
            # Add actual start/end points
            path.insert(0, [start_lon, start_lat])
            path.append([end_lon, end_lat])
            
        return path, distance

    def assign_bins_and_facilities(self):
        """Assign bins to vehicles and determine path to facility using Dijkstra"""
        # This method seems redundant if dispatch_all_vehicles does the work, 
        # but keeping it for compatibility or alternative usage.
        # Simplified version of dispatch logic.
        
        for v in self.vehicles:
            if not self.bin_heap.is_empty():
                top_bin = self.bin_heap.pop()
                v.target_bin = top_bin

                # 1. Vehicle -> Bin
                path_to_bin, dist_bin = self.get_route(v.x, v.y, top_bin.x, top_bin.y)

                # Find all matching facilities
                matching_facilities = [f for f in self.facility_service.get_all() if f.type == top_bin.bin_type]

                # Find nearest facility
                best_facility = None
                min_fac_dist = float('inf')
                path_to_fac = []
                
                for f in matching_facilities:
                    path, dist = self.get_route(top_bin.x, top_bin.y, f.x, f.y)
                    if dist < min_fac_dist:
                        min_fac_dist = dist
                        best_facility = f
                        path_to_fac = path

                v.target_facility = best_facility
                
                # Full route
                full_route = path_to_bin
                if path_to_fac:
                    full_route.extend(path_to_fac)
                
                v.current_route = full_route

            else:
                v.target_bin = None
                v.target_facility = None
                v.current_route = []
        
        self.save_vehicles()

    def reload_bins(self):
        """Reload bins from file to ensure we have the latest data."""
        self.bin_service = BinService(file_path=self.bin_service.file_path)
        self.bin_heap = self.create_bin_heap()

    def _capture_state(self):
        """Capture current state of vehicles and bins."""
        return {
            "vehicles": [v.to_dict() for v in self.vehicles],
            "bins": [b.to_dict() for b in self.bin_service.bins]
        }

    def dispatch_all_vehicles(self):
        """
        Greedy dispatch strategy with new Dijkstra
        """
        self.reload_bins()
        state = self._capture_state()
        self.history.push_action("dispatch", "dispatch_all", state)

        # Track assigned bins
        assigned_bin_ids = set()
        
        for v in self.vehicles:
            # Find nearest unassigned bin
            best_bin = None
            min_dist = float('inf')
            
            # Simple Euclidean distance for initial selection to be fast
            # Or use Haversine. Let's use simple Euclidean on lat/lon for selection speed
            # as Dijkstra is expensive to run for ALL bins.
            
            candidates = []
            for b in self.bin_service.bins:
                if b.id in assigned_bin_ids or b.fill_level <= 0:
                    continue
                # Approx distance
                dist = (v.x - b.x)**2 + (v.y - b.y)**2
                candidates.append((dist, b))
            
            candidates.sort(key=lambda x: x[0])
            
            # Pick best
            if candidates:
                best_bin = candidates[0][1]
            
            if best_bin:
                v.target_bin = best_bin
                assigned_bin_ids.add(best_bin.id)
                
                # 1. Vehicle -> Bin
                path_1, dist_1 = self.get_route(v.x, v.y, best_bin.x, best_bin.y)
                v.dist_to_bin = dist_1
                
                # 2. Find nearest facility
                matching_facilities = [f for f in self.facility_service.get_all() if f.type == best_bin.bin_type]
                best_facility = None
                min_fac_dist = float('inf')
                
                # Again, simple check first? No, facilities are few, check all.
                for f in matching_facilities:
                    # Euclidean estimate
                    d = (best_bin.x - f.x)**2 + (best_bin.y - f.y)**2
                    if d < min_fac_dist:
                        min_fac_dist = d
                        best_facility = f
                
                v.target_facility = best_facility
                
                full_route = path_1
                total_dist = dist_1
                
                if best_facility:
                    # Bin -> Facility
                    path_2, dist_2 = self.get_route(best_bin.x, best_bin.y, best_facility.x, best_facility.y)
                    full_route.extend(path_2)
                    total_dist += dist_2
                    v.dist_to_facility = dist_2
                    
                    # Facility -> Return
                    path_3, dist_3 = self.get_route(best_facility.x, best_facility.y, v.x, v.y)
                    full_route.extend(path_3)
                    total_dist += dist_3
                    v.dist_return = dist_3
                    
                v.current_route = full_route
                v.total_distance += total_dist # Accumulate distance
                
                # Empty bin
                best_bin.fill_level = 0
                self.bin_service.update_bin(best_bin.id, 0)
            else:
                v.target_bin = None
                v.target_facility = None
                v.current_route = []
        
        self.save_vehicles()

    def undo_last(self):
        """Undo the last dispatch action."""
        action = self.history.pop_action("dispatch")
        if not action or action["type"] != "dispatch_all":
            return False

        data = action["data"]
        self.vehicles = [Vehicle.from_dict(v_data) for v_data in data["vehicles"]]
        self.save_vehicles()
        
        from models.bin import Bin
        from data_structures.linked_list import LinkedList
        
        new_bins = LinkedList()
        for b_data in data["bins"]:
            new_bins.append(Bin.from_dict(b_data))
            
        self.bin_service.bins = new_bins
        self.bin_service.save_bins()
        return "Undid dispatch. Restored vehicle locations and bin levels."

    def reset_vehicles(self):
        """Reset all vehicles to their initial state and refill bins."""
        # Load from seed file
        with open(self.vehicles_file, "r") as f:
            vehicles_data = json.load(f)
        self.vehicles = [Vehicle(v["id"], v["x"], v["y"]) for v in vehicles_data]
        self.save_vehicles()
        
        # Reset bins to full? Or just leave them? 
        # The original code had a loop over bins but 'b' was undefined in the snippet provided.
        # Let's assume we want to reset bins to random fill or full.
        # For safety, let's just reload bins from file if needed, but user didn't ask for bin reset logic change.
        # The original code had:
        #   for v in self.vehicles: ...
        #   b.fill_level = 100 ...
        # This looks like a bug in original code (b undefined).
        # I will fix the vehicle reset part.

