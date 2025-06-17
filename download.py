import requests
import os
import subprocess

ASEPRITE_REPOSITORY = 'aseprite/aseprite'
SKIA_REPOSITORY = 'aseprite/skia'
SKIA_RELEASE_FILE_NAME = 'Skia-Windows-Release-x64.zip'

def run_command(command):
    """Runs a command using subprocess and checks for errors."""
    print(f"Executing: {' '.join(command)}")
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        raise

def get_latest_tag_aseprite():
    """
    Gets the tag name of the most recent release from the Aseprite repository.
    This includes pre-releases (betas, release candidates).
    """
    response = requests.get(f'https://api.github.com/repos/{ASEPRITE_REPOSITORY}/releases')
    response.raise_for_status()
    response_json = response.json()

    if response_json:
        return response_json[0]['tag_name']
    return None

def save_aseprite_tag(tag):
    """Saves the provided tag to a file named version.txt."""
    with open('version.txt', 'w') as f:
        f.write(tag)

def clone_aseprite(tag):
    """
    Clones the Aseprite repository at a specific tag using the --recursive
    flag to ensure all submodules are downloaded correctly.
    """
    clone_url = f'https://github.com/{ASEPRITE_REPOSITORY}.git'
    git_cmd = [
        'git', 'clone',
        '--recursive',  # This is the key change to fix the dependency errors
        '-b', tag,
        '--depth', '1',
        clone_url,
        'src/aseprite'
    ]
    run_command(git_cmd)

def get_latest_tag_skia():
    """Gets the required Skia tag. This is hardcoded for compatibility."""
    return 'm102-861e4743af'

def download_skia_for_windows(tag):
    """Downloads and extracts the specified Skia version for Windows."""
    download_url = f'https://github.com/{SKIA_REPOSITORY}/releases/download/{tag}/{SKIA_RELEASE_FILE_NAME}'

    print(f"Downloading Skia version {tag}...")
    file_response = requests.get(download_url)
    file_response.raise_for_status()
    
    with open(f'src/{SKIA_RELEASE_FILE_NAME}', 'wb') as f:
        f.write(file_response.content)
    
    print("Extracting Skia...")
    # Using a list for the command is safer
    extract_cmd = ['7z', 'x', f'src/{SKIA_RELEASE_FILE_NAME}', '-osrc/skia']
    run_command(extract_cmd)

if __name__ == '__main__':
    print("Finding the latest Aseprite version...")
    aseprite_tag = get_latest_tag_aseprite()
    
    if aseprite_tag:
        print(f"Latest Aseprite tag found: {aseprite_tag}")
        clone_aseprite(aseprite_tag)
        save_aseprite_tag(aseprite_tag)

        print("\nFinding the required Skia version...")
        skia_tag = get_latest_tag_skia()
        download_skia_for_windows(skia_tag)
        
        print("\nSetup complete. You can now proceed with the CMake/Ninja build steps.")
    else:
        print("Could not find the latest Aseprite version tag.")
