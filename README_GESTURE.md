### How to Record Your Own Lock Pattern?

#### How it works?
    This program will map an 9x9 transparent grid with custom sized gaps between the two points the user specified inside the configuration file. 
    By using the mouse to move across the grid squres, a pattern of a specify length is recorded and hashed. Once the pattern hash matches what's stored inside the config file, the program will kill the xtrlock process launched by it and exit. 


#### Overall Usage:
usage: xtrlock-gesture.py [-h] [-l LOG_LEVEL] [-f LOG_FILE] [-g GEN]
                          [-c CONFIG_FILE]

optional arguments:
  -h, --help            show this help message and exit
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        the logging level. e.g: 10 for debug, 20 for info, 30
                        for warning(default), 40 for error, 50 for critical.
  -f LOG_FILE, --log-file LOG_FILE
                        the file path to the log file
  -g GEN, --gen GEN     record pwd and generate the config file (please use -g1)
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        specify the config file to use/write, default as
                        ~/xtrlock.conf

#### Step-By-Step
1. Use `xtrlock-gesture -g1 -c [PATH/TO/CREATE/CONFIG/NAME.SUFFIX]` to generate a default config file. (You may need to use Ctrl-C to leave the program after the creation)
Note that the `-c` option is optional config file will be generated at `~/.xtrlock.conf`.

2. One a configuration file with the correct setting inside exists, run the command above again and the user should be able to enter an interactive interface. 

    Path to xtrlock installation: Should be `/usr/bin/xtrlock` by default. In case you modified the installation, use `whereis xtrlock` to be sure.
    
    Backup Password: The password that could be typed in to unlock the screen in case the pattern lock failed. (Use `Alt+Ctrl+f2` and perform the `killall xtrlock` command is another backup solution)

    X1/Y1: The First point of your 
