USE OR NOT? DEPENDS ON YOU!
===========

#### From last author:

Since working on this project, I have come to the conclusion that using anything but xscreensaver is a very unwise decision ([details](http://www.jwz.org/xscreensaver/toolkits.html)). I am no longer updating this project and strongly advise against its use (or the use of the upstream branch). Since this program puts you in peril of disclosing sensitive information, I do think its general concept is a Bad Idea™. Imagine your friend bob writes an OTR-encrypted message to you via Jabber, which causes Pidgin to open a new window display the decrypted message.

If you just want to confuse/annoy people, I would suggest having xscreensaver take a screenshot when the screen is locked, which is then displayed by feh, xv or any other program capable of displaying images on X root windows. Another IMHO very nice (though seriously hacky) method is the one I described [in this gist](https://gist.github.com/jaseg/3487142): Have xscreensaver spawn an actual Windows XP VM that curious people can interact with, including automatic reset on screen unlocking.

Thanks for checking out anyway!

jaseg


#### From this author:

I am modifying this project into a simple screen lock that have more of the convenience rather than security. It will be modified to deal problems like the lid of a laptop keep touching the keyboard, one looking for some screensaver allows custom hashed password, or for users who don't have an keyboard and decided to unlock their screen by drawing invisible patterns(testing). However, please carefully read the note from the last author(which I highly agrees) and decide if a professional screen lock like Xscreensaver is necessary for you! Nevertheless, IMHO this program should be able to deal with routine cases secure enough.

Please check out the releases to grab a finished version! Any contribution would be appreciated!
2017/9/19

d0048

#### Basic Installation Guide:
##### On linux:
1. Install required libiary and tools to build the project:
Debian series: `sudo apt-get install bash-completion libnotify-dev libx11-dev build-essential cmake cmake-data pkg-config`
        Redhat series: `sudo dnf install bash-completion libnotify-dev libx11-dev build-essential cmake cmake-data pkg-config`
2. Download the correct version of source code you want and unzip it.(Probably from releases if stability is required)
3. `cd Better-XTrLock`
4. `make && sudo make install` to install the main binaries.
5. To install the manual for xtrlock, `sudo make install.man`. Then use `man xtrlock` to read the manual.
6. To install the auto completion support for bash 'sudo make install.bash_completion`
7. To trigger xtrlock on lid close, `sudo make install.on_lid LID_CMD='lock_command_with_args'`.(e.g: `LID_CMD='xtrlock -l -n'`). If no command specified, `xtrlock -l` will be used.
8. `xtrlock -h` to view usage

#### Basic Removal Guide:
##### On linux:
1. Download the correct version of source code you want and unzip it.(Probably from releases if stability is required)
2. `cd Better-XTrLock`
3. `sudo make remove`

#### Mouse Gesture Lock Support installation Guide(Alpha):
##### On linux:
1. Finish the basic installation above.
2. Make sure you have `Python3` and `Pip` installed. If not, try install it using `sudo apt install python3.5 python3-pip` (on debian/ubuntu).
3. Install the required dependencies using pip. `sudo pip install python-pip`
4. Install the python scripts to place. `sudo make install.gesture_support`
5. Use this Guide to record your own pattern into the config file:

[![Pattern Lock Usage](https://cdn2.iconfinder.com/data/icons/buttons-9/128/Button_Next-01.png)](https://github.com/D0048/Better-XTrLock/blob/master/doc/README_GESTURE.md)<br>
