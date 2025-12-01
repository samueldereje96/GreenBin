import json
import os
import math
import datetime
from models.vehicle import Vehicle
from models.bin import Bin
from models.facility import Facility
from services.dijkstra import generate_grid_graph, find_nearest_node, dijkstra
from services.history_service import HistoryService

class ActualMapService:
    def __init__(self):
        self.bins_file = "data/bins.json"
        self.vehicles_file = "data/vehicles.json"
        self.facilities_file = "data/facilities.json"
        
        self.bins = self.load_bins()
        self.vehicles = self.load_vehicles()
        self.facilities = self.load_facilities()
        self.history_service = HistoryService()
        
        # Initialize Dijkstra Grid Graph (Dubai Area)
        # Bounding box covering all points + buffer
        # Min Lat: ~25.0, Max Lat: ~25.4
        # Min Lon: ~55.0, Max Lon: ~55.5
        print("Generating grid graph...")
        self.graph = generate_grid_graph(25.0, 25.4, 55.0, 55.5, step_km=0.5)
        print(f"Graph generated with {len(self.graph.nodes)} nodes")

    def load_bins(self):
        if not os.path.exists(self.bins_file):
            return []
        with open(self.bins_file, "r") as f:
            data = json.load(f)
            return [Bin(b["id"], b["location"], b["x"], b["y"], b["fill_level"], b["bin_type"]) for b in data]

    def load_vehicles(self):
        if not os.path.exists(self.vehicles_file):
            return []
        with open(self.vehicles_file, "r") as f:
            data = json.load(f)
            return [Vehicle(v["id"], v["x"], v["y"]) for v in data]

    def load_facilities(self):
        if not os.path.exists(self.facilities_file):
            return []
        with open(self.facilities_file, "r") as f:
            data = json.load(f)
            return [Facility.from_dict(f) for f in data]

    def save_bins(self):
        data = [b.to_dict() for b in self.bins]
        with open(self.bins_file, "w") as f:
            json.dump(data, f, indent=4)

    def save_vehicles(self):
        data = [v.to_dict() for v in self.vehicles]
        with open(self.vehicles_file, "w") as f:
            json.dump(data, f, indent=4)
            
    def push_history(self, action, state):
        # Using HistoryService to push dispatch actions
        # Action is usually "dispatch" string in previous code, but HistoryService takes (category, type, data)
        # Here we use category="dispatch", type=action, data=state
        self.history_service.push_action("dispatch", action, state)

    def pop_history(self):
        # Pop from "dispatch" category
        action = self.history_service.pop_action("dispatch")
        if action:
            return action # Returns {type: ..., data: ...}
        return None

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Haversine distance in km"""
        R = 6371 # Earth radius in km
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    def get_dijkstra_route(self, start_lat, start_lon, end_lat, end_lon):
        """Fetch route using local Dijkstra algorithm"""
        
        # Find start/end nodes on grid
        start_node = find_nearest_node(self.graph, start_lat, start_lon)
        end_node = find_nearest_node(self.graph, end_lat, end_lon)
        
        if not start_node or not end_node:
            print("Nodes not found on grid")
            return [[start_lon, start_lat], [end_lon, end_lat]], 0
            
        # Run Dijkstra
        path, distance_meters = dijkstra(self.graph, start_node, end_node)
        
        # Add actual start/end points to path for smooth connection
        if path:
            path.insert(0, [start_lon, start_lat])
            path.append([end_lon, end_lat])
            
        return path, distance_meters

    def dispatch_all_vehicles(self):
        # Capture state for undo
        state = {
            "vehicles": [v.to_dict() for v in self.vehicles],
            "bins": [b.to_dict() for b in self.bins]
        }
        self.push_history("dispatch_all", state)

        # Simple greedy dispatch
        unassigned_bins = [b for b in self.bins if b.fill_level > 0]
        
        for v in self.vehicles:
            if not unassigned_bins:
                break
                
            # Find nearest bin
            best_bin = None
            min_dist = float('inf')
            
            for b in unassigned_bins:
                dist = self.calculate_distance(v.x, v.y, b.x, b.y)
                if dist < min_dist:
                    min_dist = dist
                    best_bin = b
            
            if best_bin:
                v.target_bin = best_bin
                v.dist_to_bin = min_dist
                
                # Find nearest facility of same type
                matching_facilities = [f for f in self.facilities if f.type == best_bin.bin_type]
                best_facility = None
                min_fac_dist = float('inf')
                
                for f in matching_facilities:
                    dist = self.calculate_distance(best_bin.x, best_bin.y, f.x, f.y)
                    if dist < min_fac_dist:
                        min_fac_dist = dist
                        best_facility = f
                
                v.target_facility = best_facility
                v.dist_to_facility = min_fac_dist if best_facility else 0
                
                # Create route with custom Dijkstra
                # 1. Vehicle -> Bin
                route_segment_1, dist_1 = self.get_dijkstra_route(v.x, v.y, best_bin.x, best_bin.y)
                
                full_route = route_segment_1
                total_dist = dist_1
                
                # 2. Bin -> Facility
                if best_facility:
                    route_segment_2, dist_2 = self.get_dijkstra_route(best_bin.x, best_bin.y, best_facility.x, best_facility.y)
                    # Append segment 2
                    full_route.extend(route_segment_2)
                    total_dist += dist_2
                    
                    # 3. Facility -> Return to Start
                    # We use v.x, v.y as the start because that's where it was before dispatch
                    route_segment_3, dist_3 = self.get_dijkstra_route(best_facility.x, best_facility.y, v.x, v.y)
                    full_route.extend(route_segment_3)
                    total_dist += dist_3
                
                v.current_route = full_route
                v.total_distance = total_dist # Store total distance in meters
                
                # "Empty" the bin
                best_bin.fill_level = 0
                unassigned_bins.remove(best_bin)
        
        self.save_bins()

    def reset_vehicles(self):
        # Reload initial state
        self.vehicles = self.load_vehicles()
        # Reset bins to full
        for b in self.bins:
            b.fill_level = 100
        self.save_bins()

    def undo_last(self):
        action = self.pop_history()
        if not action:
            return False
            
        data = action["data"]
        self.vehicles = [Vehicle.from_dict(v) for v in data["vehicles"]]
        self.bins = [Bin.from_dict(b) for b in data["bins"]]
        self.save_bins()
        return True
