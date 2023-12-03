import argparse
import subprocess
import platform

def update_network_config_linux(interface, ip_address, service_port, netmask, broadcast):
    # Exécuter les commandes pour mettre à jour les configurations réseau sur Linux
    commands = [
        ['ifconfig', interface, 'inet', ip_address, 'netmask', netmask],
        ['route', 'add', 'default', 'gw', broadcast],
        # Ajouter d'autres commandes pour mettre à jour les autres configurations réseau
    ]
    for command in commands:
        subprocess.call(command)

def update_network_config_windows(interface, ip_address, service_port, netmask, broadcast):
    # Exécuter les commandes pour mettre à jour les configurations réseau sur Windows
    commands = [
        ['netsh', 'interface', 'ip', 'set', 'address', 'name=', interface, 'source=static', 'addr=', ip_address],
        ['netsh', 'interface', 'ip', 'set', 'address', 'name=', interface, 'mask=', netmask],
        # Ajouter d'autres commandes pour mettre à jour les autres configurations réseau
    ]
    for command in commands:
        subprocess.call(command)

def update_network_config(interface, ip_address, service_port, netmask, broadcast):
    system = platform.system()
    if system == 'Linux':
        update_network_config_linux(interface, ip_address, service_port, netmask, broadcast)
    elif system == 'Windows':
        update_network_config_windows(interface, ip_address, service_port, netmask, broadcast)
    else:
        print('Système d\'exploitation non pris en charge')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--interface', help='Interface réseau')
    parser.add_argument('--ip-address', help='Adresse IP')
    parser.add_argument('--service-port', help='Port du service')
    parser.add_argument('--netmask', help='Masque de sous-réseau')
    parser.add_argument('--broadcast', help='Adresse de diffusion')
    args = parser.parse_args()
    
    update_network_config(args.interface, args.ip_address, args.service_port, args.netmask, args.broadcast)


