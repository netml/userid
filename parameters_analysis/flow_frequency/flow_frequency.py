import os
import pandas as pd
import socket
import matplotlib.pyplot as plt
import seaborn as sns

# Load your network traffic data
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
csv_path = os.path.join(root_dir, 'network_traffic.csv')
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

# Plot frequency of Source Domains
plt.figure(figsize=(14, 8))
sns.countplot(y='source_domain', data=df, order=df['source_domain'].value_counts().index, palette='viridis')
plt.title('Frequency of Source Domains', fontsize=16)
plt.xlabel('Count', fontsize=14)
plt.ylabel('Source Domain', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()  # Adjusts plot to fit labels
plt.show()

# Plot frequency of Destination Domains
plt.figure(figsize=(14, 8))
sns.countplot(y='destination_domain', data=df, order=df['destination_domain'].value_counts().index, palette='viridis')
plt.title('Frequency of Destination Domains', fontsize=16)
plt.xlabel('Count', fontsize=14)
plt.ylabel('Destination Domain', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()  # Adjusts plot to fit labels
plt.show()

# Plot frequency of Source IP Addresses
plt.figure(figsize=(14, 8))
sns.countplot(y='source_ip', data=df, order=df['source_ip'].value_counts().index, palette='viridis')
plt.title('Frequency of Source IP Addresses', fontsize=16)
plt.xlabel('Count', fontsize=14)
plt.ylabel('Source IP', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()  # Adjusts plot to fit labels
plt.show()

# Plot frequency of Destination IP Addresses
plt.figure(figsize=(14, 8))
sns.countplot(y='destination_ip', data=df, order=df['destination_ip'].value_counts().index, palette='viridis')
plt.title('Frequency of Destination IP Addresses', fontsize=16)
plt.xlabel('Count', fontsize=14)
plt.ylabel('Destination IP', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()  # Adjusts plot to fit labels
plt.show()

# Create a pivot table for the heatmap
heatmap_data = df.pivot_table(index='source_domain', columns='destination_domain', aggfunc='size', fill_value=0)

plt.figure(figsize=(14, 10))
sns.heatmap(heatmap_data, cmap='YlGnBu', annot=True, fmt='d', annot_kws={"size": 8})
plt.title('Traffic Heatmap: Source Domain vs. Destination Domain', fontsize=16)
plt.xlabel('Destination Domain', fontsize=14)
plt.ylabel('Source Domain', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()  # Adjusts plot to fit labels
plt.show()
