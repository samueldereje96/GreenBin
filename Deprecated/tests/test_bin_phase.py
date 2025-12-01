# test_bin_phase.py
import sys
import os

# Ensure the project root is in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from services.bin_service import BinService
from models.bin import Bin

service = BinService()

# Add new bin
bin1 = Bin(bin_id="B001", location="Area A", bin_type="household", capacity=100, x = 2, y = 5)
service.add_bin(bin1)

# List bins
for b in service.list_bins():
    print(b.to_dict())

# Find bin
found = service.get_bin("B001")
print("Found:", found.to_dict())

# Remove bin
# service.remove_bin("B001")
