# Router Management CLI Tool

A Python-based command-line tool to manage router settings including MAC filtering, restarts, and session management.

## Features
- **Router Restart**: Remotely restart the router
- **MAC Filter Management**:
  - List all whitelisted MAC addresses
  - Add new MAC addresses to the whitelist
  - Delete existing MAC addresses from the whitelist
- **Session Control**: Explicit logout capability
- **TLS 1.0 Support**: For compatibility with older router firmware
- **Custom SSL Handling**: Bypasses certificate verification for devices with self-signed certificates

## Prerequisites
- Python 3.6+
- Required packages: `requests`, `urllib3`

## Usage

### Basic Syntax
```bash
python router_tool.py [global_options] <command> [command_options]
```

## Available Commands

1.  **Restart Router**

    **bash**

    ```bash
    python router_tool.py -router -ip 192.168.1.1 --username admin -password admin restart
    ```

2.  **List MAC Addresses**

    **bash**

    ```bash
    python router_tool.py -router -ip 192.168.1.1 username admin -password admin list -macs
    ```

3.  **Add MAC Address**

    **bash**

    ```bash
    python router_tool.py -router -ip 192.168.1.1 --username admin -password admin \
    add-mac -name " Device Name " mac " 00 : 11 : 22 : 33 : 44 : 55 " -ssid 1
    ```

4.  **Delete MAC Address**

    **bash**

    ```bash
    # Delete by MAC address
    python router_tool.py --router-ip 192.168.1.1 --username admin --password admin \
      delete-mac --mac "00:11:22:33:44:55" --ssid 1

    # Delete by name
    python router_tool.py --router-ip 192.168.1.1 --username admin --password admin \
      delete-mac --name "Device Name" --ssid 1
    ```

5.  **Logout Session**

    **bash**

    ```bash
    python router_tool.py --router-ip 192.168.1.1 --username admin --password admin logout
    ```