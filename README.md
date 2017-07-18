USE OR NOT? DEPENDS ON YOU!
===========

#### From last author:

Since working on this project, I have come to the conclusion that using anything but xscreensaver is a very unwise decision ([details](http://www.jwz.org/xscreensaver/toolkits.html)). I am no longer updating this project and strongly advise against its use (or the use of the upstream branch). Since this program puts you in peril of disclosing sensitive information, I do think its general concept is a Bad Idea™. Imagine your friend bob writes an OTR-encrypted message to you via Jabber, which causes Pidgin to open a new window display the decrypted message.

If you just want to confuse/annoy people, I would suggest having xscreensaver take a screenshot when the screen is locked, which is then displayed by feh, xv or any other program capable of displaying images on X root windows. Another IMHO very nice (though seriously hacky) method is the one I described [in this gist](https://gist.github.com/jaseg/3487142): Have xscreensaver spawn an actual Windows XP VM that curious people can interact with, including automatic reset on screen unlocking.

Thanks for checking out anyway!

jaseg


#### From this author:

I am modifing this project into a simple screen lock that have more of the conviniency rather than security. It will be modified to deal with laptop lids that always touch the keyboard or someone trying to mess around with your screen when your are in the toliet. However, please carefully read the note from the last author and deside if a professional screen lock like Xscreensaver is necessary for you! Nevertheless, IMHO this program should be able to deal with routine cases secure enough. 

Please check out the releases to grab a finished version! Any contribution would be appreciated!
2017/7/13

d0048

#### Installation Guide:
##### On linux:
1. Install required libiary and tools to build the project:
Debian series: `sudo apt-get install libnotify-dev libx11-dev build-essential cmake cmake-data pkg-config`
Redhat series: `sudo yum install libnotify-dev libx11-dev build-essential cmake cmake-data pkg-config`
2. Download the correct version of source code you want and unzip it.(Probably from releases if stability is required)
3. `cd Better-XTrLock`
4. `make && sudo make install && sudo make install.man && sudo make install.bash_completion`
5. `xtrlock -h` to view usage

#### Removal Guide:
##### On linux:
1. Download the correct version of source code you want and unzip it.(Probably from releases if stability is required)
2. `cd Better-XTrLock`
3. `sudo make remove`
