# services/report_service.py
from services.request_service import RequestService
from services.bin_service import BinService
from services.facility_service import FacilityService
from services.history_service import HistoryService

class ReportService:
    EMISSION_FACTOR = 0.2  # kg CO2 per km, example

    def __init__(self):
        self.request_service = RequestService()
        self.bin_service = BinService()
        self.facility_service = FacilityService()
        self.history_service = HistoryService()

    def co2_saved_per_facility(self):
        """Return dict {facility_name: co2_saved}"""
        facilities = self.facility_service.get_all()
        result = {f.name: 0 for f in facilities}
        
        # Get processed requests from history
        stack = self.history_service.get_stack("request")
        if not stack or stack.is_empty():
            return result
            
        history_list = stack.to_list()
        
        for h in history_list:
            if h["type"] == "process_request":
                data = h["data"]
                bin_id = data.get("bin_id")
                
                bin_obj = self.bin_service.get_bin_by_id(bin_id)
                if not bin_obj:
                    continue
                    
                # Find nearest facility of same type
                matching_facilities = [f for f in facilities if f.type == bin_obj.bin_type]
                if not matching_facilities:
                    continue
                    
                # Find closest facility (Haversine distance)
                best_fac = None
                min_dist_km = float('inf')
                
                for fac in matching_facilities:
                    # x is lat, y is lon based on data inspection
                    dist_km = self._haversine_distance(bin_obj.x, bin_obj.y, fac.x, fac.y)
                    if dist_km < min_dist_km:
                        min_dist_km = dist_km
                        best_fac = fac
                
                if best_fac:
                    co2 = min_dist_km * self.EMISSION_FACTOR
                    result[best_fac.name] += co2

        return result

    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """
        import math
        # Convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

        # Haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a)) 
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles
        return c * r

    def total_requests(self):
        return len(self.request_service.get_all_requests())

    def total_bins(self):
        return len(self.bin_service.bins)
