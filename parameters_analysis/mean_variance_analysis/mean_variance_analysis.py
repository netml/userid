import os
import socket
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Load the data from the CSV file
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
csv_path = os.path.join(root_dir, 'network_traffic.csv')
df = pd.read_csv(csv_path)

def get_domain(ip):
    try:
        domain = socket.gethostbyaddr(ip)[0]
    except socket.herror:
        domain = "Unknown"
    return domain

# Group by source and destination to create flows
flows = df.groupby(['source_ip', 'destination_ip']).agg({
    'total_packets': 'sum',
    'packet_size': list,
    'inter_arrival_time': list,
    'temporal_patterns': list,
    'session_count' : list
}).reset_index()

# Create the table
table_data = []

for index, row in flows.iterrows():
    packet_details = "<br>".join([
        f"Time: {timestamp} <br>Mean size: {size} bytes, Flow time: {time} ms, Session packets: {sessioncount} <br>"
        for size, sessioncount,  time, timestamp in zip(row['packet_size'], row['session_count'], row['inter_arrival_time'], row['temporal_patterns'])
    ])

    # Appending a combination of grouped total packets and individual packet details
    table_data.append([
        row['source_ip'] + '<br>(' + get_domain(row['source_ip']) +  ')',
        row['destination_ip'] + '<br>(' + get_domain(row['destination_ip']) +  ')',
        row['total_packets'],  # Sum of total packets
        packet_details  # Details of individual packets
    ])

fig = go.Figure(data=[go.Table(
    columnwidth=[200, 200, 50, 400],
    header=dict(
        values=["Source IP", "Destination IP", "Total Packets", "Packet Details"],
        fill_color='paleturquoise',
        align='left',
        font=dict(size=12)
    ),
    cells=dict(
        values=[list(col) for col in zip(*table_data)],
        fill_color='lavender',
        align='left',
        font=dict(size=10),
        height=30,
        format=[None, None, None, None],
        line_color='darkslategray',
    ))
])

# Update layout to make it scrollable and fit text
fig.update_layout(
    title="Network Flow Table with Packet Details",
    height=500,  # Adjust height to enable scrolling
    margin=dict(l=0, r=0, t=30, b=0),
)


# Save as HTML
html_path = 'flow_table.html'
fig.write_html(html_path)

fig.show()


################## ----- Mean and Variance Analysis --------------- ##############

# Create a scatter plot
fig = px.scatter(df,
                 x='mean_packet_size',
                 y='variance_packet_size',
                 color='source_ip',  # Color by source IP to identify different flows
                 hover_data=['source_ip', 'destination_ip', 'total_packets'],
                 title="Mean Packet Size vs Variance Packet Size",
                 labels={
                     "mean_packet_size": "Mean Packet Size (bytes)",
                     "variance_packet_size": "Variance in Packet Size"
                 })

# Save the plot as an HTML file
html_path = 'mean_variance_visualization.html'
fig.write_html(html_path)

print(f"Plot saved as {html_path}")