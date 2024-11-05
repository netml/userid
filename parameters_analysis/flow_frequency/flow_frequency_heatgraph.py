import os
import pandas as pd
import socket
import matplotlib.pyplot as plt
import seaborn as sns

# Load your network traffic data
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
csv_path = os.path.join(root_dir , 'network_traffic.csv')
df = pd.read_csv(csv_path)

def get_domain(ip):
    try:
        domain = socket.gethostbyaddr(ip)[0]
    except socket.herror:
        domain = "Unknown"
    return domain

# Apply this function to your dataframe
df['source_domain'] = df['source_ip'].apply(get_domain)
df['destination_domain'] = df['destination_ip'].apply(get_domain)

# Create combined labels with IPs in brackets
df['source_label'] = df.apply(lambda row: f"{row['source_domain']} ({row['source_ip']})", axis=1)
df['destination_label'] = df.apply(lambda row: f"{row['destination_domain']} ({row['destination_ip']})", axis=1)


heatmap_data = df.pivot_table(index='source_label', columns='destination_label', aggfunc='size', fill_value=0)

# Plot the heatmap
plt.figure(figsize=(14, 10))
sns.heatmap(heatmap_data, cmap='YlGnBu', annot=True, fmt='d', annot_kws={"size": 8})
plt.title('Traffic Heatmap: Source Domain (IP) vs. Destination Domain (IP)', fontsize=16)
plt.xlabel('Destination Domain (IP)', fontsize=14)
plt.ylabel('Source Domain (IP)', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()  # Adjusts plot to fit labels
plt.show()
