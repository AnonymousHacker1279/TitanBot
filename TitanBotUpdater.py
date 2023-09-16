##########################
# TitanBot Update Script #
##########################

# WARNING! This script is not meant to be run by the user.
# TitanBot will execute this script automatically when an update is available.
#
# Modifying this file may cause TitanBot to not update properly
# and could cause loss of data!

import json
import os
import shutil
import sys
import tempfile
import time

print("TitanBot Updater is starting...")

# Wait 5 seconds, to ensure all files are unlocked by threads
print("Waiting 5 seconds, to ensure files are unlocked...")
time.sleep(5)

# Get the metadata file from script arguments
metadata_file = sys.argv[1]

# Get the target directory from script arguments
target_directory = sys.argv[2]

# Read the metadata file
with open(metadata_file, "r") as file:
	metadata = json.load(file)
	file.close()
print("Read metadata file")

# Change to the target directory
print("Entering target directory")
os.chdir(target_directory)

# Make the temporary directory in the system's temporary directory
print("Making temporary directory")
temp_directory = tempfile.mkdtemp()

# Backup the target directory
backup_file = metadata["previous_version"] + "_" + metadata["previous_commit"] + "_backup"

# Create the backup file
print("Backing up the target directory")
# Ignore existing backups in the "Backups" directory, by temporarily moving them to the temporary directory
if os.path.exists(target_directory + "\\Storage\\UpdateManager\\Backups\\"):
	shutil.move(target_directory + "\\Storage\\UpdateManager\\Backups\\", temp_directory + "\\Backups\\")
shutil.make_archive(backup_file, "gztar", target_directory)

# Move the backup file to the target directory
# Make the directory if it does not exist
print("Moving backup file into the target directory")
if not os.path.exists(target_directory + "\\Storage\\UpdateManager\\Backups\\"):
	os.mkdir(target_directory + "\\Storage\\UpdateManager\\Backups\\")
shutil.move(backup_file + ".tar.gz", target_directory + "\\Storage\\UpdateManager\\Backups\\")
# Move the old backups back
if os.path.exists(temp_directory + "\\Backups\\"):
	# Move all files in the directory
	for item in os.listdir(temp_directory + "\\Backups\\"):
		shutil.move(temp_directory + "\\Backups\\" + item, target_directory + "\\Storage\\UpdateManager\\Backups\\")

# Use Git to update the target directory
print("Updating from GitHub repository")
gh_branch = metadata["github_branch"]
os.system("git fetch --all")
os.system("git reset --hard origin/" + gh_branch)

# Delete the extracted directory and its contents
print("Cleaning up")
shutil.rmtree(temp_directory)

# Delete the metadata file
os.remove(metadata_file)

# Activate the virtual environment
print("Activating virtual environment")
if os.name == "nt":
	os.system("start /B venv\\Scripts\\activate.bat")
else:
	os.system("source venv/bin/activate")

# Update dependencies
print("Updating dependencies")
os.system("pip install -r requirements.txt")

# Restart TitanBot
print("Restarting TitanBot")
# Use a new process so the current process can exit
# Open it in the background
if os.name == "nt":
	os.system("start /B venv\\Scripts\\python.exe TitanBot.py")
else:
	os.system("python3 TitanBot.py &")
