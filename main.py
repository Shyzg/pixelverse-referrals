from colorama import Fore, Style, init
from Pixel import Pixel
from Proxy import Proxy
import os
import sys
import time


def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def main():
    init()
    pix = Pixel()
    pro = Proxy()
    emails = pix.generate_emails()
    proxies = pro.get_proxies()
    connect_imap = pix.connect_imap()
    proxy_index = 0
    for index, email in enumerate(emails, start=1):
        proxy = proxies[proxy_index]

        while not pro.is_proxy_live(proxy):
            proxy_index = (proxy_index + 1) % len(proxies)
            proxy = proxies[proxy_index]

        proxy_index = (proxy_index + 1) % len(proxies)
        print(f"📧 {Fore.CYAN+Style.BRIGHT}[ Progress {index} ]\t: {email}")
        if pix.requestOtp(email, proxy):
            print(f"✅ {Fore.YELLOW+Style.BRIGHT}[ OTP Requested ]\t: {email}")
            time.sleep(10)
            body = pix.search_email(connect_imap)
            code = pix.extractOtp(body)
            print(f"✅ {Fore.GREEN+Style.BRIGHT}[ OTP Received ]\t: {code}")
            data = pix.verifyOtp(email, code, proxy)
            if data and 'access_token' in data:
                access_token = data['access_token']
                print(f"✅ {Fore.GREEN+Style.BRIGHT}[ Access Token Received ]")
                if pix.setReferrals(access_token, proxy):
                    print(f"✅ {Fore.GREEN+Style.BRIGHT}[ Successfully Set Referrals ]")
                else:
                    print(f"🍎 {Fore.RED+Style.BRIGHT}[ Failed To Set Referrals ]")
            else:
                print(f"🍎 {Fore.RED+Style.BRIGHT}[ Failed To Get Access Token ]")
        else:
            print(f"🍎 {Fore.RED+Style.BRIGHT}[ Failed To Request OTP ]")
    connect_imap.logout()

if __name__ == "__main__":
    while True:
        try:
            main()
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(f"🍓 {Fore.RED+Style.BRIGHT}[ Error ]\t\t: {type(e).__name__} {e}")
        clear()