import requests
import os

ASEPRITE_REPOSITORY = 'aseprite/aseprite'
SKIA_REPOSITORY = 'aseprite/skia'
SKIA_RELEASE_FILE_NAME = 'Skia-Windows-Release-x64.zip'

def get_latest_tag_aseprite():
	"""
	Gets the tag name of the most recent release from the Aseprite repository.
	This includes pre-releases (betas, release candidates).
	"""
	response = requests.get(f'https://api.github.com/repos/{ASEPRITE_REPOSITORY}/releases')
	response.raise_for_status()  # Will raise an error for bad responses
	response_json = response.json()

	# The GitHub API lists releases from newest to oldest.
	# The first item in the list is the latest version.
	if response_json:
		return response_json[0]['tag_name']

	return None

def save_aseprite_tag(tag):
	"""Saves the provided tag to a file named version.txt."""
	with open('version.txt', 'w') as f:
		f.write(tag)

def clone_aseprite(tag):
	"""Clones the Aseprite repository at a specific tag."""
	clone_url = f'https://github.com/{ASEPRITE_REPOSITORY}.git'
	git_cmd = f'git clone -b {tag} {clone_url} src/aseprite --depth 1'
	os.system(git_cmd)
	os.system('cd src/aseprite && git submodule update --init --recursive')

def get_latest_tag_skia():
	"""Gets the required Skia tag. This is hardcoded for compatibility."""
	# The Skia version is often tied to a specific Aseprite build.
	# The original hardcoded value is kept for stability.
	# response = requests.get(f'https://api.github.com/repos/{SKIA_REPOSITORY}/releases/latest')
	# response_json = response.json()
	# return response_json['tag_name']
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
	os.system(f'7z x src/{SKIA_RELEASE_FILE_NAME} -osrc/skia')

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
		
		print("\nSetup complete.")
	else:
		print("Could not find the latest Aseprite version tag.")
