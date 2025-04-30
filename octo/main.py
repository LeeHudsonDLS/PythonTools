import pandas as pd
import matplotlib.pyplot as plt
from datetime import time

# ====== SETTINGS ======
START_DATE = '2025-03-28'
END_DATE = '2025-04-27'

OFF_PEAK_RATE = 0.085    # £/kWh
ON_PEAK_RATE = 0.2879    # £/kWh
DAILY_STANDING_CHARGE = 0.4394  # £/day
# =======================

# Load CSV with possible BOM and clean whitespace
df = pd.read_csv('consumption.csv', skipinitialspace=True)

# Debug date parsing
print("Start column dtype before conversion:", df['Start'].dtype)

# Force parse Start and End columns as UTC datetime
df['Start'] = pd.to_datetime(df['Start'], errors='coerce', utc=True)
df['End'] = pd.to_datetime(df['End'], errors='coerce', utc=True)

print("Start column dtype after conversion:", df['Start'].dtype)

# Drop rows with invalid datetimes
df = df.dropna(subset=['Start', 'End'])

# Filter by date range
start_ts = pd.to_datetime(START_DATE, utc=True)
end_ts = pd.to_datetime(END_DATE, utc=True) + pd.Timedelta(days=1)
df = df[(df['Start'] >= start_ts) & (df['Start'] < end_ts)]

# Define off-peak hours
offpeak_start = time(0, 30)
offpeak_end = time(5, 30)

def is_offpeak(start_dt, end_dt):
    t1 = start_dt.time()
    t2 = end_dt.time()
    return offpeak_start <= t1 < offpeak_end and offpeak_start < t2 <= offpeak_end

# Group usage
daily_usage = {}

for _, row in df.iterrows():
    day = row['Start'].date()
    kwh = row['Consumption (kWh)']
    if day not in daily_usage:
        daily_usage[day] = {'off_peak': 0.0, 'on_peak': 0.0}
    
    if is_offpeak(row['Start'], row['End']):
        daily_usage[day]['off_peak'] += kwh
    else:
        daily_usage[day]['on_peak'] += kwh

# Print summary and collect data for plotting
dates = []
off_peaks = []
on_peaks = []
daily_costs = []
energy_cost_total = 0.0

print("\nDaily Usage and Cost (excluding standing charge):")
print("--------------------------------------------------")

for day, usage in sorted(daily_usage.items()):
    off_kwh = usage['off_peak']
    on_kwh = usage['on_peak']
    off_cost = off_kwh * OFF_PEAK_RATE
    on_cost = on_kwh * ON_PEAK_RATE
    daily_cost = off_cost + on_cost

    energy_cost_total += daily_cost
    dates.append(str(day))
    off_peaks.append(off_kwh)
    on_peaks.append(on_kwh)
    daily_costs.append(daily_cost)

    print(f"{day}: Off-peak = {off_kwh:.3f} kWh (£{off_cost:.2f}), "
          f"On-peak = {on_kwh:.3f} kWh (£{on_cost:.2f}), "
          f"Energy Cost = £{daily_cost:.2f}")

# Totals
num_days = len(daily_usage)
standing_charge_total = num_days * DAILY_STANDING_CHARGE
total_cost = energy_cost_total + standing_charge_total

print("\n--------------------------------------------------")
print(f"Total energy cost (no standing charge): £{energy_cost_total:.2f}")
print(f"Standing charge total ({num_days} days at £{DAILY_STANDING_CHARGE:.4f}/day): £{standing_charge_total:.2f}")
print(f"➡️  Total cost including standing charge: £{total_cost:.2f}")

# Plot usage and cost
if dates:
    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.bar(dates, off_peaks, label='Off-peak kWh', color='royalblue')
    ax1.bar(dates, on_peaks, bottom=off_peaks, label='On-peak kWh', color='darkorange')
    ax1.set_ylabel('Energy Used (kWh)')
    ax1.set_xlabel('Date')
    ax1.legend(loc='upper left')
    ax1.set_title(f'Energy Use and Cost Breakdown ({START_DATE} to {END_DATE})')

    ax2 = ax1.twinx()
    ax2.plot(dates, daily_costs, label='Daily Cost (£)', color='green', marker='o', linewidth=2)
    ax2.set_ylabel('Daily Cost (£)')
    ax2.legend(loc='upper right')

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
else:
    print("No data available in the selected date range.")

