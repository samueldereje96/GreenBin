import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from services.vehicle_service import VehicleService
from services.city_serivce import create_city_grid

def verify_dispatch():
    print("Initializing VehicleService...")
    service = VehicleService()
    
    print("Initial Vehicle States:")
    for v in service.vehicles:
        print(f"Vehicle {v.id} at ({v.x}, {v.y}) - Target Bin: {v.target_bin}, Target Facility: {v.target_facility}")

    print("\nRunning dispatch_all_vehicles()...")
    service.dispatch_all_vehicles()
    
    print("\nPost-Dispatch Vehicle States:")
    all_dispatched = True
    for v in service.vehicles:
        status = "ASSIGNED" if v.target_bin else "UNASSIGNED"
        print(f"Vehicle {v.id} at ({v.x}, {v.y}) -> Bin: {v.target_bin.id if v.target_bin else 'None'} -> Facility: {v.target_facility.name if v.target_facility else 'None'} | Route Len: {len(v.current_route)}")
        
        if not v.target_bin:
            all_dispatched = False
            
    if all_dispatched:
        print("\nSUCCESS: All vehicles dispatched.")
    else:
        print("\nWARNING: Some vehicles were not dispatched (might be expected if no bins/facilities available).")

if __name__ == "__main__":
    verify_dispatch()
