import os
import socket
import pandas as pd
import plotly.graph_objects as go

# Define the domain resolution function
def get_domain(ip):
    try:
        domain = socket.gethostbyaddr(ip)[0]
    except socket.herror:
        domain = "Unknown"
    return domain

# Load your CSV data into a DataFrame
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
csv_path = os.path.join(root_dir, 'network_traffic.csv')
df = pd.read_csv(csv_path)

# Apply the function to resolve IPs to domains
df['source_domain'] = df['source_ip'].apply(get_domain)
df['destination_domain'] = df['destination_ip'].apply(get_domain)

# Filter data by flow direction
inbound_df = df[df['flow_direction'] == 'inbound']
outbound_df = df[df['flow_direction'] == 'outbound']

def create_sankey(df, flow_direction):
    # Create node labels with detailed info
    source_nodes = df['source_domain'].unique()
    destination_nodes = df['destination_domain'].unique()
    protocol_nodes = df['protocol'].unique()

    nodes = list(source_nodes) + list(destination_nodes) + list(protocol_nodes)
    node_indices = {node: idx for idx, node in enumerate(nodes)}

    # Create link data for Sankey diagram
    links = []
    link_labels = []
    for _, row in df.iterrows():
        source_idx = node_indices[row['source_domain']]
        destination_idx = node_indices[row['destination_domain']]
        protocol_idx = node_indices[row['protocol']]

        # Add connections based on session data
        links.append({'source': source_idx, 'target': protocol_idx, 'value': row['session_duration'], 'count': row['session_count']})
        links.append({'source': protocol_idx, 'target': destination_idx, 'value': row['session_duration'], 'count': row['session_count']})

        # Create hover text for links
        link_labels.append(
            f"Source IP: {row['source_ip']}<br>"
            f"Source Domain: {row['source_domain']}<br>"
            f"Destination IP: {row['destination_ip']}<br>"
            f"Destination Domain: {row['destination_domain']}<br>"
            f"Protocol: {row['protocol']}<br>"
            f"Session Duration: {row['session_duration']}<br>"
            f"Session Count: {row['session_count']}"
        )
        # link_labels.append(
        #     f"Source IP: {row['source_ip']}<br>Source Domain: {row['source_domain']}<br>Destination IP: {row['destination_ip']}<br>Destination Domain: {row['destination_domain']}<br>Protocol: {row['protocol']}<br>Duration: {row['session_duration']}")

    # Detailed node labels for hover
    node_labels = []
    for node in nodes:
        if node in source_nodes:
            ip = df[df['source_domain'] == node]['source_ip'].iloc[0]
            node_labels.append(f"{node}<br>IP: {ip}")
        elif node in destination_nodes:
            ip = df[df['destination_domain'] == node]['destination_ip'].iloc[0]
            node_labels.append(f"{node}<br>IP: {ip}")
        else:
            node_labels.append(node)

    # Create Sankey diagram
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='black', width=0.5),
            label=node_labels,
            hovertemplate="%{label}<extra></extra>",  # Custom hover template for nodes
            align='left'
        ),
        link=dict(
            source=[link['source'] for link in links],
            target=[link['target'] for link in links],
            value=[link['value'] for link in links],
            customdata=[link['count'] for link in links],
            color=['rgba(255, 0, 0, 0.4)' if i % 2 == 0 else 'rgba(0, 0, 255, 0.4)' for i in range(len(links))],
            hovertemplate=(
                "Source Domain: %{source.label}<br>"
                "Target Domain: %{target.label}<br>"
                "Session Count: %{customdata:.0f} times<br>"
                "Session Duration: %{value:.0f} seconds<br>"  # Flow duration is represented by the 'value' property
                "<extra></extra>"
            )
        )
    ))

    fig.update_layout(title_text=f"Sankey Diagram of {flow_direction.capitalize()} Flow", font_size=10)
    return fig

# Create Sankey diagrams for session data
inbound_sankey = create_sankey(inbound_df, 'inbound')
outbound_sankey = create_sankey(outbound_df, 'outbound')

# Combine all plots into a single HTML file
with open("session_analysis_sankey.html", 'w') as f:
    f.write('<html><head><title>Session Analysis Sankey Diagrams</title></head><body>')
    f.write(inbound_sankey.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write(outbound_sankey.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write('</body></html>')

# Show the plots
inbound_sankey.show()
outbound_sankey.show()