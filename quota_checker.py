import schedule
import time
import datetime  
import requests
# import threading
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options



class ScheduleAllProcess:

    def __init__(self, check_function):
        self.prayers_times = {}
        self.run_scheduler(check_function)


    def get_prayers_times(self):
        """ 
        Get the Islamic prayers times to schedule when to check the quota
        """
        api_data =  requests.get('https://api.aladhan.com/v1/timingsByCity?city=Cairo&country=Egypt&method=5').json()
        self.prayers_times["Fajr"]= api_data["data"]["timings"]["Fajr"]
        self.prayers_times["Dhuhr"]= api_data["data"]["timings"]["Dhuhr"]
        self.prayers_times["Asr"]= api_data["data"]["timings"]["Asr"]
        self.prayers_times["Maghrib"]= api_data["data"]["timings"]["Maghrib"]
        self.prayers_times["Isha"]= api_data["data"]["timings"]["Isha"]


    def schedule_running_process(self, check_function):
        if not self.prayers_times:
            self.get_prayers_times()
        
        for prayer_name, prayer_time in self.prayers_times.items():
            schedule.every().day.at(prayer_time).do(check_function)


    def run_scheduler(self, check_function):
        self.get_prayers_times()
        self.schedule_running_process(check_function)
        while True:
            schedule.run_pending()
            time.sleep(1)




class QuotaChecker:
    def __init__(self):
        self.remaining_quota = None
        options = Options()
        
        # إعدادات الأمان
        options.set_preference("webdriver_accept_untrusted_certs", True)
        options.set_preference("webdriver_assume_untrusted_issuer", True)
        options.set_preference("network.stricttransportsecurity.preloadlist", False)
        options.set_preference("security.cert_pinning.enforcement_level", 0)
        options.set_preference("security.csp.enable", False)
        options.set_preference("security.mixed_content.block_active_content", False)
        
        # إعدادات التسريع
        
        # وضع بدون واجهة
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)
        self.action = ActionChains(self.driver)
        try:
            self.get_remaining_quota()
        except Exception as e:
            print(e)
        # finally:
        #     self.driver.quit()
        #     exit()

    def get_remaining_quota(self):
        login_url = 'https://my.te.eg/echannel/#/login'
        self.driver.get(login_url)

        ### Fill the Login Form
        service_number_input = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, 'login_loginid_input_01')))
        service_number_input.send_keys('0482996952')
                    

        service_type = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, 'login_input_type_01')))
        service_type.click()
        time.sleep(2)

        service_type_internet_option = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, 'login_input_type_01_list_0')))
        self.action.click(service_type_internet_option).perform()

        password_input =  WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, 'login_password_input_01')))
        password_input.send_keys('Bodyryad20@')
        password_input.send_keys(Keys.ENTER)

        ### Check the remaining quota
        def get_quota_value():
            quota = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.ec_accountoverview_primaryBtn_Qyg-Vp:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(2) > div:nth-child(1) > span:nth-child(1)')))
            return quota.text
        quota = get_quota_value()
        print(f"CSS_SELECTOR Value: {get_quota_value()}")
        for i in range(5):
            if quota :
                self.remaining_quota = float(quota)
                break
            else:
                self.driver.get('https://my.te.eg/echannel/#/accountoverview')
                quota = get_quota_value()


    def cut_the_internet(self, ):
        if self.remaining_quota:
            if self.remaining_quota> 250 - (8*int(datetime.date.today().day)):
                return True
            else:
                return False



""" 
This is the class that controls the router using selenium , but we are going to use requests instead for some issues 
"""

# class ControllRouter:
#     def __init__(self, driver, action, Macs):
#         self.driver = driver
#         self.action = action
#         self.Macs = Macs
#         self.enable_Tls_Version1()
#         self.login()
#         self.cut_the_internet()
    

#     def enable_Tls_Version1(self):
#         self.driver.get('about:config')
#         Accept_button = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, 'warningButton'))).click()
#         search_input = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, 'about-config-search'))).send_keys('security.tls.version.min')
#         edit_button = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.button-edit'))).click()
#         Tls_Version_input = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#form-edit > input:nth-child(1)')))
#         Tls_Version_input.clear()
#         Tls_Version_input.send_keys('1')
#         Tls_Version_input.send_keys(Keys.ENTER)
#         self.driver.get('https://192.168.1.12')
#         try:
#             Advanced_button = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, 'advancedButton'))).click()
#             time.sleep(4)
#             Accept_Risk_button = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, 'exceptionDialogButton'))).click()
#         except Exception as e:
#             print(e)

    
#     def login(self):
#         time.sleep(5)
#         Username = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, 'Frm_Username')))
#         Username.send_keys('admin')
#         Password = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, 'Frm_Password')))
#         Password.send_keys('Bodyryad20@')
#         Password.send_keys(Keys.ENTER)   


#     def cut_the_internet(self):
#         WebDriverWait(self.driver, 50).until(lambda d: d.execute_script("return document.readyState") == "complete")
#         time.sleep(10)
#         local_network = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, 'mmLocalnet'))).click()
#         Wlan = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, 'smLocalWLAN'))).click()
    

#     def allow_Macs(self, name=None, Mac=None, SSID=1):
#         # Some Helper Functions
#         def timestamp_ms():
#             # Get the current time in seconds since the epoch
#             current_time_s = time.time()

#             # Convert to milliseconds like : 1723825585255
#             timestamp_ms = int(current_time_s * 1000)
#             return timestamp_ms
#         def extract__sessionTmpToken(Request):
#             start = (
#                 Request.find('_sessionTmpToken = "') + 1
#             )  # Find the index of the first quote and add 1
#             end = Request.find(
#                 '";', start
#             )  # Find the index of the second quote starting from 'start'
#             line = Request[start:end]
#             return line[line.find('"') + 1 :]
        

#         # pass selenium cookies to requests session
#         cookies = self.driver.get_cookies()
#         session= requests.Session()
#         for cookie in cookies:
#             session.cookies.set(cookie['name'], cookie['value'])
#         print(f"session.cookies:{session.cookies}")

#         ## Request 1 Wlan_Advanced ## Must
#         response = session.get(f"https://192.168.1.12/getpage.lua?pid=123&nextpage=Localnet_WlanAdvanced_t.lp&Menu3Location=0&_{timestamp_ms()}",verify=False)
#         _sessionTmpToken = extract__sessionTmpToken(response.text)
#         # if name and Mac
#         ## Request  Add ## Must
#         print(f"Mac , name: {Mac} , {name}")
#         response = session.post(
#             f"https://192.168.1.12/common_page/Localnet_WlanAdvanced_MACFilterRule_lua.lua",verify=False,
#             data={
#                 "IF_ACTION": "Apply",
#                 "_InstID": "-1",
#                 "MACAddress": Mac,
#                 "Name": name,
#                 "Interface": f"DEV.WIFI.AP{SSID}",
#                 "Btn_cancel_MACFilterRule": "",
#                 "Btn_apply_MACFilterRule": "",
#                 "_sessionTOKEN": bytes(_sessionTmpToken, "utf-8").decode("unicode_escape"),
#             },
#         )





if __name__ == "__main__":
    checker = QuotaChecker()
    checker.driver.close()
    if checker.cut_the_internet():
        print(f"the Daily Quota is Finished: {checker.remaining_quota} GB remaining\nWe are gonna Cut the Internet......\n" )
        del checker
        Mac_Addresses = {"dad-ph": "06:63:b1:8e:f3:bd",}
        network_cutting = ControllRouter( Mac_Addresses["dad-ph"]) 
    # schedule_process = ScheduleAllProcess(QuotaChecker)

