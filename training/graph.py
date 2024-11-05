import os
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from sklearn.preprocessing import LabelEncoder

# Load CSV file
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
csv_path = os.path.join(root_dir + '/humanbehaviour', 'tokenized_data.csv')
df = pd.read_csv(csv_path)

# Clean up column names in case of extra spaces
df.columns = df.columns.str.strip()

# Print column names to check if they exist
print(df.columns)

# Tokenization using LabelEncoder for IP addresses and protocol
le = LabelEncoder()

# Ensure the 'source_ip_token', 'destination_ip_token', and 'protocol_token' columns exist
if 'source_ip_token' in df.columns and 'destination_ip_token' in df.columns and 'protocol_token' in df.columns:
    # Apply LabelEncoder to the IP address and protocol fields
    df['source_ip_token'] = le.fit_transform(df['source_ip_token'])
    df['destination_ip_token'] = le.fit_transform(df['destination_ip_token'])
    df['protocol_token'] = le.fit_transform(df['protocol_token'])
else:
    print("Missing necessary columns 'source_ip_token', 'destination_ip_token', or 'protocol_token'")

# Normalize numerical values such as packet_size and session_duration
df['packet_size'] = df['packet_size_token'].astype(float)
df['session_duration'] = df['session_duration_token'].astype(float)

# Create a directed graph using NetworkX
G = nx.DiGraph()

# Add edges from tokenized data
for _, row in df.iterrows():
    G.add_edge(row['source_ip_token'], row['destination_ip_token'],  # Use integer-encoded tokens as nodes
               protocol=row['protocol_token'],
               packet_size=row['packet_size'],
               flow_direction=row['flow_direction_token'],
               session_duration=row['session_duration'])

# Extract node and edge data for visualization
edges = G.edges(data=True)
nodes = G.nodes()

# Prepare data for Plotly
edge_x = []
edge_y = []
edge_text = []

for edge in edges:
    start, end, data = edge
    x0, y0 = start % 10, start // 10  # Simple layout calculation
    x1, y1 = end % 10, end // 10  # Simple layout calculation
    edge_x.append(x0)
    edge_x.append(x1)
    edge_x.append(None)  # Separate lines
    edge_y.append(y0)
    edge_y.append(y1)
    edge_y.append(None)  # Separate lines
    edge_text.append(f"Protocol: {data['protocol']}, Packet Size: {data['packet_size']}")

# Prepare node positions
node_x = []
node_y = []
node_text = []

for node in nodes:
    x = node % 10  # Simple layout calculation
    y = node // 10  # Simple layout calculation
    node_x.append(x)
    node_y.append(y)
    node_text.append(f"Node: {node}")

# Create Plotly figure
fig = go.Figure()

# Add edges
fig.add_trace(go.Scatter(
    x=edge_x, y=edge_y,
    mode='lines',
    line=dict(width=0.5, color='gray'),
    hoverinfo='text',
    text=edge_text,
    name='Edges'
))

# Add nodes
fig.add_trace(go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    marker=dict(size=10, color='lightblue'),
    text=node_text,
    textposition="bottom center",
    hoverinfo='text',
    name='Nodes'
))

# Update layout
fig.update_layout(
    title="Network Traffic Graph",
    xaxis_title="X",
    yaxis_title="Y",
    showlegend=False,
    template='plotly_white',
)

# Save the plot as an HTML file
output_html = 'network_traffic_graph.html'
fig.write_html(output_html)

print(f"Plot saved as {output_html}")
