from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import F, ExpressionWrapper, fields
from datetime import timedelta
from .models import ActualGeneration, ForecastGeneration
import pandas as pd

class WindDataAPIView(APIView):
    def get(self, request):
        # 1. Grab parameters from the React frontend (with safe defaults)
        start_str = request.GET.get('start', '2024-01-01T00:00:00Z')
        end_str = request.GET.get('end', '2024-01-31T23:59:59Z')
        horizon_hours = float(request.GET.get('horizon', 0))

        # 2. Fetch Actuals for the date range
        actuals = ActualGeneration.objects.filter(
            timestamp__gte=start_str,
            timestamp__lte=end_str
        ).values('timestamp', 'generation_mw')

        # 3. The "Founding Engineer" Horizon Logic
        # We need forecasts where (target_time - publish_time) >= horizon_hours
        # Django ORM can do this math directly in the database for extreme speed!
        horizon_delta = timedelta(hours=horizon_hours)
        
        forecasts = ForecastGeneration.objects.annotate(
            horizon=ExpressionWrapper(
                F('target_time') - F('publish_time'), 
                output_field=fields.DurationField()
            )
        ).filter(
            target_time__gte=start_str,
            target_time__lte=end_str,
            horizon__gte=horizon_delta
        ).values('target_time', 'generation_mw', 'publish_time')

        # 4. Merge the data into a single time-series array for React/Recharts
        # Using a dictionary for O(1) lookups by timestamp
        merged_data = {}

        # Add Actuals
        for act in actuals:
            ts = act['timestamp'].isoformat()
            merged_data[ts] = {
                'timestamp': ts,
                'actual_mw': act['generation_mw'],
                'forecast_mw': None 
            }

        # Add Forecasts (If multiple forecasts exist for the same target, we take the one closest to the horizon)
        # We sort by publish_time descending so the most recent valid forecast overwrites older ones
        sorted_forecasts = sorted(forecasts, key=lambda x: x['publish_time'])
        
        for fcast in sorted_forecasts:
            ts = fcast['target_time'].isoformat()
            if ts not in merged_data:
                merged_data[ts] = {
                    'timestamp': ts,
                    'actual_mw': None,
                    'forecast_mw': fcast['generation_mw']
                }
            else:
                merged_data[ts]['forecast_mw'] = fcast['generation_mw']

        # Convert dictionary back to a sorted list for the frontend chart
        chart_data = sorted(merged_data.values(), key=lambda x: x['timestamp'])

        return Response({"data": chart_data})