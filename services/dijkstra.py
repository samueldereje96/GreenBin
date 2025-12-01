import heapq
import math

class Graph:
    def __init__(self):
        self.nodes = {} # id -> (lat, lon)
        self.edges = {} # id -> {neighbor_id: weight}

    def add_node(self, id, lat, lon):
        self.nodes[id] = (lat, lon)
        self.edges[id] = {}

    def add_edge(self, u, v, weight):
        self.edges[u][v] = weight
        self.edges[v][u] = weight # Undirected graph

    def get_neighbors(self, u):
        return self.edges.get(u, {})

def calculate_distance(lat1, lon1, lat2, lon2):
    """Haversine distance in meters"""
    R = 6371000 # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def generate_grid_graph(min_lat, max_lat, min_lon, max_lon, step_km=0.5):
    """
    Generates a grid graph covering the bounding box.
    step_km: approximate distance between nodes in km
    """
    graph = Graph()
    
    # Approximate degrees per step
    lat_step = step_km / 111.0
    lon_step = step_km / (111.0 * math.cos(math.radians((min_lat + max_lat)/2)))
    
    lats = []
    curr_lat = min_lat
    while curr_lat <= max_lat:
        lats.append(curr_lat)
        curr_lat += lat_step
        
    lons = []
    curr_lon = min_lon
    while curr_lon <= max_lon:
        lons.append(curr_lon)
        curr_lon += lon_step
        
    # Create nodes
    for i, lat in enumerate(lats):
        for j, lon in enumerate(lons):
            node_id = f"{i}_{j}"
            graph.add_node(node_id, lat, lon)
            
            # Connect to neighbors (Grid structure)
            # Left
            if j > 0:
                left_id = f"{i}_{j-1}"
                dist = calculate_distance(lat, lon, lats[i], lons[j-1])
                graph.add_edge(node_id, left_id, dist)
            
            # Bottom
            if i > 0:
                bottom_id = f"{i-1}_{j}"
                dist = calculate_distance(lat, lon, lats[i-1], lons[j])
                graph.add_edge(node_id, bottom_id, dist)
                
            # Diagonals (optional, for better paths)
            if i > 0 and j > 0:
                diag_id = f"{i-1}_{j-1}"
                dist = calculate_distance(lat, lon, lats[i-1], lons[j-1])
                graph.add_edge(node_id, diag_id, dist)
                
            if i > 0 and j < len(lons) - 1:
                diag_id = f"{i-1}_{j+1}"
                dist = calculate_distance(lat, lon, lats[i-1], lons[j+1])
                graph.add_edge(node_id, diag_id, dist)
                
    return graph

def find_nearest_node(graph, lat, lon):
    """Finds the closest node in the graph to the given coordinates"""
    min_dist = float('inf')
    nearest_id = None
    
    for node_id, coords in graph.nodes.items():
        dist = calculate_distance(lat, lon, coords[0], coords[1])
        if dist < min_dist:
            min_dist = dist
            nearest_id = node_id
            
    return nearest_id

def dijkstra(graph, start_node, end_node):
    """
    Dijkstra's algorithm to find shortest path.
    Returns: (path_coordinates, total_distance)
    """
    queue = [(0, start_node)] # (distance, node_id)
    distances = {node: float('inf') for node in graph.nodes}
    distances[start_node] = 0
    previous = {node: None for node in graph.nodes}
    
    visited = set()
    
    while queue:
        current_dist, current_node = heapq.heappop(queue)
        
        if current_node in visited:
            continue
        visited.add(current_node)
        
        if current_node == end_node:
            break
            
        for neighbor, weight in graph.get_neighbors(current_node).items():
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))
                
    # Reconstruct path
    path = []
    current = end_node
    if distances[end_node] == float('inf'):
        return [], 0 # No path found
        
    while current is not None:
        lat, lon = graph.nodes[current]
        path.append([lon, lat]) # OSRM/PyDeck format: [lon, lat]
        current = previous[current]
        
    path.reverse()
    return path, distances[end_node]
