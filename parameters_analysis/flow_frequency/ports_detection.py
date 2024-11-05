import os

import networkx as nx
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from pyvis.network import Network

# Load the network traffic data
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
csv_path = os.path.join(root_dir , 'network_traffic.csv')
df = pd.read_csv(csv_path)

# Plot histogram for Source Ports
plt.figure(figsize=(12, 6))
plt.hist(df['source_port'], bins=50, color='skyblue', edgecolor='black')
plt.title('Distribution of Source Ports')
plt.xlabel('Source Port')
plt.ylabel('Frequency')
plt.grid(True)
plt.show()

# Plot histogram for Destination Ports
plt.figure(figsize=(12, 6))
plt.hist(df['destination_port'], bins=50, color='salmon', edgecolor='black')
plt.title('Distribution of Destination Ports')
plt.xlabel('Destination Port')
plt.ylabel('Frequency')
plt.grid(True)
plt.show()

#### Heat Graph

# Create a matrix for the heatmap
port_matrix = pd.crosstab(index=df['source_port'], columns=df['destination_port'], values=df['source_ip'], aggfunc='count').fillna(0)

# Draw the heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(port_matrix, annot=False, cmap='YlGnBu')
plt.title('Source Port vs Destination Port Traffic')
plt.xlabel('Destination Port')
plt.ylabel('Source Port')
plt.show()

# Aggregate data to reduce complexity
# Group by Source IP and Destination IP, then aggregate ports
agg_df = df.groupby(['source_ip', 'destination_ip']).agg({
    'source_port': lambda x: ','.join(map(str, set(x))),
    'destination_port': lambda x: ','.join(map(str, set(x)))
}).reset_index()

# Create a directed graph
G = nx.DiGraph()

# Add edges to the graph with aggregated port information
for _, row in agg_df.iterrows():
    G.add_edge(row['source_ip'], row['destination_ip'],
               label=f"{row['source_port']}->{row['destination_port']}")

# Simplify the layout
pos = nx.spring_layout(G, k=0.15, iterations=20)

# Draw the graph with simpler design
plt.figure(figsize=(10, 8))
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1000, font_size=8, font_weight='bold', edge_color='gray')
edge_labels = nx.get_edge_attributes(G, 'label')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7, font_color='red')

plt.title('Simplified Network Traffic Visualization')
plt.show()

# Initialize a PyVis network
net = Network(notebook=True, height="750px", width="100%", bgcolor="#222222", font_color="white")

# Add nodes and edges
for _, row in agg_df.iterrows():
    net.add_node(row['source_ip'], label=row['source_ip'])
    net.add_node(row['destination_ip'], label=row['destination_ip'])
    net.add_edge(row['source_ip'], row['destination_ip'], title=f"{row['source_port']}->{row['destination_port']}")

# Generate the interactive visualization
net.show("network_traffic.html")