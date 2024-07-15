from colorama import Fore, Style
import requests

class Proxy:
    def get_proxies(self):
        proxy_sources = [
            'https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&proxy_format=ipport&format=text&timeout=20000'
        ]
        all_proxies = set()

        for url in proxy_sources:
            try:
                response = requests.get(url=url)
                response.raise_for_status()
                proxies = response.text.strip().splitlines()
                all_proxies.update(proxies)
            except (ValueError, requests.RequestException) as e:
                print(f"🍓 {Fore.RED+Style.BRIGHT}[ {e} ]")
                return None

        sorted_proxies = sorted(all_proxies)
        print(f"🧬 {Fore.CYAN + Style.BRIGHT}[ Generated {len(sorted_proxies)} Proxies ]")
        return sorted_proxies

    def is_proxy_live(self, proxy):
        url = 'http://httpbin.org/ip'
        proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        try:
            response = requests.get(url, proxies=proxies, timeout=5)
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False