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
        if not proxies:
            print(f"🔄 {Fore.YELLOW+Style.BRIGHT}[ No Proxies Available. Getting New Proxies ]")
            proxies = pro.get_proxies()
            if not proxies:
                print(f"🍒 {Fore.RED+Style.BRIGHT}[ Failed to Get Proxies ]")
                break

        proxy = proxies[proxy_index]

        while not pro.is_proxy_live(proxy):
            print(f"🔴 {Fore.RED+Style.BRIGHT}[ Proxy Dead ]\t\t: {proxy}")
            proxies.pop(proxy_index)
            if not proxies:
                print(f"🔄 {Fore.YELLOW+Style.BRIGHT}[ No Proxies Available. Getting New Proxies ]")
                proxies = pro.get_proxies()
                if not proxies:
                    print(f"🍒 {Fore.RED+Style.BRIGHT}[ Failed to Get Proxies ]")
                    break
            proxy_index %= len(proxies)
            proxy = proxies[proxy_index]

        if not proxies:
            print(f"❌ {Fore.RED+Style.BRIGHT}[ No Live Proxies Available ]")
            break
        
        print(f"🟢 {Fore.GREEN+Style.BRIGHT}[ Proxy Live ]\t\t: {proxy}")
        
        while True:
            print(f"📧 {Fore.CYAN+Style.BRIGHT}[ Progress {index} ]\t\t: {email}")
            if pix.request_otp(email, proxy):
                print(f"📥 {Fore.YELLOW+Style.BRIGHT}[ OTP Requested ]\t\t: {email}")
                time.sleep(10)
                body = pix.search_email(connect_imap)
                code = pix.extract_otp(body)
                print(f"📤 {Fore.GREEN+Style.BRIGHT}[ OTP Received ]\t\t: {code}")
                data = pix.verify_otp(email, code, proxy)
                if data and 'access_token' in data:
                    access_token = data['access_token']
                    print(f"🍏 {Fore.GREEN+Style.BRIGHT}[ Access Token Received ]")
                    if pix.set_referrals(access_token, proxy):
                        print(f"🍏 {Fore.GREEN+Style.BRIGHT}[ Successfully Set Referrals ]")
                    else:
                        print(f"🍎 {Fore.RED+Style.BRIGHT}[ Failed To Set Referrals ]")
                else:
                    print(f"🍎 {Fore.RED+Style.BRIGHT}[ Failed To Get Access Token ]")
                break
            else:
                print(f"🍎 {Fore.RED+Style.BRIGHT}[ Failed To Request OTP ]")
                proxies.pop(proxy_index)
                if not proxies:
                    print(f"🔄 {Fore.YELLOW+Style.BRIGHT}[ No Proxies Available. Getting New Proxies ]")
                    proxies = pro.get_proxies()
                    if not proxies:
                        print(f"🍒 {Fore.RED+Style.BRIGHT}[ Failed to Get Proxies ]")
                        break
                proxy_index %= len(proxies)
                proxy = proxies[proxy_index]
                while not pro.is_proxy_live(proxy):
                    print(f"🔴 {Fore.RED+Style.BRIGHT}[ Proxy Dead ]\t\t: {proxy}")
                    proxies.pop(proxy_index)
                    if not proxies:
                        print(f"🔄 {Fore.YELLOW+Style.BRIGHT}[ No Proxies Available. Getting New Proxies ]")
                        proxies = pro.get_proxies()
                        if not proxies:
                            print(f"🍒 {Fore.RED+Style.BRIGHT}[ Failed to Get Proxies ]")
                            break
                    proxy_index %= len(proxies)
                    proxy = proxies[proxy_index]
                print(f"🟢 {Fore.GREEN+Style.BRIGHT}[ Switched To Proxy ]\t: {proxy}")
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