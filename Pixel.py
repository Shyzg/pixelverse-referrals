from colorama import Fore, Style
from email import policy
from email.header import decode_header
from email.parser import BytesParser
import imaplib
import json
import random
import re
import requests
import string
import time


class Pixel:
    def __init__(self):
        with open('config.json', 'r') as file:
            self.config = json.load(file)

        self.email = self.config['email']
        self.password = self.config['password']
        self.referrals = self.config['referrals']
        self.count = self.config['count']
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Origin': 'https://dashboard.pixelverse.xyz',
            'Referer': 'https://dashboard.pixelverse.xyz/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/126.0.0.0 Safari/537.36'
        }

    def generate_emails(self):
        email_parts = self.email.split('@')
        generated_emails = set()

        for _ in range(self.count):
            random_string = ''.join(random.choices(string.ascii_lowercase, k=8))
            emails = f'{email_parts[0]}+{random_string}@{email_parts[1]}'.strip().splitlines()
            generated_emails.update(emails)

        sorted_emails = sorted(generated_emails)
        print(f"🧬 {Fore.CYAN + Style.BRIGHT}[ Generated {len(sorted_emails)} Emails ]")
        return sorted_emails

    def connect_imap(self):
        mail = imaplib.IMAP4_SSL('imap-mail.outlook.com')
        mail.login(self.email, self.password)
        return mail
    
    def search_email(self, mail):
        mail.select('inbox')
        status, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()
        for email_id in reversed(email_ids):
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = BytesParser(policy=policy.default).parsebytes(response_part[1])
                    msg_subject = decode_header(msg['Subject'])[0][0]
                    if isinstance(msg_subject, bytes):
                        msg_subject = msg_subject.decode()
                    if 'Pixelverse Authorization' in msg_subject:
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                if content_type == 'text/plain':
                                    body = part.get_payload(decode=True).decode()
                                    return body
                        else:
                            body = msg.get_payload(decode=True).decode()
                            return body
        return None
    
    def extract_otp(self, body):
        otp_match = re.search(r'Here is your Pixelverse OTP: (\d+)', body)
        return otp_match.group(1) if otp_match else None

    def request_otp(self, email, proxy):
        url = 'https://api.pixelverse.xyz/api/otp/request'
        payload = {'email': email}
        proxies = {'http': f"http://{proxy}"}
        try:
            response = requests.post(url, proxies=proxies, json=payload)
            time.sleep(5)
            response.raise_for_status()
            print(f"📥 {Fore.BLUE + Style.BRIGHT}[ OTP Requested"
                  f"{Fore.WHITE + Style.BRIGHT} | "
                  f"{Fore.BLUE + Style.BRIGHT}{email} ]")
            return True
        except (ValueError, json.JSONDecodeError, requests.RequestException) as e:
            print(f"🍓 {Fore.RED + Style.BRIGHT}[ {e} ]")
            print(f"⏳ {Fore.YELLOW + Style.BRIGHT}[ Switching Proxies ]")
            return False

    def verify_otp(self, email, otp, proxy):
        url = 'https://api.pixelverse.xyz/api/auth/otp'
        payload = {
            'email': email,
            'otpCode': otp
        }
        proxies = {'http': f"http://{proxy}"}
        try:
            response = requests.post(url, proxies=proxies, json=payload)
            time.sleep(3)
            response.raise_for_status()
            data = response.json()
            data['refresh_token'] = response.cookies.get('refresh-token')
            data['access_token'] = data['tokens']['access']
            print(f"🍏 {Fore.GREEN + Style.BRIGHT}[ Access Token Received ]")
            self.set_referrals(data['access_token'], proxy)
            return True
        except (ValueError, json.JSONDecodeError, requests.RequestException) as e:
            print(f"🍓 {Fore.RED + Style.BRIGHT}[ {e} ]")
            print(f"⏳ {Fore.YELLOW + Style.BRIGHT}[ Switching Proxies ]")
            return False

    def set_referrals(self, access_token, proxy):
        url = f"https://api.pixelverse.xyz/api/referrals/set-referer/{self.referrals}"
        self.headers['Authorization'] = access_token
        proxies = {'http': f"http://{proxy}"}
        try:
            response = requests.put(url, proxies=proxies, headers=self.headers)
            time.sleep(2)
            response.raise_for_status()
            print(f"🍏 {Fore.GREEN + Style.BRIGHT}[ Successfully Set Referrals ]")
            return True
        except (ValueError, json.JSONDecodeError, requests.RequestException) as e:
            print(f"🍓 {Fore.RED + Style.BRIGHT}[ {e} ]")
            print(f"⏳ {Fore.YELLOW + Style.BRIGHT}[ Switching Proxies ]")
            return False