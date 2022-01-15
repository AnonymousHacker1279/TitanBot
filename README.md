# TitanBot
## An intelligent Discord bot, written for Titan Programming

TitanBot is designed to provide various features, from utility to entertainment. While these are
tailored specifically for my Titan Programming server, they should work anywhere else.

A goal of TitanBot is to provide modularity. Modules are toggleable without having to remove portions of code.
Modules (and commands) can also be disabled at the user level, so if a pesky user is abusing a command, their
permissions can be revoked.

### Hosting TitanBot
I do not provide servers to host TitanBot anywhere other than my own server. If you wish to use TitanBot,
you will need to provide the server.

#### What TitanBot needs:
- His own operating folder
- A Python 3 installation (currently built with `3.10`, older versions may work but aren't verified)
- Some `pip` modules; Python will tell you what you need when it crashes on startup :)

You will need to create a `.env` file in the root of the operating folder. This stores environment
variables that TitanBot needs. The file should look somewhat like this:

```env
DISCORD_TOKEN=<your bot token>
DISCORD_GUILD=<a guild for your bot>
WIZARD_ROLE=<a role ID to denote users that can access higher level functions>
BOT_VERSION=v0.0.1
BOT_UPDATE_LOCATION=https://raw.githubusercontent.com/AnonymousHacker1279/TitanBot/v2.x/update.json
```

You will need to replace any text within `<>` with your own data. `BOT_VERSION` represents the current
version that is being used, while `BOT_UPDATE_LOCATION` represents a location to access an update metadata.
The bot will not auto-update, however it will tell you the current and latest versions on the `$about`
command.

To run TitanBot, simply execute the following in your terminal: `python TitanBot.py`. A message will be
logged stating that the bot has connected.

### Other Information
This really is just a side project of mine, I am not too invested into it. I will try to attend to issue
reports when I can, but it is not a priority. The only supported version is the latest one.

If you wish to contribute, please join the Titan Programming Discord server (link can be found on my profile).
We will discuss any changes.