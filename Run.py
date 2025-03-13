import argparse
from typing import Dict
import requests
import time
import urllib3
import re
import hashlib
import xml.etree.ElementTree as ET
import ssl
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Solve the Probelm of The SSL Certification 
class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Use TLS version 1.0
        context.set_ciphers('DEFAULT:@SECLEVEL=1')  # Set ciphers to support TLS 1.0
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE  # Disable certificate verification
        kwargs['ssl_context'] = context
        # Define the retry strategy
        retries = Retry(
            total=5,  # Total number of retries
            backoff_factor=0.1,  # Backoff factor for retries
            status_forcelist=[500, 502, 503, 504]  # HTTP status codes to retry on
        )
        kwargs['retries'] = retries

        super(TLSAdapter, self).init_poolmanager(*args, **kwargs)


######## Data ##############
Mac_Addresses = {
    "dad-ph": "06:63:b1:8e:f3:bd",
}


cookies1 = {"_TESTCOOKIESUPPORT": "1"}
headers_1 = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.100 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Priority": "u=0, i",}

Router_Ip = '192.168.1.1'
USERNAME = 'admin'
PASSWORD = 'admin'
############ Helping Methods #############

def create_session() -> requests.Session:
    """Create a configured session with TLS adapter and verification disabled"""
    session = requests.Session()
    session.mount('https://', TLSAdapter())
    session.verify = False 
    return session

def timestamp_ms():
    # Get the current time in seconds since the epoch
    current_time_s = time.time()

    # Convert to milliseconds like : 1723825585255
    timestamp_ms = int(current_time_s * 1000)
    return timestamp_ms


def extract_xml_root_number(xml_string):
    pattern = rb"<ajax_response_xml_root>(\d+)</ajax_response_xml_root>"
    match = re.search(pattern, xml_string)
    if match:
        return match.group(1).decode("utf-8")
    return None


def extract__sessionTmpToken(Request):
    start = (
        Request.find('_sessionTmpToken = "') + 1
    )  # Find the index of the first quote and add 1
    end = Request.find(
        '";', start
    )  # Find the index of the second quote starting from 'start'
    line = Request[start:end]
    return line[line.find('"') + 1 :]




############################## Critical Functions ############################

def Login(Session: requests.Session) -> bool:
    """Perform login to router"""
    # Request 1 to get the solt that added to pass to be hashed
    try:
        response = Session.get(
            url=f"https://{Router_Ip}/function_module/login_module/login_page/logintoken_lua.lua?_={timestamp_ms()}",
            headers=headers_1,
            cookies=cookies1,
            verify=False,
        )

        the_hashed_Pass = hashlib.sha256(PASSWORD.encode("utf-8") + extract_xml_root_number(response.content).encode("utf-8")).hexdigest()

        response = Session.post(
            f"https://{Router_Ip}/",
            verify=False,
            cookies=cookies1,
            data={
                "Username": USERNAME,
                "Password": the_hashed_Pass,
                "Frm_Logintoken": "",
                "action": "login",
                "captchaCode": "",
            },
        )
        print("\n#### Login successful ####\n")
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"Login failed: {e}")
        return False


def logout(Session: requests.Session) -> None:
    """Perform logout"""
    try:
        response= Session.post(
        f"https://{Router_Ip}/",verify=False, data={"IF_LogOff": "1", "IF_LanguageSwitch": ""}
    )
        response.raise_for_status()

        print("Logout successful ")
    except requests.exceptions.RequestException as e:
        print(f"Logout failed: {e}")


def Restart(session: requests.Session) -> bool:
    try:
        ## Request 1
        response = session.get(
            f"https://{Router_Ip}/getpage.lua?pid=123&nextpage=ManagDiag_DeviceManag_t.lp&Menu3Location=0&_={timestamp_ms()}",verify=False
        )
        response.raise_for_status()

        _sessionTmpToken = extract__sessionTmpToken(response.text)
        ## Request 2
        response = session.post(
            f"https://{Router_Ip}/common_page/deviceManag_lua.lua",verify=False,
            data={
                "IF_ACTION": "Restart",
                "Btn_restart": "",
                "_sessionTOKEN": bytes(_sessionTmpToken, "utf-8").decode("unicode_escape"),
            },
        )
        response.raise_for_status()
        print("Restart command sent successfully")
        return True

    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Restart failed: {e}")
        return False



def get_All_Mac(session: requests.Session) -> list[Dict[str, str]]:
    """Retrieve MAC filter list"""
    try:
        ## Request 1 Wlan_Advanced ##### Must
        session.get(f"https://{Router_Ip}/getpage.lua?pid=123&nextpage=Localnet_WlanAdvanced_t.lp&Menu3Location=0&_={timestamp_ms()}",verify=False)

        ## Request 2  Wlan_Advanced -->>>>> Access Control-Rule Configuration ##### Must

        response = session.get(
            f"https://{Router_Ip}/common_page/Localnet_WlanAdvanced_MACFilterRule_lua.lua?_={timestamp_ms()}",verify=False
        )
        response.raise_for_status()

        # Your XML data
        def All_Mac(xml_data):
            # Parse the XML data
            root = ET.fromstring(xml_data)

            # Initialize a list to hold all instances
            two_dimensional_list = []

            # Iterate over each 'Instance' in the XML
            for instance in root.findall(".//Instance"):
                instance_data = []
                # Iterate over each child element in 'Instance'
                for i in range(
                    0, len(instance), 2
                ):  # Assuming each ParaName is followed by its ParaValue
                    para_name = instance[i].text
                    para_value = instance[i + 1].text
                    instance_data.append({para_name: para_value})
                two_dimensional_list.append(instance_data)
            return two_dimensional_list

        All_Macs = All_Mac(response.text)
        # two dimential list for all macs
        for i in All_Macs:
            print(i)
        return All_Macs
    except (ET.ParseError, requests.exceptions.RequestException) as e:
        print(f"Failed to retrieve MAC filters: {e}")
        return []



def add_Mac_to_the_whitelist(session, name=None, Mac=None, SSID=1):
    ## Request 1 Wlan_Advanced ## Must
    response = session.get(f"https://{Router_Ip}/getpage.lua?pid=123&nextpage=Localnet_WlanAdvanced_t.lp&Menu3Location=0&_{timestamp_ms()}",verify=False)
    _sessionTmpToken = extract__sessionTmpToken(response.text)
    # if name and Mac
    ## Request  Add ## Must
    print(f"Mac , name: {Mac} , {name}")
    response = session.post(
        f"https://{Router_Ip}/common_page/Localnet_WlanAdvanced_MACFilterRule_lua.lua",verify=False,
        data={
            "IF_ACTION": "Apply",
            "_InstID": "-1",
            "MACAddress": Mac,
            "Name": name,
            "Interface": f"DEV.WIFI.AP{SSID}",
            "Btn_cancel_MACFilterRule": "",
            "Btn_apply_MACFilterRule": "",
            "_sessionTOKEN": bytes(_sessionTmpToken, "utf-8").decode("unicode_escape"),
        },
    )

    return session


def delete_Mac_from_the_whitelist(session, all_Macs, name=None, Mac=None, SSID=1):
    ## Request 1 Wlan_Advanced ## Must
    response = session.get(
        f"https://{Router_Ip}/getpage.lua?pid=123&nextpage=Localnet_WlanAdvanced_t.lp&Menu3Location=0&_{timestamp_ms()}",verify=False
    )
    _sessionTmpToken = extract__sessionTmpToken(response.text)
    InstID, Name, mac  = None, None, None
    ## Request  Add ## Must
    # Find the matching item
    for item in all_Macs:
        for sub_item in item:
            if (name and sub_item.get("Name") == name) or (
                Mac and sub_item.get("MACAddress") == Mac
            ):
                InstID = item[0]["_InstID"]
                mac = item[1]["MACAddress"]
                Name = item[2]["Name"]
                print("Found")
                break
        if InstID:
            break

    if not InstID:
        print("Not Found")
        return session

    response = session.post(
        f"https://{Router_Ip}/common_page/Localnet_WlanAdvanced_MACFilterRule_lua.lua",verify=False,
        data={
            "IF_ACTION": "Delete",
            "_InstID": InstID,
            "MACAddress": mac,
            "Name": Name,
            "Interface": f"DEV.WIFI.AP{SSID}",
            "Btn_cancel_MACFilterRule": "",
            "Btn_apply_MACFilterRule": "",
            "_sessionTOKEN": bytes(_sessionTmpToken, "utf-8").decode("unicode_escape"),
        },
    )

    return session


######################################


def main():
    global Router_Ip, USERNAME, PASSWORD
    parser = argparse.ArgumentParser(description="Manage router settings via CLI.")
    parser.add_argument('--router-ip', default=Router_Ip, help='Router IP address (default: 192.168.1.1)')
    parser.add_argument('--username', default=USERNAME, help='Router admin username (default: admin)')
    parser.add_argument('--password', default=PASSWORD, help='Router admin password (default: admin)')

    subparsers = parser.add_subparsers(dest='command', required=True)



    # Restart command
    subparsers.add_parser('restart', help='Restart the router')

    # List MACs command
    subparsers.add_parser('list-macs', help='List MAC addresses in the whitelist')

    # Add MAC command
    add_mac_parser = subparsers.add_parser('add-mac', help='Add a MAC address to the whitelist')
    add_mac_parser.add_argument('--name', required=True, help='Name for the MAC entry')
    add_mac_parser.add_argument('--mac', required=True, help='MAC address to add')
    add_mac_parser.add_argument('--ssid', type=int, default=1, help='SSID (default: 1)')

    # Delete MAC command
    delete_mac_parser = subparsers.add_parser('delete-mac', help='Delete a MAC address from the whitelist')
    delete_mac_parser.add_argument('--name', help='Name of the MAC entry to delete')
    delete_mac_parser.add_argument('--mac', help='MAC address to delete')
    delete_mac_parser.add_argument('--ssid', type=int, default=1, help='SSID (default: 1)')

    # Logout command
    subparsers.add_parser('logout', help='Logout from the router')

    args = parser.parse_args()

    # Update global variables based on args
    Router_Ip = args.router_ip
    USERNAME = args.username
    PASSWORD = args.password

    session = create_session()

    if args.command == 'restart':
        if Login(session):
            Restart(session)
    elif args.command == 'list-macs':
        if Login(session):
            get_All_Mac(session)
    elif args.command == 'add-mac':
        if Login(session):
            add_Mac_to_the_whitelist(session, name=args.name, Mac=args.mac, SSID=args.ssid)
    elif args.command == 'delete-mac':
        if not args.name and not args.mac:
            print("Error: Either --name or --mac must be provided for delete-mac")
            return
        if Login(session):
            all_macs = get_All_Mac(session)
            delete_Mac_from_the_whitelist(session, all_macs, name=args.name, Mac=args.mac, SSID=args.ssid)
    elif args.command == 'logout':
        logout(session)

if __name__ == "__main__":
    main()
