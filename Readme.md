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