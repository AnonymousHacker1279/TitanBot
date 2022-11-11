import json
import os
import tempfile
from enum import Enum

import discord
import requests
from discord.ext.bridge import Bot

from Framework.FileSystemAPI import DatabaseObjects
from Framework.FileSystemAPI.ConfigurationManager import ConfigurationValues
from Framework.FileSystemAPI.ConfigurationManager.ConfigurationManager import ConfigurationManager
from Framework.FileSystemAPI.ThreadedLogger import ThreadedLogger
from Framework.GeneralUtilities import GeneralUtilities
from Framework.ManagementPortal.ManagementPortalHandler import ManagementPortalHandler


# The update manger checks for new updates on the GitHub repository and
# downloads/installs them if they are available
class UpdateManager:

	def __init__(self, mph: ManagementPortalHandler, cm: ConfigurationManager, bot: Bot, scheduled: bool = False):
		self.logger = ThreadedLogger("UpdateManager", mph)
		self.configuration_manager = cm
		self.bot = bot
		self.scheduled = scheduled
		self.update_configuration = GeneralUtilities.run_and_get(cm.get_value("bot_update"))

		self.gh_repository = ConfigurationValues.UPDATE_REPOSITORY
		self.restart_on_update = self.update_configuration["restart_on_update"]

		self.update_available = False
		self.update_commit = None
		self.current_commit = ConfigurationValues.COMMIT

		self.latest_release_info = None

	async def check_for_updates(self):
		self.logger.log_info("Checking for updates at " + self.gh_repository)
		# Check the GitHub repository for new releases
		current_release = ConfigurationValues.VERSION
		latest_release = await self.get_latest_release()
		# If there is an -indev in the version string, do not update as it is a development version
		if "-indev" in current_release:
			self.logger.log_warning("Development version detected, skipping update check")
			return
		# If the current release is not the latest release, update is available
		if current_release != latest_release:
			self.update_available = True
			self.logger.log_info("An update is available: " + latest_release)

			# Check if an update has already been downloaded, and is pending installation
			if os.path.exists(await DatabaseObjects.get_update_metadata()):
				with open(await DatabaseObjects.get_update_metadata(), "r") as file:
					update_metadata = json.load(file)

					try:
						if update_metadata["version"] == latest_release:
							self.logger.log_info("An update has already been downloaded, and is pending installation")
							# If it is unscheduled, the bot is just starting up, so install the update
							if not self.scheduled:
								await self.install_update()
					except TypeError:
						await self.download_update(latest_release)
			else:
				await self.download_update(latest_release)

	async def download_update(self, tag_name: str):
		# Download the latest release from the GitHub repository
		if self.update_available:
			await self.bot.change_presence(activity=discord.Game(name="Downloading updates..."), status=discord.Status.dnd)
			self.logger.log_info("Downloading update...")
			# Get the download URL for the latest release, target the .tar.gz file
			download_url = self.latest_release_info["tarball_url"]
			# Download the latest release
			response = requests.get(download_url)
			# Write the latest release to a file
			# Delete the old update file if it exists
			path = await DatabaseObjects.get_update_directory() + "\\update.tar.gz"
			if os.path.exists(path):
				os.remove(path)

			with open(path, "wb") as file:
				file.write(response.content)
			self.logger.log_info("Update downloaded to " + path)

			# Create a metadata file for the update
			with open(await DatabaseObjects.get_update_metadata(), "w") as file:
				tag_release = requests.get(GHAPIEndpoints.TAG_RELEASE.format(self.gh_repository, tag_name)).json()

				update_metadata = {
					"commit": tag_release["object"]["sha"][:7],
					"version": tag_name,
					"previous_version": ConfigurationValues.VERSION,
					"previous_commit": ConfigurationValues.COMMIT,
					"update_file": path,
				}
				json.dump(update_metadata, file, indent=4)

			if self.scheduled and self.restart_on_update:
				self.logger.log_info("TitanBot will restart to install the update. Please wait...")
				await self.install_update()

			elif not self.scheduled:
				self.logger.log_info("An update was downloaded, but has not yet been installed. Please restart TitanBot to install the update.")

	async def install_update(self):
		# Install any updates that have been downloaded

		# Get the project directory
		project_directory = os.getcwd()

		# Copy the update script to a temporary location, so that it can overwrite the current files
		# This is necessary because the update script is running in the same directory as the files it is trying to overwrite
		updater = tempfile.NamedTemporaryFile(suffix=".py", delete=False)
		with open(project_directory + "\\TitanBotUpdater.py", "r") as file:
			updater.write(bytes(file.read(), "utf-8"))
			updater.close()

		# Run the update script, passing the path to the update metadata file and the project directory as args
		os.system(f'python "{updater.name}" "{await DatabaseObjects.get_update_metadata()}" "{project_directory}"')

		exit(0)

	async def get_latest_release(self):
		# Get the latest release from the GitHub repository
		headers = {"Accept": "application/vnd.github.v3+json"}
		response = requests.get(GHAPIEndpoints.LATEST_RELEASE.format(self.gh_repository), headers=headers)
		self.latest_release_info = response.json()
		return self.latest_release_info["tag_name"]


class GHAPIEndpoints(str, Enum):
	# GitHub API endpoints
	LATEST_RELEASE = "https://api.github.com/repos/{}/releases/latest"
	LATEST_COMMIT = "https://api.github.com/repos/{}/commits"
	TAG_RELEASE = "https://api.github.com/repos/{}/git/ref/tags/{}"
