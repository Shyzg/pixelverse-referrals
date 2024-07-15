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
            print(f"🔄 {Fore.YELLOW + Style.BRIGHT}[ No Proxies Available. Getting New Proxies ]")
            proxies = pro.get_proxies()
            if not proxies:
                print(f"🔴 {Fore.RED + Style.BRIGHT}[ Failed to Get Proxies ]")
                break

        proxy = proxies[proxy_index]

        while not pro.is_proxy_live(proxy):
            proxies.pop(proxy_index)
            if not proxies:
                print(f"🔄 {Fore.YELLOW + Style.BRIGHT}[ No Proxies Available. Getting New Proxies ]")
                proxies = pro.get_proxies()
                if not proxies:
                    print(f"🔴 {Fore.RED + Style.BRIGHT}[ Failed to Get Proxies ]")
                    break
            proxy_index %= len(proxies)
            proxy = proxies[proxy_index]

        while True:
            print(f"📧 {Fore.CYAN + Style.BRIGHT}[ Progress {index}"
                  f"{Fore.WHITE + Style.BRIGHT} | "
                  f"{Fore.CYAN + Style.BRIGHT}{email} ]")
            print(f"🟢 {Fore.GREEN + Style.BRIGHT}[ {proxy} ]")
            if pix.request_otp(email, proxy):
                time.sleep(20)
                body = pix.search_email(connect_imap)
                code = pix.extract_otp(body)
                print(f"📤 {Fore.BLUE + Style.BRIGHT}[ OTP Received"
                      f"{Fore.WHITE + Style.BRIGHT} | "
                      f"{Fore.BLUE + Style.BRIGHT}{code} ]")
                pix.verify_otp(email, code, proxy)
                break
            else:
                proxies.pop(proxy_index)
                if not proxies:
                    print(f"🔄 {Fore.YELLOW + Style.BRIGHT}[ No Proxies Available. Getting New Proxies ]")
                    proxies = pro.get_proxies()
                    if not proxies:
                        print(f"🔴 {Fore.RED + Style.BRIGHT}[ Failed to Get Proxies ]")
                        break

                proxy_index %= len(proxies)
                proxy = proxies[proxy_index]

                while not pro.is_proxy_live(proxy):
                    proxies.pop(proxy_index)
                    if not proxies:
                        print(f"🔄 {Fore.YELLOW + Style.BRIGHT}[ No Proxies Available. Getting New Proxies ]")
                        proxies = pro.get_proxies()
                        if not proxies:
                            print(f"🔴 {Fore.RED+Style.BRIGHT}[ Failed to Get Proxies ]")
                            break
                    proxy_index %= len(proxies)
                    proxy = proxies[proxy_index]

                print(f"🟡 {Fore.YELLOW + Style.BRIGHT}[ Switched To {proxy} ]")

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