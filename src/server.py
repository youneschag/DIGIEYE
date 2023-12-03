import os
import struct
import subprocess
import time
import netifaces
import socket
import json
import platform
import threading
import ipaddress

def get_local_ip_address():
    interfaces = netifaces.interfaces()

    for interface in interfaces:
        addresses = netifaces.ifaddresses(interface)
        ipv4_info = addresses.get(netifaces.AF_INET)

        if ipv4_info:
            ip_address = ipv4_info[0]['addr']
            if ip_address.startswith('192.168.'):
                return ip_address

    return None

# Utilisez la fonction pour obtenir l'adresse IP locale
local_ip_address = get_local_ip_address()
print(f"Adresse IP locale : {local_ip_address}")

def extract_value(line):
    return line.strip().split(' ')[-1]

def detect_network_services():
    services = []
    interfaces = netifaces.interfaces()
    
    ifconfig_output = subprocess.check_output(['ifconfig']).decode('utf-8')

    for interface in interfaces:
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            ipv4_info = addresses[netifaces.AF_INET][0]
            ip_address = ipv4_info['addr']
            netmask = ipv4_info['netmask']
            broadcast = ipv4_info.get('broadcast', 'N/A')
            
            service_name = socket.getservbyport(socket.SOCK_STREAM)
            service_port = socket.getservbyname(service_name)
            
            if netifaces.AF_LINK in addresses:
                mac_info = addresses[netifaces.AF_LINK][0]
                mac_address = mac_info.get('addr', 'N/A')
            else:
                mac_address = 'N/A'
            ipv6_address = addresses.get(netifaces.AF_INET6, [{'addr': 'N/A'}])[0]['addr']
            
            system_info = platform.uname()
            device_type = system_info.system
            software_version = platform.release()
            
            status = 'N/A'
            http_port = 'N/A'
            device_trial_no = 'N/A'
            
            lines = ifconfig_output.split('\n')
            for line in lines:
                if 'status:' in line:
                    status = extract_value(line)
                elif 'http_port:' in line:
                    http_port = int(extract_value(line))
                elif 'device_trial_no:' in line:
                    device_trial_no = int(extract_value(line))

            if not device_trial_no:
                device_trial_no = 'N/A'
                
            service = {
                'Interface': interface,
                'IP Address': ip_address,
                'Netmask': netmask,
                'Broadcast': broadcast,
                'Service Name': service_name,
                'Service Port': service_port,
                'Mac Address': mac_address,
                'IPv6 Address': ipv6_address,
                'Device Type': device_type,
                'Status': status,
                'Software Version': software_version,
                'HTTP Port': http_port,
                'Device Trial No': device_trial_no
            }
            services.append(service)
    
    return services

def send_services_via_unicast(services, target_ip):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(1)  # Temps d'attente pour la connexion
    
    try:
        # Utilisez le port 3784 pour la communication unicast
        client_socket.connect((target_ip, 3784))
        client_socket.sendall(json.dumps(services).encode())
        client_socket.close()
        print(f'Sent unicast services to {target_ip}:{3784}', services)
    except (socket.timeout, ConnectionRefusedError):
        pass

def save_services_to_file(services):
    # Enregistrer les services dans un fichier JSON
    with open('server_services.json', 'w') as file:
        json.dump(services, file)

def apply_network_configuration(interface, ip_address, netmask, broadcast):
    if platform.system() == 'Linux':
        current_ipv4_info = netifaces.ifaddresses(interface).get(netifaces.AF_INET)
        if current_ipv4_info is None or (current_ipv4_info[0]['addr'] != ip_address or current_ipv4_info[0]['netmask'] != netmask):
            subprocess.run(["ip", "addr", "add", ip_address, "dev", interface])
            subprocess.run(["ip", "addr", "add", netmask, "dev", interface])

        if broadcast and broadcast != '255.255.255.255':
            current_broadcast = current_ipv4_info[0].get('broadcast', '')
            if current_broadcast != broadcast:
                subprocess.run(["ip", "addr", "add", broadcast, "dev", interface])
    elif platform.system() == 'Darwin':
        # Configuration IP sur macOS (Darwin)
        os.system(f"ifconfig {interface} {ip_address} netmask {netmask}")

        # Configuration broadcast (si disponible) sur macOS (Darwin)
        if broadcast and broadcast != '255.255.255.255':
            os.system(f"ifconfig {interface} broadcast {broadcast}")
    elif platform.system() == 'Windows':
        # Configuration IP sur Windows
        subprocess.run(["netsh", "interface", "ipv4", "set", "address", f"name={interface}", f"static {ip_address} {netmask}"])

        # Configuration broadcast (si disponible) sur Windows
        if broadcast:
            subprocess.run(["netsh", "interface", "ipv4", "set", "address", f"name={interface}", f"static {broadcast}"])
    else:
        print("Système d'exploitation non pris en charge. Les configurations ne seront pas appliquées.")


def main():
    multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    multicast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    multicast_socket.bind(('0.0.0.0', 3785))
    multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton('224.0.0.2') + socket.inet_aton(local_ip_address))
    
    def multicast_listener():
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_socket.bind(('0.0.0.0', 3784))
        mreq = struct.pack('4sl', socket.inet_aton('224.0.0.2'), socket.INADDR_ANY)
        listen_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        while True:
            try:
                data, addr = listen_socket.recvfrom(4096)
                client_ip = json.loads(data.decode())['clientIp']
                print(f'Received multicast client IP: {client_ip}')
            
                services = detect_network_services()
                # Envoyer les services au client en unicast
                send_services_via_unicast(services, client_ip)    
            
                data, addr = multicast_socket.recvfrom(4096)
                client_services = json.loads(data.decode())
                print('Received multicast services from client:', client_services)
             
                # Traiter les services reçus en multicast
                updated_services = []
                # Traiter les services reçus en multicast
                for received_service in client_services:
                    interface = received_service['Interface']
                    if interface in netifaces.interfaces():
                        if netifaces.AF_INET in netifaces.ifaddresses(interface):
                            current_ipv4_info = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]
                            if received_service['IP Address'] != current_ipv4_info['addr']:
                                original_broadcast = current_ipv4_info.get('broadcast', '')
                                # Supprimer l'adresse IP existante
                                subprocess.run(["ip", "addr", "del", f"{current_ipv4_info['addr']}/{current_ipv4_info['netmask']}", "dev", interface])
    
                                # Ajouter la nouvelle adresse IP
                                subprocess.run(["ip", "addr", "add", f"{received_service['IP Address']}/{current_ipv4_info['netmask']}", "dev", interface])
                                print(f"Updated IP Address for {interface} to {received_service['IP Address']}")

                                if original_broadcast:
                                    subprocess.run(["ip", "addr", "add", f"{original_broadcast}", "dev", interface])
                                    print(f"Restored original Broadcast for {interface} to {original_broadcast}")
                                    
                            if received_service['Netmask'] != current_ipv4_info['netmask']:
                                # Supprimer l'adresse de diffusion existante (si disponible)
                                if 'broadcast' in current_ipv4_info:
                                    subprocess.run(["ip", "addr", "del", f"{current_ipv4_info['broadcast']}", "dev", interface])
    
                                    # Ajouter le nouveau masque de sous-réseau
                                    subprocess.run(["ip", "addr", "add", f"{received_service['Netmask']}", "dev", interface])
                                    print(f"Updated Netmask for {interface} to {received_service['Netmask']}")

                                if received_service['Broadcast'] != current_ipv4_info.get('broadcast', ''):
                                    # Supprimer l'adresse de diffusion existante (si disponible)
                                    if current_ipv4_info.get('broadcast'):
                                        subprocess.run(["ip", "addr", "del", f"{current_ipv4_info['broadcast']}", "dev", interface])
    
                                        # Ajouter la nouvelle adresse de diffusion
                                        subprocess.run(["ip", "addr", "add", f"{received_service['Broadcast']}", "dev", interface])
                                        print(f"Updated Broadcast for {interface} to {received_service['Broadcast']}")
     
                    updated_services.append(received_service)
            
                save_services_to_file(updated_services)
                # Envoyer les services mis à jour au client
                updated_services_data = json.dumps(updated_services).encode()
                multicast_socket.sendto(updated_services_data, addr)
            
            except Exception as e:
                print("An error occurred:", e)
            
    multicast_thread = threading.Thread(target=multicast_listener)
    multicast_thread.start()
        
password = os.environ.get('password')
detected_services = detect_network_services()
print(detected_services)

if __name__ == "__main__":
    threading.Thread(target=main).start()
    print("Waiting for multicast client to be ready...")
    time.sleep(2)  # Attendre 2 secondes pour la préparation du socket multicast




