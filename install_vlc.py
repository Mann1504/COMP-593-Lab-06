import requests
import hashlib
import pathlib
import os
import subprocess

# Constants
BASE_URL = "https://download.videolan.org/pub/videolan/vlc/3.0.21/win64/"
FILE_NAME_SHA256 = "vlc-3.0.21-win64.exe.sha256"
FILE_NAME = "vlc-3.0.21-win64.exe"

def get_expected_sha256():
    """Download the SHA-256 hash file and extract the expected hash value."""
    try:
        response = requests.get(f'{BASE_URL}/{FILE_NAME_SHA256}')
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text.split()[0]  # Extract the hash value
    except requests.exceptions.RequestException as e:
        print(f"Failed to download the SHA-256 file: {e}")
        exit()

def download_installer():
    """Download the VLC installer and return its binary content."""
    try:
        response = requests.get(f'{BASE_URL}/{FILE_NAME}')
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.content  # Return the binary content
    except requests.exceptions.RequestException as e:
        print(f"Failed to download the installer: {e}")
        exit()

def compute_sha256(file_binary):
    """Compute the SHA-256 hash of the downloaded installer."""
    sha256 = hashlib.sha256(file_binary)
    return sha256.hexdigest()

def save_installer(file_binary):
    """Save the installer to a temporary directory."""
    try:
        file_path = pathlib.Path(os.getenv('TEMP')) / FILE_NAME
        with open(file_path, "wb") as outfile:
            outfile.write(file_binary)
        return file_path
    except Exception as e:
        print(f"Failed to save the installer: {e}")
        exit()

def run_installer(file_path):
    """Run the installer silently and wait for it to complete."""
    try:
        result = subprocess.run([file_path, '/L=1033', '/S'], check=True)
        if result.returncode == 0:
            print("VLC installed successfully!")
        else:
            print("Installation failed.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to run the installer: {e}")
        exit()

def delete_installer(file_path):
    """Delete the installer file from disk."""
    try:
        file_path.unlink()
        print("Installer file deleted.")
    except Exception as e:
        print(f"Failed to delete the installer: {e}")

def main():
    """Main function to automate the VLC installation process."""
    # Step 1: Get the expected SHA-256 hash value
    expected_sha256 = get_expected_sha256()
    print(f"Expected SHA-256 hash: {expected_sha256}")

    # Step 2: Download the installer
    installer_binary = download_installer()
    print(f"Downloaded installer size: {len(installer_binary)} bytes")

    # Step 3: Compute the SHA-256 hash of the downloaded installer
    computed_sha256 = compute_sha256(installer_binary)
    print(f"Computed SHA-256 hash: {computed_sha256}")

    # Step 4: Verify the integrity of the downloaded installer
    if computed_sha256 != expected_sha256:
        print("SHA-256 hash mismatch. The installer may be corrupted. Exiting...")
        exit()

    # Step 5: Save the installer to disk
    installer_path = save_installer(installer_binary)
    print(f"Installer saved to: {installer_path}")

    # Step 6: Run the installer silently
    run_installer(installer_path)

    # Step 7: Delete the installer file
    delete_installer(installer_path)

if __name__ == "__main__":
    main()