# TitanBot
## An intelligent Discord bot, written for Titan Programming

TitanBot is designed to provide various features, from utility to entertainment. While these are
tailored specifically for my Titan Programming server, they should work anywhere else.

A goal of TitanBot is to provide modularity. Modules are toggleable without having to remove portions of code.
Modules (and commands) can also be disabled at the user level, so if a pesky user is abusing a command, their
permissions can be revoked.

Additionally, custom commands can be used to expand the functionality of the bot right from your server. See 
[the wiki for custom commands](https://github.com/AnonymousHacker1279/TitanBot/wiki/Custom-Commands).

### Hosting TitanBot
I do not provide servers to host TitanBot anywhere other than my own server. If you wish to use TitanBot,
you will need to provide the server.

#### What TitanBot needs:
- A folder to operate in
- A Python 3 installation (currently built with `3.10.7`, older versions may work but aren't verified)
- Some `pip` modules. Those can be installed from the `requirements.txt` file in the repository.

You will need to create a `.env` file in the root of the operating folder. This stores environment
variables that TitanBot needs. The file should look somewhat like this:

```txt
DISCORD_TOKEN=<your bot token>
MANAGEMENT_PORTAL_URL<your management portal URL>
```

You will need to replace any text within `<>` with your own data. 

The management portal is a new feature starting with v2.3.0 that allows you to manage your bot from a web interface.
The portal is required for the bot to operate. The source code for the portal is not yet available, but
hopefully will be soon. Until then, please use v2.2.x. Alternatively, you could attempt to reverse-engineer
the portal from the source code of TitanBot (though I'd imagine you have better things to do with your time).

To run TitanBot, simply execute the following in your terminal: `python TitanBot.py`. A message will be
logged stating that the bot has connected.

### Other Information
This really is just a side project of mine, I am not too invested into it. I will try to attend to issue
reports when I can, but it is not a priority. The only supported version is the latest one.

If you wish to contribute, please join the Titan Programming Discord server (link can be found on my profile).
We will discuss any changes.