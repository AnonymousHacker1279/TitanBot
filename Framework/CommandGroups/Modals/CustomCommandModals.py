import json
import os
from datetime import datetime

import discord

from Framework.FileSystemAPI import DatabaseObjects, FileAPI
from Framework.GeneralUtilities import Constants, GeneralUtilities, VirusTotalQuery


class AddCommand(discord.ui.Modal):
	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

		self.add_item(discord.ui.InputText(label="Command Name"))
		self.add_item(discord.ui.InputText(label="Command Alias (Short name)"))
		self.add_item(discord.ui.InputText(label="Command Description", style=discord.InputTextStyle.long))
		self.add_item(discord.ui.InputText(label="Wizard-Only (Admin)", placeholder="False"))
		self.add_item(discord.ui.InputText(label="Code", style=discord.InputTextStyle.long))

	async def callback(self, interaction: discord.Interaction):
		embed = discord.Embed(color=discord.Color.dark_blue(), description='')

		command_name = self.children[0].value
		alias = self.children[1].value
		description = self.children[2].value
		wizard_only = self.children[3].value
		code = self.children[4].value

		if command_name is not None:
			if code is None:
				embed.title = "Failed to Add Custom Command"
				embed.description = "You must provide code to run with the command."
			if code is not None:
				# Scan the code for malware unless disabled
				message = None
				if Constants.ENABLE_CUSTOM_COMMANDS_MALWARE_SCANNING == "True":
					embed.title = "Command Addition Pending"
					embed.description = "Your command is currently being scanned for malware via VirusTotal. " \
										"This process can take some time, so please be patient."
					embed.set_footer(text="This window will automatically update once the scan is complete.")
					message = await interaction.response.send_message(embed=embed)
					scan_result = await VirusTotalQuery.scan_text(code)
					if scan_result["THREAT"]:
						embed.title = "Refusing to Add Custom Command: Malware Detected"
						embed.description = "A malware scan via VirusTotal determined the submitted code to be **malicious**." \
							"\n```txt\nMalware Name: " + scan_result["THREAT_NAME"] + "\nSHA-256 Hash: " \
							"" + scan_result["SHA256"] + "\n```\nThe scan result can be found below:\n" \
							"https://www.virustotal.com/gui/file/" + scan_result["SHA256"]

						embed.set_footer(text="Think something is wrong? Please contact an administrator.")
						await message.edit(embed=embed)
				else:
					scan_result = {"THREAT": False}

				if scan_result["THREAT"] is False:
					# Minimize the code to save space
					code = await GeneralUtilities.minimize_js(code)

					file_path = os.path.abspath(
						await DatabaseObjects.get_custom_commands_directory(interaction.guild.id) + "/" + command_name + ".js")
					await FileAPI.create_empty_file(file_path)
					with open(file_path, 'w') as f:
						f.write(code)

					with open(await DatabaseObjects.get_custom_commands_metadata_database(interaction.guild.id), 'r') as f:
						metadata_database = json.load(f)

					with open(await DatabaseObjects.get_custom_commands_metadata_database(interaction.guild.id), 'w') as f:
						metadata_database["aliases"][alias] = command_name
						if wizard_only:
							metadata_database["wizard_only_commands"].append(command_name)

						metadata_database["metadata"][command_name] = {}
						metadata_database["metadata"][command_name]["date_added"] = datetime.now().isoformat()
						metadata_database["metadata"][command_name]["author"] = interaction.user.id
						metadata_database["metadata"][command_name]["size"] = str(len(code.encode('utf-8'))) + " bytes"

						if description is None:
							metadata_database["metadata"][command_name]["description"] = "No description provided."
						else:
							metadata_database["metadata"][command_name]["description"] = description

						json.dump(metadata_database, f, indent=4)

					embed.title = "Custom Command Added: " + command_name
					embed.description = "You can now run the custom command by executing `/custom_command "\
										+ command_name + "` or by using the alias `" + alias + "`"
					embed.set_footer(text="")

					if message is not None:
						await interaction.edit_original_message(embed=embed)
					else:
						await interaction.response.send_message(embed=embed)
			else:
				embed.title = "Failed to Add Custom Command"
				embed.description = "You must provide code to run with the command."
				await interaction.response.send_message(embed=embed)
		else:
			embed.title = "Failed to Add Custom Command"
			embed.description = "You must specify a command name."

			await interaction.response.send_message(embed=embed)
