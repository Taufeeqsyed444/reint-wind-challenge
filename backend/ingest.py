import os
import django
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
from datetime import timedelta, date
import time

# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import ActualGeneration, ForecastGeneration

# 2. Configure a Resilient Session
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

def daterange(start_date, end_date):
    """Generator for looping through days"""
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def fetch_all_data():
    # Setting range for the full month of Jan 2024 as per challenge requirements
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    print("🚀 Initiating Final Resilient Ingestion for Jan 2024...")
    
    for single_date in daterange(start_date, end_date):
        date_str = single_date.strftime("%Y-%m-%d")
        
        # Check if we already have ACTUALS for this day to avoid redundant API calls
        # If actuals exist but forecasts are missing, it will still proceed to fetch
        existing_actuals = ActualGeneration.objects.filter(timestamp__date=single_date).count()
        existing_forecasts = ForecastGeneration.objects.filter(target_time__date=single_date).count()

        if existing_actuals > 40 and existing_forecasts > 100:
            print(f"✅ Skipping {date_str} (Full data already exists)")
            continue
            
        print(f"📡 Fetching {date_str}...")
        actuals_to_create = []
        forecasts_to_create = []
        
        # --- 1. Fetch Actuals (FUELHH) ---
        url_act = "https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH"
        params_act = {
            "settlementDateFrom": date_str,
            "settlementDateTo": date_str,
        }
        
        try:
            res_act = session.get(url_act, params=params_act, timeout=15)
            if res_act.status_code == 200:
                data_act = res_act.json().get('data', [])
                for item in data_act:
                    if item.get('fuelType') == 'WIND':
                        try:
                            ts = pd.to_datetime(item['startTime'])
                            gen = float(item['generation'])
                            actuals_to_create.append(ActualGeneration(timestamp=ts, generation_mw=gen))
                        except (KeyError, ValueError, TypeError):
                            pass
        except Exception as e:
            print(f"   ❌ Error fetching actuals for {date_str}: {e}")

        # --- 2. Fetch Forecasts (WINDFOR) ---
        # Using settlementDate range ensures we get forecasts TARGETING this day, 
        # regardless of when they were published.
        url_for = "https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR"
        params_for = {
            "settlementDateFrom": date_str,
            "settlementDateTo": date_str,
        }
        
        try:
            res_for = session.get(url_for, params=params_for, timeout=15)
            if res_for.status_code == 200:
                data_for = res_for.json().get('data', [])
                for item in data_for:
                    try:
                        pub_ts = pd.to_datetime(item['publishTime'])
                        tar_ts = pd.to_datetime(item['startTime'])
                        gen = float(item['generation'])
                        
                        forecasts_to_create.append(
                            ForecastGeneration(publish_time=pub_ts, target_time=tar_ts, generation_mw=gen)
                        )
                    except (KeyError, ValueError, TypeError):
                        pass
        except Exception as e:
            print(f"   ❌ Error fetching forecasts for {date_str}: {e}")

        # --- 3. Atomic DB Write ---
        if actuals_to_create:
            ActualGeneration.objects.bulk_create(actuals_to_create, ignore_conflicts=True)
        if forecasts_to_create:
            ForecastGeneration.objects.bulk_create(forecasts_to_create, ignore_conflicts=True)
            
        print(f"   💾 Saved: {len(actuals_to_create)} Actuals | {len(forecasts_to_create)} Forecasts")
        
        # Respectful delay for the Elexon API
        time.sleep(1)
    
    print("\n🏁 SUCCESS! The database is now fully populated.")

if __name__ == "__main__":
    fetch_all_data()