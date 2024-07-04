from colorama import Fore, Style, init
from Pixel import Pixel
import os
import requests
import sys
import time

def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def is_proxy_live(proxy):
    try:
        url = 'http://httpbin.org/ip'
        proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        response = requests.get(url, proxies=proxies, timeout=5)
        if response.status_code == 200:
            return True
    except:
        return False
    return False

def main():
    init()
    pixel = Pixel()
    pixel.generate_emails()
    time.sleep(5)
    with open('emails.txt', 'r') as file:
        emails = [line.strip() for line in file.readlines()]
    mail = pixel.connect_imap()
    response = requests.get('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format=ipport&format=text')
    with open('proxies.txt', 'w') as file:
        file.write(response.text)
    time.sleep(5)
    with open('proxies.txt', 'r') as f:
        proxies = [line.strip() for line in f.readlines() if line.strip()]
    proxy_index = 0
    for index, email in enumerate(emails, start=1):
        proxy = proxies[proxy_index]
        while not is_proxy_live(proxy):
            proxy_index = (proxy_index + 1) % len(proxies)
            proxy = proxies[proxy_index]
        proxy_index = (proxy_index + 1) % len(proxies)
        print(f"📧 {Fore.CYAN+Style.BRIGHT}[ Progress {index} ]\t: {email}")
        if pixel.requestOtp(email, proxy):
            print(f"✅ {Fore.YELLOW+Style.BRIGHT}[ OTP Requested ]\t: {email}")
            time.sleep(10)
            body = pixel.search_email(mail)
            code = pixel.extractOtp(body)
            print(f"✅ {Fore.GREEN+Style.BRIGHT}[ OTP Received ]\t: {code}")
            data = pixel.verifyOtp(email, code, proxy)
            if data and 'access_token' in data:
                access_token = data['access_token']
                print(f"✅ {Fore.GREEN+Style.BRIGHT}[ Access Token Received ]")
                if pixel.setReferrals(access_token, proxy):
                    print(f"✅ {Fore.GREEN+Style.BRIGHT}[ Successfully Set Referrals ]")
                else:
                    print(f"🍎 {Fore.RED+Style.BRIGHT}[ Failed To Set Referrals ]")
            else:
                print(f"🍎 {Fore.RED+Style.BRIGHT}[ Failed To Get Access Token ]")
        else:
            print(f"🍎 {Fore.RED+Style.BRIGHT}[ Failed To Request OTP ]")
    mail.logout()

if __name__ == "__main__":
    while True:
        try:
            main()
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(f"🍓 {Fore.RED+Style.BRIGHT}[ Error ]\t\t: {type(e).__name__} {e}")
        clear()