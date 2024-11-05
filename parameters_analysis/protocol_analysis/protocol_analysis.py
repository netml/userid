import os
import socket

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Load the data from the CSV file
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
csv_path = os.path.join(root_dir, 'network_traffic.csv')
df = pd.read_csv(csv_path)

# Display basic statistics about the dataset
print(df.describe())

# Check for missing values
print(df.isnull().sum())

# Display unique protocols
print("Unique Protocols:", df['protocol'].unique())

# Set the style of the visualizations
sns.set(style="whitegrid")

# Plot the distribution of protocols
plt.figure(figsize=(10, 6))
sns.countplot(x='protocol', data=df)
plt.title('Protocol Distribution')
plt.xlabel('Protocol')
plt.ylabel('Count')
plt.show()


## ---------------------------------  HeatMap ----------------------- ###

# Step 2: Prepare the data
df_grouped = df.groupby(['source_ip', 'protocol', 'destination_ip']).size().reset_index(name='count')

# Step 3: Create a Sunburst chart
fig = px.sunburst(
    df_grouped,
    path=['source_ip', 'protocol', 'destination_ip'],  # Hierarchical path
    values='count',  # Size of each segment
    color='protocol',  # Color by protocol
    title="Network Traffic Visualization (Source IP → Protocol → Destination IP)"
)

# Step 4: Save as HTML
fig.write_html("network_traffic_sunburst.html")

# Display the figure
fig.show()


###### ------------ TreeMap ----------------------- ############

# Step 2: Define the function to get domain names
def get_domain(ip):
    try:
        domain = socket.gethostbyaddr(ip)[0]
    except socket.herror:
        domain = "Unknown"
    return domain

# Step 3: Replace IP addresses with domain names and include IP in brackets
df['source_ip'] = df['source_ip'].apply(lambda ip: f"{get_domain(ip)} ({ip})")
df['destination_ip'] = df['destination_ip'].apply(lambda ip: f"{get_domain(ip)} ({ip})")

# Step 4: Prepare the data
df_grouped = df.groupby(['source_ip', 'protocol', 'destination_ip']).size().reset_index(name='count')

# Step 5: Create a Treemap
fig = px.treemap(
    df_grouped,
    path=['source_ip', 'protocol', 'destination_ip'],  # Hierarchical path
    values='count',  # Size of each rectangle
    color='protocol',  # Color by protocol
    title="Network Traffic Visualization (Source Domain → Protocol → Destination Domain)"
)

# Step 6: Save as HTML
fig.write_html("network_traffic_treemap_with_dynamic_domains.html")

# Display the figure
fig.show()