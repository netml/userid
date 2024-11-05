import os
import pandas as pd
import plotly.express as px

# Load the data from the CSV file
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
csv_path = os.path.join(root_dir, 'network_traffic.csv')
df = pd.read_csv(csv_path)

# Convert timestamp to datetime
df['temporal_patterns'] = pd.to_datetime(df['temporal_patterns'])

# Aggregate data by day
daily_traffic = df.groupby(['temporal_patterns']).agg({'total_packets': 'sum'}).reset_index()
daily_traffic.set_index('temporal_patterns', inplace=True)

# Calculate rolling average
daily_traffic['rolling_avg'] = daily_traffic['total_packets'].rolling(window=7).mean()

# Create a line plot with rolling average
fig = px.line(daily_traffic,
              x=daily_traffic.index,
              y=['total_packets', 'rolling_avg'],
              title="Daily Network Traffic with Rolling Average",
              labels={
                  "value": "Total Packets",
                  "timestamp": "Date"
              })

# Save the plot as an HTML file
output_html = 'daily_traffic_rolling_avg.html'
fig.write_html(output_html)

print(f"Plot saved as {output_html}")