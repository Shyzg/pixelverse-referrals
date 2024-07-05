from colorama import Fore, Style
from email import policy
from email.header import decode_header
from email.parser import BytesParser
import imaplib
import json
import random
import re
import string
import requests
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
        generated_emails = []

        for _ in range(self.count):
            random_string = ''.join(random.choices(string.ascii_lowercase, k=8))
            generated_email = f'{email_parts[0]}+{random_string}@{email_parts[1]}'
            generated_emails.append(generated_email)
            
        generated_emails.sort()

        with open('emails.txt', 'w') as file:
            for email in generated_emails:
                file.write(f'{email}\n')
        with open('emails.txt', 'r') as file:
            emails = file.read().strip().split('\n')
                
        print(f"🧬 {Fore.GREEN + Style.BRIGHT}[ Generated {self.count} Emails ]")
        return emails

    def connect_imap(self):
        mail = imaplib.IMAP4_SSL("imap-mail.outlook.com")
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
        proxies = {'http': f'http://{proxy}'}
        try:
            response = requests.post(url, proxies=proxies, json=payload)
            if response.status_code == 429:
                print(f"⏳ {Fore.YELLOW+Style.BRIGHT}[ {response.reason} Switching Proxy... ]")
                return False
            response.raise_for_status()
            return response.status_code in [200, 201]
        except (ValueError, json.JSONDecodeError, requests.RequestException) as e:
            print(f"🍓 {Fore.RED+Style.BRIGHT}[ Error ]\t\t: {e}")
            return False

    def verify_otp(self, email, otp, proxy):
        url = 'https://api.pixelverse.xyz/api/auth/otp'
        payload = {
            'email': email,
            'otpCode': otp
        }
        proxies = {'http': f'http://{proxy}'}
        try:
            response = requests.post(url, proxies=proxies, json=payload)
            response.raise_for_status()
            data = response.json()
            data['refresh_token'] = response.cookies.get('refresh-token')
            data['access_token'] = data['tokens']['access']
            return data
        except (ValueError, json.JSONDecodeError, requests.RequestException) as e:
            print(f"🍓 {Fore.RED+Style.BRIGHT}[ Error ]\t\t: {e}")
            return None

    def set_referrals(self, access_token, proxy):
        url = f'https://api.pixelverse.xyz/api/referrals/set-referer/{self.referrals}'
        self.headers['Authorization'] = access_token
        proxies = {'http': f'http://{proxy}'}
        try:
            response = requests.put(url, proxies=proxies, headers=self.headers)
            response.raise_for_status()
            return response.status_code in [200, 201]
        except (ValueError, json.JSONDecodeError, requests.RequestException) as e:
            print(f"🍓 {Fore.RED+Style.BRIGHT}[ Error ]\t\t: {e}")
            return None