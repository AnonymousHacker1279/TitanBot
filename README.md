# TitanBot
## An intelligent Discord bot

TitanBot is designed to provide various features, from utility to entertainment. It's mostly a fun project
to use with friends, but could be deployed anywhere. It is built with Python and utilizes the `py-cord` library.

### Hosting TitanBot
I do not provide servers to host TitanBot anywhere other than my own servers. If you wish to use TitanBot,
you will need to provide the server.

#### What TitanBot needs:
- A folder to operate in
- A Python 3 installation (currently built with `3.12.5`, older versions may work but aren't verified)
- Some `pip` modules. Those can be installed from the `requirements.txt` file in the repository.

You will need to create a `.env` file in the root of the operating folder. This stores environment
variables that TitanBot needs. The file should look somewhat like this:

```txt
DISCORD_TOKEN=<your bot token>
IPC_ADDRESS=localhost
IPC_PORT=65432
```

The `IPC_ADDRESS` and `IPC_PORT` are used for the CLI management interface, which can be accessed via the terminal
by running `python TBApp.py`.

To run TitanBot, simply execute the following in your terminal: `python TitanBot.py`. A log output will become
visible.

### Other Information
This really is just a side project of mine, I am not too invested into it. I will try to attend to issue
reports when I can, but it is not a priority. The only supported version is the latest one.