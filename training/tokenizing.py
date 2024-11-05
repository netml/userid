import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Load CSV
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
csv_path = os.path.join(root_dir + '/humanbehaviour', 'network_traffic.csv')
df = pd.read_csv(csv_path)

# Initialize a LabelEncoder for categorical fields
label_enc = LabelEncoder()

# Apply label encoding to categorical fields
df['protocol'] = label_enc.fit_transform(df['protocol'])
df['flow_direction'] = label_enc.fit_transform(df['flow_direction'])
df['country'] = label_enc.fit_transform(df['country'])
df['region'] = label_enc.fit_transform(df['region'])
df['city'] = label_enc.fit_transform(df['city'])

# Normalize numeric fields (optional)
df['packet_size'] = df['packet_size'] / df['packet_size'].max()

# Create tokenized columns
df['source_ip_token'] = df['source_ip']
df['destination_ip_token'] = df['destination_ip']
df['protocol_token'] = df['protocol']
df['packet_size_token'] = df['packet_size']
df['flow_direction_token'] = df['flow_direction']
df['session_duration_token'] = df['session_duration']

# Save tokenized data for LLM input with columns
tokenized_df = df[['source_ip_token', 'destination_ip_token', 'protocol_token',
                   'packet_size_token', 'flow_direction_token', 'session_duration_token']]

# Save to CSV in a structured way
output_path = os.path.join(root_dir + '/humanbehaviour', 'tokenized_data.csv')
tokenized_df.to_csv(output_path, index=False)

print(f"Tokenized data saved to {output_path}")
