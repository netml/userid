import os
import pandas as pd
import plotly.express as px

# Load the data from the CSV file
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
csv_path = os.path.join(root_dir, 'network_traffic.csv')
df = pd.read_csv(csv_path)

# Create a bar chart to show traffic volume by country
fig = px.bar(df,
             x='country',
             y='total_packets',
             color='country',
             hover_data=['region', 'city', 'source_ip', 'destination_ip'],
             title="Network Traffic by Country",
             labels={
                 "total_packets": "Total Packets",
                 "country": "Country"
             })

# Save the plot as an HTML file
output_html = 'country_traffic_visualization.html'
fig.write_html(output_html)

print(f"Plot saved as {output_html}")


fig = px.bar(df,
             x='region',  # You can switch between 'country', 'region', or 'city' as the x-axis
             y='total_packets',
             color='country',  # Color code by country
             hover_data=['country', 'city', 'source_ip', 'destination_ip'],
             title="Network Traffic by Country, Region, and City",
             labels={
                 "total_packets": "Total Packets",
                 "region": "Region",
                 "city": "City"
             })

# Save the plot as an HTML file
output_html = 'region_city_traffic_visualization.html'
fig.write_html(output_html)

print(f"Plot saved as {output_html}")