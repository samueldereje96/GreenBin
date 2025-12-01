import heapq
from services.bin_service import BinService
from datetime import datetime, timedelta

class PredictionService:
    DEFAULT_FILL_RATE = 5  # % per hour if no historical data

    def __init__(self, bin_service: BinService):
        self.bin_service = bin_service

    def predict_fill(self, hours_ahead=2):
        """
        Predict fill level of all bins after `hours_ahead` hours.
        Returns a list of tuples: (predicted_fill, bin_obj)
        """
        predicted_list = []

        for b in self.bin_service.bins:
            # Simple prediction: current fill + (fill_rate * hours)
            fill_rate = getattr(b, "avg_fill_rate", self.DEFAULT_FILL_RATE)
            predicted_fill = b.fill_level + fill_rate * hours_ahead
            predicted_fill = min(predicted_fill, 100)  # cap at 100%
            predicted_list.append((predicted_fill, b))

        return predicted_list

    def top_overflow_bins(self, hours_ahead=2, top_n=5):
        """
        Return top_n bins predicted to overflow soonest.
        Uses a min-heap to track bins with highest predicted fill.
        """
        predicted = self.predict_fill(hours_ahead)
        
        # Create a max-heap based on predicted fill
        max_heap = [(-fill, b) for fill, b in predicted]
        heapq.heapify(max_heap)

        top_bins = []
        for _ in range(min(top_n, len(max_heap))):
            neg_fill, b = heapq.heappop(max_heap)
            top_bins.append((-neg_fill, b))  # convert back to positive fill

        return top_bins
