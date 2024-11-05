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

# network range
network = ip_network('192.168.1.0/24')

# CSV file setup
csv_file = 'network_traffic.csv'
csv_fields = [
    'source_ip', 'destination_ip', 'source_port', 'destination_port',
    'protocol', 'packet_size', 'inter_arrival_time', 'payload_size', 'flow_duration',
    'total_packets', 'total_bytes', 'flow_direction', 'session_duration',
    'session_count', 'mean_packet_size', 'variance_packet_size', 'entropy',
    'access_patterns', 'usage_frequency', 'temporal_patterns',
    'country', 'region', 'city', 'application_data', 'behavioral_pattern', 'network_context'
]

# Open CSV file for writing
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(csv_fields)  # Write header row


    def calculate_entropy(packet_sizes):
        """
        Calculate the entropy of a list of packet sizes.
        """
        packet_count = len(packet_sizes)
        if packet_count == 0:
            return 0
        size_counts = defaultdict(int)
        for size in packet_sizes:
            size_counts[size] += 1
        entropy = -sum((count / packet_count) * math.log2(count / packet_count) for count in size_counts.values())
        return entropy


    def get_protocol(packet):
        """
        Determine the protocol of the packet.
        """
        if packet.haslayer(TCP):
            return 'TCP'
        elif packet.haslayer(UDP):
            return 'UDP'
        else:
            return 'Other'


    def get_domain(ip):
        try:
            return socket.gethostbyaddr(ip)[0]
        except socket.herror:
            return None

    def determine_flow_direction(src_ip, dst_ip):
        src_ip_addr = ip_address(src_ip)
        dst_ip_addr = ip_address(dst_ip)

        if src_ip_addr in network:
            return "outbound" if dst_ip_addr not in network else "internal"
        else:
            return "inbound" if dst_ip_addr in network else "external"


    def packet_callback(packet):
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

            # Print packet details (optional)
            print(f"Flow: {flow_key}")
            print(f"IP Source Domain: {get_domain(ip_layer.src)}")
            print(f"IP Source Destination: {get_domain(ip_layer.dst)}")
            print(f"Protocol: {protocol}")
            print(f"Packet Size: {len(packet)} bytes")
            print(f"Inter-Arrival Time: {inter_arrival_time} seconds")
            print(f"Payload Size: {len(packet.payload)} bytes")
            print(f"Total Packets: {flow_data[flow_key]['packet_count']}")
            print(f"Total Bytes: {flow_data[flow_key]['byte_count']} bytes")
            print(f"Flow Duration: {flow_data[flow_key]['last_time'] - flow_data[flow_key]['start_time']} seconds")
            print(f"Session Duration: {session_duration} seconds")
            print(f"Mean Packet Size: {mean_packet_size} bytes")
            print(f"Variance of Packet Size: {variance_packet_size}")
            print(f"Entropy: {entropy}")
            print(f"Flow Direction: {flow_direction}")
            print(f"Access Patterns: {access_patterns}")
            print(f"Usage Frequency: {usage_frequency} packets/second")
            print(f"Geolocation: {country}, {region}, {city}")
            print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(current_time))}\n")


    # Start sniffing
    sniff(prn=packet_callback, store=False)
