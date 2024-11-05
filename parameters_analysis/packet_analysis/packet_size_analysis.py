import os
import socket

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from matplotlib import pyplot as plt
from plotly.subplots import make_subplots
import seaborn as sns

# Load the data from the CSV file
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
csv_path = os.path.join(root_dir, 'network_traffic.csv')
df = pd.read_csv(csv_path)

# Display basic statistics about packet sizes
print(df['packet_size'].describe())

# Check for missing values in packet size
print(df['packet_size'].isnull().sum())

# Calculate header size
df['header_size'] = df['packet_size'] - df['payload_size']

# Create subplots
fig = make_subplots(rows=3, cols=1, subplot_titles=('Total Packet Size', 'Payload Size', 'Header Size'))

# Plot Total Packet Size distribution
total_trace = go.Histogram(
    x=df['packet_size'],
    nbinsx=30,
    name='Total Packet Size',
    marker_color='blue',
    opacity=0.6,
    hovertemplate="Packet Size: %{x}<br>Frequency: %{y}<extra></extra>"
)
fig.add_trace(total_trace, row=1, col=1)

# Plot Payload Size distribution
payload_trace = go.Histogram(
    x=df['payload_size'],
    nbinsx=30,
    name='Payload Size',
    marker_color='green',
    opacity=0.6,
    hovertemplate="Payload Size: %{x}<br>Frequency: %{y}<extra></extra>"
)
fig.add_trace(payload_trace, row=2, col=1)

# Plot Header Size distribution
header_trace = go.Histogram(
    x=df['header_size'],
    nbinsx=30,
    name='Header Size',
    marker_color='orange',
    opacity=0.6,
    hovertemplate="Header Size: %{x}<br>Frequency: %{y}<extra></extra>"
)
fig.add_trace(header_trace, row=3, col=1)

# Update x-axes to show every packet size without gaps
fig.update_xaxes(tickmode='linear', dtick=100, title_text="Size (bytes)")

# Customize layout for better readability
fig.update_layout(
    height=900,
    width=800,
    title_text="Packet Size, Payload Size, and Header Size Distributions",
    showlegend=False
)


# Update y-axes to show frequency
fig.update_yaxes(title_text="Frequency")

# Save the figure as an HTML file
fig.write_html("packet_size_distribution.html")

# Show the figure
fig.show()

#####

df['temporal_patterns'] = pd.to_datetime(df['temporal_patterns'])

# Plot packet sizes over time
plt.figure(figsize=(14, 7))
sns.lineplot(x='temporal_patterns', y='packet_size', data=df)
plt.title('Packet Sizes Over Time')
plt.xlabel('Timestamp')
plt.ylabel('Packet Size (Bytes)')
plt.show()

# Scatter plot of packet size vs. source port
plt.figure(figsize=(10, 6))
sns.scatterplot(x='source_port', y='packet_size', data=df)
plt.title('Packet Size vs. Source Port')
plt.xlabel('Source Port')
plt.ylabel('Packet Size (Bytes)')
plt.show()

# Scatter plot of packet size vs. destination port
plt.figure(figsize=(10, 6))
sns.scatterplot(x='destination_port', y='packet_size', data=df)
plt.title('Packet Size vs. Destination Port')
plt.xlabel('Destination Port')
plt.ylabel('Packet Size (Bytes)')
plt.show()

#### ============================== Final with TimeLine ============================


def get_domain(ip):
    try:
        domain = socket.gethostbyaddr(ip)[0]
    except socket.herror:
        domain = "Unknown"
    return domain

# Apply this function to your dataframe
df['source_domain'] = df['source_ip'].apply(get_domain)
df['destination_domain'] = df['destination_ip'].apply(get_domain)

# Ensure temporal patterns are in datetime format if not already
df['temporal_patterns'] = pd.to_datetime(df['temporal_patterns'])

# Calculate header size
df['header_size'] = df['packet_size'] - df['payload_size']

# Define thresholds for anomaly detection (example values)
anomaly_thresholds = {
    'TCP': {'min_payload': 40, 'max_payload': 1500, 'min_header': 10, 'max_header': 60},
    'UDP': {'min_payload': 50, 'max_payload': 1500, 'min_header': 8, 'max_header': 60}
}

# Define colors for different protocols and data types
protocol_colors = {
    'TCP': {'payload': 'green', 'header': 'grey', 'anomaly_payload': '#ADD8E6', 'anomaly_header': '#E0FFFF'},
    'UDP': {'payload': 'red', 'header': 'black', 'anomaly_payload': '#90EE90', 'anomaly_header': '#FFDAB9'}
}

# Plotting using Plotly for interactive HTML output
fig = go.Figure()

# Add data points and highlight anomalies
for protocol in df['protocol'].unique():
    protocol_data = df[df['protocol'] == protocol]

    # Plot Payload Sizes
    fig.add_trace(go.Scatter(
        x=protocol_data['temporal_patterns'],
        y=protocol_data['payload_size'],
        mode='markers',
        name=f'{protocol} Payload Size',
        marker=dict(size=5, color=protocol_colors[protocol]['payload']),
        text=protocol_data.apply(lambda
                                     row: f"Size: {row['payload_size']} bytes (Payload)<br>Header Size: {row['header_size']} bytes<br>Protocol: {row['protocol']}<br>Source: {row['source_domain']}<br>Destination: {row['destination_domain']}",
                                 axis=1),
        hoverinfo='text'
    ))

    # Plot Header Sizes
    fig.add_trace(go.Scatter(
        x=protocol_data['temporal_patterns'],
        y=protocol_data['header_size'],
        mode='markers',
        name=f'{protocol} Header Size',
        marker=dict(size=5, color=protocol_colors[protocol]['header']),
        text=protocol_data.apply(lambda
                                     row: f"Size: {row['header_size']} bytes (Header)<br>Payload Size: {row['payload_size']} bytes<br>Protocol: {row['protocol']}<br>Source: {row['source_domain']}<br>Destination: {row['destination_domain']}",
                                 axis=1),
        hoverinfo='text'
    ))

    # Highlight anomalies
    if protocol in anomaly_thresholds:
        thresholds = anomaly_thresholds[protocol]
        anomaly_data = protocol_data[
            (protocol_data['payload_size'] < thresholds['min_payload']) |
            (protocol_data['payload_size'] > thresholds['max_payload']) |
            (protocol_data['header_size'] < thresholds['min_header']) |
            (protocol_data['header_size'] > thresholds['max_header'])
            ]

        fig.add_trace(go.Scatter(
            x=anomaly_data['temporal_patterns'],
            y=anomaly_data['payload_size'],
            mode='markers',
            name=f'{protocol} Anomalous Payload Size',
            marker=dict(size=8, color=protocol_colors[protocol]['anomaly_payload']),
            text=anomaly_data.apply(lambda
                                        row: f"Size: {row['payload_size']} bytes (Payload)<br>Header Size: {row['header_size']} bytes<br>Protocol: {row['protocol']}<br>Source: {row['source_domain']}<br>Destination: {row['destination_domain']}",
                                    axis=1),
            hoverinfo='text'
        ))

        fig.add_trace(go.Scatter(
            x=anomaly_data['temporal_patterns'],
            y=anomaly_data['header_size'],
            mode='markers',
            name=f'{protocol} Anomalous Header Size',
            marker=dict(size=8, color=protocol_colors[protocol]['anomaly_header']),
            text=anomaly_data.apply(lambda
                                        row: f"Size: {row['header_size']} bytes (Header)<br>Payload Size: {row['payload_size']} bytes<br>Protocol: {row['protocol']}<br>Source: {row['source_domain']}<br>Destination: {row['destination_domain']}",
                                    axis=1),
            hoverinfo='text'
        ))

# Update layout
fig.update_layout(
    title='Packet Sizes Over Time with Anomaly Detection',
    xaxis_title='Time',
    yaxis_title='Size (bytes)',
    legend_title='Legend',
    xaxis_rangeslider_visible=True
)

# Save as HTML
html_path = 'packet_size_anomaly_detection.html'
fig.write_html(html_path)

# Optionally show the plot in a notebook or other environment
fig.show()