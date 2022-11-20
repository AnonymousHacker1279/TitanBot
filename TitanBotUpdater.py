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

# Extract the update file to the temporary directory
print("Unpacking update file")
shutil.unpack_archive(metadata["update_file"], temp_directory)

# Get the name of the directory that contains the update files
update_directory = os.listdir(temp_directory)[0]

# Backup the target directory
backup_file = metadata["previous_version"] + "_" + metadata["previous_commit"] + "_backup"

# Create the backup file
print("Backing up the target directory")
# Ignore existing backups in the "Backups" directory, by temporarily moving them to the temporary directory
if os.path.exists(target_directory + "\\Storage\\UpdateManager\\Backups\\"):
	shutil.move(target_directory + "\\Storage\\UpdateManager\\Backups\\", temp_directory + "\\Backups\\")
shutil.make_archive(backup_file, "gztar", target_directory)

# Delete some directories
# This is purged in case an update deletes or renames a file, so that it is not left behind
print("Purging directories")
shutil.rmtree("Framework")
shutil.rmtree("Resources")

# Move the contents of the update directory to the target directory
# Directories and files must be done separately, otherwise shutil.move will throw an error
print("Moving update files to target directory")
for item in os.listdir(temp_directory + "\\" + update_directory):
	# check if the item is a file or directory
	if os.path.isfile(temp_directory + "\\" + update_directory + "\\" + item):
		# move the file
		shutil.copy2(temp_directory + "\\" + update_directory + "\\" + item, target_directory)
	else:
		# move the directory
		shutil.copytree(temp_directory + "\\" + update_directory + "\\" + item, target_directory + "\\" + item)

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

# Delete the extracted directory and its contents
print("Cleaning up")
shutil.rmtree(temp_directory)

# Delete the update file
os.remove(metadata["update_file"])

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
