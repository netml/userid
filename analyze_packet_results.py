import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load the data from the CSV file
df = pd.read_csv('network_traffic.csv')

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

###

# Create histogram with KDE
ax = sns.histplot(df['packet_size'], bins=30, kde=True)

# Get the x and y values for the KDE line
kde_x = np.linspace(df['packet_size'].min(), df['packet_size'].max(), 100)
kde_y = sns.kdeplot(df['packet_size'], bw_adjust=1).get_lines()[0].get_ydata()

# Annotate the KDE line with frequency values
for i in range(0, len(kde_x), 5):  # Adjust step (5) to control the number of annotations
    plt.annotate(f'{kde_y[i]:.2f}', xy=(kde_x[i], kde_y[i]), xytext=(0, 5),
                 textcoords='offset points', ha='center', fontsize=8, color='blue')

plt.title('Packet Size Distribution with Frequency Annotations')
plt.xlabel('Packet Size (bytes)')
plt.ylabel('Frequency')
plt.show()



###


# Scatter plot of flow duration vs. packet size
plt.figure(figsize=(10, 6))
sns.scatterplot(x='flow_duration', y='packet_size', hue='protocol', data=df)
plt.title('Flow Duration vs. Packet Size')
plt.xlabel('Flow Duration (seconds)')
plt.ylabel('Packet Size (bytes)')
plt.show()

# Count traffic per country
country_counts = df['country'].value_counts()

# Plot the distribution of traffic by country
plt.figure(figsize=(12, 8))
sns.barplot(x=country_counts.index, y=country_counts.values)
plt.title('Traffic Distribution by Country')
plt.xlabel('Country')
plt.ylabel('Traffic Count')
plt.xticks(rotation=45)
plt.show()

# Calculate mean packet size by protocol
mean_packet_size = df.groupby('protocol')['packet_size'].mean()

# Plot the mean packet size by protocol
plt.figure(figsize=(10, 6))
sns.barplot(x=mean_packet_size.index, y=mean_packet_size.values)
plt.title('Mean Packet Size by Protocol')
plt.xlabel('Protocol')
plt.ylabel('Mean Packet Size (bytes)')
plt.show()
