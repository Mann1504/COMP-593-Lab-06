import requests
import hashlib
import os
import subprocess
from bs4 import BeautifulSoup

def main():
    latest_version = get_latest_version()
    expected_sha256 = get_expected_sha256(latest_version)
    installer_data = download_installer(latest_version)

    if installer_ok(installer_data, expected_sha256):
        installer_path = save_installer(installer_data)
        run_installer(installer_path)
        delete_installer(installer_path)

def get_latest_version():
    url = "https://download.videolan.org/pub/videolan/vlc/last/win64/"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')
    versions = [link.text for link in links if link.text.startswith("vlc-") and link.text.endswith(".exe")]
    latest_version = versions[-1]  # Assuming the last one in the list is the latest
    return latest_version

def get_expected_sha256(latest_version):
    url = f"https://download.videolan.org/pub/videolan/vlc/3.0.17.4/win64/vlc-3.0.17.4-win64.exe.sha256"
    response = requests.get(url)
    response.raise_for_status()

    sha256_line = response.text.splitlines()[0]
    expected_hash = sha256_line.split()[0]
    return expected_hash

def download_installer(latest_version):
    url = f"https://download.videolan.org/pub/videolan/vlc/3.0.17.4/win64/vlc-3.0.17.4-win64.exe"
    response = requests.get(url, stream=True)
    response.raise_for_status()
    return response.content

def installer_ok(installer_data, expected_sha256):
    sha256 = hashlib.sha256(installer_data).hexdigest()
    return sha256 == expected_sha256

def save_installer(installer_data):
    installer_path = os.path.join(os.getcwd(), "vlc_installer.exe")
    with open(installer_path, 'wb') as file:
        file.write(installer_data)
    return installer_path

def run_installer(installer_path):
    subprocess.run([installer_path, '/S'], check=True)

def delete_installer(installer_path):
    os.remove(installer_path)

if __name__ == '__main__':
    main()
