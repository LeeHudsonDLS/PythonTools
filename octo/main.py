import pandas as pd
import matplotlib.pyplot as plt
from datetime import time

# Rates (in pounds)
OFF_PEAK_RATE = 0.085     # £/kWh
ON_PEAK_RATE = 0.2879     # £/kWh
DAILY_STANDING_CHARGE = 0.4394  # £/day

# Load CSV
df = pd.read_csv('consumption.csv', skipinitialspace=True, parse_dates=['Start', 'End'])

# Define off-peak window
offpeak_start = time(0, 30)
offpeak_end = time(5, 30)

def is_offpeak(start_dt, end_dt):
    start_t = start_dt.time()
    end_t = end_dt.time()
    return offpeak_start <= start_t < offpeak_end and offpeak_start < end_t <= offpeak_end

# Group consumption into off-peak or on-peak
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

# Display results and calculate costs
energy_cost_total = 0.0
dates = []
off_peaks = []
on_peaks = []
daily_costs = []

print("Daily Usage and Energy Cost (excluding standing charge):")
for day, usage in sorted(daily_usage.items()):
    off_kwh = usage['off_peak']
    on_kwh = usage['on_peak']
    off_cost = off_kwh * OFF_PEAK_RATE
    on_cost = on_kwh * ON_PEAK_RATE
    daily_total = off_cost + on_cost
    energy_cost_total += daily_total

    dates.append(str(day))
    off_peaks.append(off_kwh)
    on_peaks.append(on_kwh)
    daily_costs.append(daily_total)

    print(f"{day}: Off-peak = {off_kwh:.3f} kWh (£{off_cost:.2f}), "
          f"On-peak = {on_kwh:.3f} kWh (£{on_cost:.2f}), "
          f"Energy Cost = £{daily_total:.2f}")

# Final totals
num_days = len(daily_usage)
standing_charge_total = num_days * DAILY_STANDING_CHARGE
total_cost = energy_cost_total + standing_charge_total

print(f"\nTotal energy cost (excluding standing charge): £{energy_cost_total:.2f}")
print(f"Standing charge total ({num_days} days at £{DAILY_STANDING_CHARGE:.4f}/day): £{standing_charge_total:.2f}")
print(f"Total cost including standing charges: £{total_cost:.2f}")

# ----- Plot -----
fig, ax1 = plt.subplots(figsize=(10, 6))

# Bar chart for energy use
ax1.bar(dates, off_peaks, label='Off-peak kWh', color='royalblue')
ax1.bar(dates, on_peaks, bottom=off_peaks, label='On-peak kWh', color='darkorange')
ax1.set_ylabel('Energy Used (kWh)')
ax1.set_xlabel('Date')
ax1.legend(loc='upper left')
ax1.set_title('Daily Energy Use and Cost Breakdown')

# Line chart for daily cost (right y-axis)
ax2 = ax1.twinx()
ax2.plot(dates, daily_costs, label='Daily Cost (£)', color='green', marker='o', linewidth=2)
ax2.set_ylabel('Daily Cost (£)')
ax2.legend(loc='upper right')

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

