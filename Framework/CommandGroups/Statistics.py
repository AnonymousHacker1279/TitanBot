import os

import discord
import matplotlib.pyplot as plt
from discord.ext import commands

from Framework.CommandGroups.BasicCog import BasicCog
from Framework.GeneralUtilities import PermissionHandler


class Statistics(BasicCog):
	"""Get statistics and analytical data regarding the bot."""

	statistics = discord.SlashCommandGroup("statistics", description="Get statistics and analytical data regarding the bot.")

	@statistics.command()
	@commands.guild_only()
	async def most_used_commands(self, ctx: discord.ApplicationContext):
		"""Get the ten most used commands."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failed_permission_check = await PermissionHandler.check_permissions(ctx, embed, "statistics")
		if not failed_permission_check:
			data = await self.sql_bridge.statistics_module.get_top_ten_commands()

			# Extract data
			analytics = [f"{item[0]} [{item[1]}]" for item in data]
			usage_counts = [item[2] for item in data]

			# Convert usage_counts to integers
			usage_counts = [int(count) for count in usage_counts]

			# Combine commands and usage_counts into a list of tuples
			data_tuples = list(zip(analytics, usage_counts))

			# Sort the data_tuples in ascending order of usage count
			data_tuples.sort(key=lambda x: x[1])

			# Unzip the sorted data_tuples back into commands and usage_counts
			analytics, usage_counts = zip(*data_tuples)

			# Create a bar graph
			bars = plt.barh(analytics, usage_counts, color="#0047AB")

			# Add usage counts next to each bar
			for bar in bars:
				plt.text(bar.get_width(), bar.get_y() + bar.get_height() / 2,
						f' {bar.get_width()}',
						va='center', ha='left', color='white')

			plt.xlabel('Times Used', color='white')
			plt.title('Command Usage Analytics', color='white')

			# Change the color of the axes and tick labels
			plt.tick_params(colors='white')
			plt.gca().spines['bottom'].set_color('#990000')
			plt.gca().spines['left'].set_color('#990000')
			plt.gca().spines['top'].set_color('#00000000')
			plt.gca().spines['right'].set_color('#00000000')

			# Save the graph as an image file - make a random name for the file based on the hash of the data
			path = f"{os.getcwd()}/Storage/Temp/{str(hash(analytics))}.png"

			# Ensure the directory exists
			os.makedirs(os.path.dirname(path), exist_ok=True)

			plt.savefig(path, bbox_inches='tight', transparent=True)
			plt.close()

			# Include the graph in the embed
			embed.title = "Top Ten Most Used Commands"
			file = discord.File(path, filename=path.split("/")[-1])
			embed.set_image(url="attachment://" + path.split("/")[-1])

			await ctx.respond(embed=embed, file=file)
		else:
			await ctx.respond(embed=embed)

		await self.update_usage_analytics("statistics", "most_used_commands", ctx.guild.id)

	@statistics.command()
	@discord.option(
		name="all_guilds",
		description="Get the top quoted users across all guilds.",
		type=bool,
		required=False
	)
	@commands.guild_only()
	async def top_quoted_users(self, ctx: discord.ApplicationContext, all_guilds: bool = False):
		"""Get the top three most quoted users."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failed_permission_check = await PermissionHandler.check_permissions(ctx, embed, "statistics")
		if not failed_permission_check:
			data = await self.sql_bridge.statistics_module.get_top_quoted_users(ctx.guild_id, all_guilds)

			# Extract data
			analytics = [f"{(await ctx.bot.fetch_user(item[0])).name}" for item in data]
			times_quoted = [item[1] for item in data]

			# Convert to integers
			times_quoted = [int(count) for count in times_quoted]

			# Combine the analytics and times_quoted into a list of tuples
			data_tuples = list(zip(analytics, times_quoted))

			# Sort the data_tuples in ascending order of times_quoted
			data_tuples.sort(key=lambda x: x[1])

			# Unzip the sorted data_tuples back into analytics and times_quoted
			analytics, times_quoted = zip(*data_tuples)

			# Create a bar graph
			bars = plt.barh(analytics, times_quoted, color="#0047AB")

			# Add usage counts next to each bar
			for bar in bars:
				plt.text(bar.get_width(), bar.get_y() + bar.get_height() / 2,
						f' {bar.get_width()}',
						va='center', ha='left', color='white')

			plt.xlabel('Times Quoted', color='white')
			title = "Top Quoted Users"
			if all_guilds:
				title += " (Global)"
			plt.title(title, color='white')

			# Change the color of the axes and tick labels
			plt.tick_params(colors='white')
			plt.gca().spines['bottom'].set_color('#990000')
			plt.gca().spines['left'].set_color('#990000')
			plt.gca().spines['top'].set_color('#00000000')
			plt.gca().spines['right'].set_color('#00000000')

			# Save the graph as an image file - make a random name for the file based on the hash of the data
			path = f"{os.getcwd()}/Storage/Temp/{str(hash(analytics))}.png"

			# Ensure the directory exists
			os.makedirs(os.path.dirname(path), exist_ok=True)

			plt.savefig(path, bbox_inches='tight', transparent=True)
			plt.close()

			# Include the graph in the embed
			embed.title = "Top Quoted Users"
			if all_guilds:
				embed.title += " (Global)"
			file = discord.File(path, filename=path.split("/")[-1])
			embed.set_image(url="attachment://" + path.split("/")[-1])

			await ctx.respond(embed=embed, file=file)
		else:
			await ctx.respond(embed=embed)

		await self.update_usage_analytics("statistics", "top_quoted_users", ctx.guild.id)
