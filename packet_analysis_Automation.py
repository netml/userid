import csv
import time
from ipaddress import ip_address, ip_network
import requests
from scapy.all import sniff
from scapy.layers.inet import IP, TCP, UDP
from collections import defaultdict
import numpy as np
import math
import socket
import os

# Function to get geolocation data
def get_geolocation(ip_address):
    try:
        response = requests.get(f'https://ipinfo.io/{ip_address}/json')
        data = response.json()
        return data.get('country', 'Unknown'), data.get('region', 'Unknown'), data.get('city', 'Unknown')
    except:
        return 'Unknown', 'Unknown', 'Unknown'


# Dictionary to store flow data
flow_data = {}

# Dictionary to store session data
session_data = defaultdict(lambda: {"packets": [], "start_time": None, "end_time": None})

# Network range
network = ip_network('192.168.1.0/24')

# CSV file fields
csv_fields = [
    'source_ip', 'destination_ip', 'source_port', 'destination_port',
    'protocol', 'packet_size', 'inter_arrival_time', 'payload_size', 'flow_duration',
    'total_packets', 'total_bytes', 'flow_direction', 'session_duration',
    'session_count', 'mean_packet_size', 'variance_packet_size', 'entropy',
    'access_patterns', 'usage_frequency', 'temporal_patterns',
    'country', 'region', 'city', 'application_data', 'behavioral_pattern', 'network_context'
]

# Create new CSV file every 15 minutes
def create_csv_writer():
    timestamp = time.strftime('%Y%m%d_%H%M')
    
    # Path to Downloads folder
    save_folder = os.path.join(os.path.expanduser('~'), 'Downloads')

    # Create the folder if it doesn't exist
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Generate the CSV filename with the Downloads folder path
    csv_filename = os.path.join(save_folder, f'network_traffic_{timestamp}.csv')
    
    # Open file
    file = open(csv_filename, mode='w', newline='')
    writer = csv.writer(file)
    writer.writerow(csv_fields)  # Write header row
    return file, writer

# Calculate entropy of packet sizes
def calculate_entropy(packet_sizes):
    packet_count = len(packet_sizes)
    if packet_count == 0:
        return 0
    size_counts = defaultdict(int)
    for size in packet_sizes:
        size_counts[size] += 1
    entropy = -sum((count / packet_count) * math.log2(count / packet_count) for count in size_counts.values())
    return entropy

# Determine the protocol of the packet
def get_protocol(packet):
    if packet.haslayer(TCP):
        return 'TCP'
    elif packet.haslayer(UDP):
        return 'UDP'
    else:
        return 'Other'

# Get the domain name from an IP address
def get_domain(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return None

# Determine the flow direction based on IP addresses
def determine_flow_direction(src_ip, dst_ip):
    src_ip_addr = ip_address(src_ip)
    dst_ip_addr = ip_address(dst_ip)

    if src_ip_addr in network:
        return "outbound" if dst_ip_addr not in network else "internal"
    else:
        return "inbound" if dst_ip_addr in network else "external"


# Packet callback function
def packet_callback(packet, writer):
    if packet.haslayer(IP):
        ip_layer = packet[IP]
        protocol = get_protocol(packet)

        # Initialize source and destination ports
        src_port = dst_port = None

        # Check for TCP or UDP layer
        if protocol == 'TCP' and packet.haslayer(TCP):
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
        elif protocol == 'UDP' and packet.haslayer(UDP):
            src_port = packet[UDP].sport
            dst_port = packet[UDP].dport

        # If ports are not available, skip processing
        if src_port is None or dst_port is None:
            return

        flow_key = (ip_layer.src, ip_layer.dst, src_port, dst_port)
        current_time = time.time()

        if flow_key not in flow_data:
            flow_data[flow_key] = {
                "start_time": current_time,
                "packet_count": 0,
                "byte_count": 0,
                "last_time": current_time,
                "packet_sizes": [],
                "inter_arrival_times": []
            }

        # Calculate inter-arrival time
        inter_arrival_time = current_time - flow_data[flow_key]["last_time"]
        flow_data[flow_key]["inter_arrival_times"].append(inter_arrival_time)

        flow_data[flow_key]["packet_count"] += 1
        flow_data[flow_key]["byte_count"] += len(packet)
        flow_data[flow_key]["last_time"] = current_time
        flow_data[flow_key]["packet_sizes"].append(len(packet))

        # Update session data
        if flow_key not in session_data or session_data[flow_key]["end_time"] is None:
            session_data[flow_key]["start_time"] = current_time
            session_data[flow_key]["end_time"] = current_time

        session_data[flow_key]["packets"].append(len(packet))
        session_data[flow_key]["end_time"] = current_time

        # Calculate additional metrics
        mean_packet_size = np.mean(flow_data[flow_key]["packet_sizes"])
        variance_packet_size = np.var(flow_data[flow_key]["packet_sizes"])
        entropy = calculate_entropy(flow_data[flow_key]["packet_sizes"])

        # Flow direction
        flow_direction = determine_flow_direction(ip_layer.src, ip_layer.dst)

        # Session metrics
        session_duration = session_data[flow_key]["end_time"] - session_data[flow_key]["start_time"]
        session_count = len(session_data[flow_key]["packets"])
        access_patterns = f"{ip_layer.src}->{ip_layer.dst}:{dst_port}"
        usage_frequency = flow_data[flow_key]["packet_count"] / session_duration if session_duration > 0 else 0

        # Get geolocation data
        country, region, city = get_geolocation(ip_layer.dst)

        # Dummy application-level data and behavioral analytics
        application_data = 'Unknown'  # Placeholder for actual application data
        behavioral_pattern = 'Normal'  # Placeholder for actual behavior pattern analysis
        network_context = 'Normal'  # Placeholder for network context analysis

        # Prepare row data for CSV
        row = [
            ip_layer.src,
            ip_layer.dst,
            src_port,
            dst_port,
            protocol,
            len(packet),
            inter_arrival_time,
            len(packet.payload),
            flow_data[flow_key]['last_time'] - flow_data[flow_key]['start_time'],
            flow_data[flow_key]['packet_count'],
            flow_data[flow_key]['byte_count'],
            flow_direction,
            session_duration,
            session_count,
            mean_packet_size,
            variance_packet_size,
            entropy,
            access_patterns,
            usage_frequency,
            time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(current_time)),
            country,
            region,
            city,
            application_data,
            behavioral_pattern,
            network_context
        ]

        # Write row data to CSV
        writer.writerow(row)


# Main function to handle CSV file creation and sniffing
def main():
    file, writer = create_csv_writer()
    start_time = time.time()

    while True:
        sniff(prn=lambda x: packet_callback(x, writer), store=False, timeout=60)  # Capture for 1 minute

        # Check if 15 minutes have passed
        if time.time() - start_time >= 900:  # 900 seconds = 15 minutes
            file.close()  # Close the current file
            file, writer = create_csv_writer()  # Create a new CSV file
            start_time = time.time()  # Reset the start time

if __name__ == "__main__":
    main()