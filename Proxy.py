from colorama import Fore, Style
import requests


class Proxy:
    def get_proxies(self):
        url = 'https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&proxy_format=ipport&format=text&timeout=20000'
        response = requests.get(url)
        proxies = response.text.strip().split('\n')
        proxies.sort()

        with open('proxies.txt', 'w') as file:
            for index, proxy in enumerate(proxies, start=1):
                file.write(f"{proxy}\n")
            print(f"🧬 {Fore.GREEN + Style.BRIGHT}[ Generated {index} Proxies ]")
        with open('proxies.txt', 'r') as file:
            proxies = file.read().strip().split('\n')

        return proxies

    def is_proxy_live(self, proxy):
        url = 'http://httpbin.org/ip'
        proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        try:
            response = requests.get(url, proxies=proxies, timeout=5)
            response.raise_for_status()
            if response.status_code == 200:
                return True
        except requests.RequestException:
            return False