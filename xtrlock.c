/*
 * xtrlock.c
 *
 * X Transparent Lock
 *
 * Copyright (C)1993,1994 Ian Jackson
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2, or (at your option)
 * any later version.
 *
 * This is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 */

#include <X11/X.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/keysym.h>
#include <X11/Xos.h>

#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <errno.h>
#include <pwd.h>
#include <grp.h>
#include <limits.h>
#include <string.h>
#include <crypt.h>
#include <unistd.h>
#include <math.h>
#include <ctype.h>
#include <values.h>
#include <unistd.h>

#ifdef SHADOW_PWD
#include <shadow.h>
#endif

//#define DEBUG

Display *display;
Window window, root;

#define TIMEOUTPERATTEMPT 30000
#define MAXGOODWILL  (TIMEOUTPERATTEMPT*5)
#define INITIALGOODWILL MAXGOODWILL
#define GOODWILLPORTION 0.3

typedef int bool;
#define true 1
#define false 0

struct {/*Setting correspond to the custom passwd setting. --d0048*/ 
   bool enable;
   bool crypt;
   char* pwd;
} cust_pw_setting;

bool init_cust_pw(){
   cust_pw_setting.enable = false;
   return true;
}

struct passwd *pw;
int passwordok(const char *s) {
  /* simpler, and should work with crypt() algorithms using longer
     salt strings (like the md5-based one on freebsd).  --marekm */
#ifdef DEBUG        
     printf("%s, %i\n",s,(int)strlen(s)); 
#endif
     if(strlen(s) <= 1){
            printf("%s, %i\n",s,(int)strlen(s)); 
            return !strcmp("a","b");
     }
    if(cust_pw_setting.enable){
#ifdef DEBUG            
            printf("Entered_de: %s\n", s);
            printf("Original_de: %s\n", cust_pw_setting.pwd);
#endif
            char* enter = strdup(crypt(s, s));
            char* original = cust_pw_setting.pwd;
#ifdef DEBUG            
            printf("Entered: %s\n", enter);
            printf("Original: %s\n", original);
            printf("%i\n",i);
#endif
            unsigned int i = strcmp(enter, original);
            free(enter);
            return !i;
    }
  return !strcmp(crypt(s, pw->pw_passwd), pw->pw_passwd);
}

void print_help(){
        printf("Xtrlock:\n    -h show this help\n    -h                      show this help\n    -c_p [password_string]  use custom non-encrypted password\n    -c_e_p [password_hash]  use encrypted custom password with salt of itself\n    -cal [password_string]  calculate the password string that can be used with the \"-c_e_p\" option\nThanks for using!\n");
}

int lock(){
  XEvent ev;
  KeySym ks;
  char cbuf[10], rbuf[128]; /* shadow appears to suggest 127 a good value here */
  int clen, rlen=0;
  long goodwill= INITIALGOODWILL, timeout= 0;
  XSetWindowAttributes attrib;
  Cursor cursor;
  Pixmap csr;
  XColor xcolor;
  int ret;
  static char csr_bits[] = {0x00};
#ifdef SHADOW_PWD
  struct spwd *sp;
#endif
  struct timeval tv;
  int tvt, gs;

  errno=0;  pw= getpwuid(getuid());
  if (!pw) { perror("password entry for uid not found"); exit(1); }
#ifdef SHADOW_PWD
  sp = getspnam(pw->pw_name);
  if (sp)
    pw->pw_passwd = sp->sp_pwdp;
  endspent();
#endif

  /* logically, if we need to do the following then the same 
     applies to being installed setgid shadow.  
     we do this first, because of a bug in linux. --jdamery */ 
  setgid(getgid());
  /* we can be installed setuid root to support shadow passwords,
     and we don't need root privileges any longer.  --marekm */
  setuid(getuid());

  if (strlen(pw->pw_passwd) < 13) {
    fputs("password entry has no pwd\n",stderr); exit(1);
  }
  
  display= XOpenDisplay(0);

  if (display==NULL) {
    fprintf(stderr,"xtrlock: cannot open display\n");
    exit(1);
  }

  attrib.override_redirect= True;
  window= XCreateWindow(display,DefaultRootWindow(display),
                        0,0,1,1,0,CopyFromParent,InputOnly,CopyFromParent,
                        CWOverrideRedirect,&attrib);
                        
  XSelectInput(display,window,KeyPressMask|KeyReleaseMask);



  csr= XCreateBitmapFromData(display,window,csr_bits,1,1);

  cursor= XCreatePixmapCursor(display,csr,csr,&xcolor,&xcolor,1,1);

  XMapWindow(display,window);

  /*Sometimes the WM doesn't ungrab the keyboard quickly enough if
   *launching xtrlock from a keystroke shortcut, meaning xtrlock fails
   *to start We deal with this by waiting (up to 100 times) for 10,000
   *microsecs and trying to grab each time. If we still fail
   *(i.e. after 1s in total), then give up, and emit an error
   */
  
  gs=0; /*gs==grab successful*/
  for (tvt=0 ; tvt<100; tvt++) {
    ret = XGrabKeyboard(display,window,False,GrabModeAsync,GrabModeAsync,
			CurrentTime);
    if (ret == GrabSuccess) {
      gs=1;
      break;
    }
    /*grab failed; wait .01s*/
    tv.tv_sec=0;
    tv.tv_usec=10000;
    select(1,NULL,NULL,NULL,&tv);
  }
  if (gs==0){
    fprintf(stderr,"xtrlock: cannot grab keyboard\n");
    exit(1);
  }

  if (XGrabPointer(display,window,False,(KeyPressMask|KeyReleaseMask)&0,
               GrabModeAsync,GrabModeAsync,None,
               cursor,CurrentTime)!=GrabSuccess) {
    XUngrabKeyboard(display,CurrentTime);
    fprintf(stderr,"xtrlock: cannot grab pointer\n");
    exit(1);
  }

  for (;;) {/*start checker loop*/
    XNextEvent(display,&ev);
    switch (ev.type) {
        case KeyPress:
            if (ev.xkey.time < timeout) { XBell(display,0); break; }
            clen= XLookupString(&ev.xkey,cbuf,9,&ks,0);
            switch (ks) {
                case XK_Escape: 
                case XK_Clear:
                    rlen=0; break;
                case XK_Delete: 
                case XK_BackSpace:
                    if (rlen>0) rlen--;
                    break;
                case XK_Linefeed: 
                case XK_Return:
                    if (rlen==0) break;
                    else rbuf[rlen]=0;
                    if (passwordok(rbuf)) goto loop_x;
                    XBell(display,0);
                    rlen= 0;
                    if (timeout) {
                        goodwill+= ev.xkey.time - timeout;
                    if (goodwill > MAXGOODWILL) {
                        goodwill= MAXGOODWILL;
                    }
                    }
                    timeout= -goodwill*GOODWILLPORTION;
                    goodwill+= timeout;
                    timeout+= ev.xkey.time + TIMEOUTPERATTEMPT;
                    break;
                default:
                if (clen != 1) break;
                /* allow space for the trailing \0 */
	            if (rlen < (sizeof(rbuf) - 1)){
	                rbuf[rlen]=cbuf[0];
	                rlen++;
	            }
                break;
            }break;

        default: break;
    }
  }/*end checker loop*/
 loop_x:/*loop exit*/
  exit(0);
}

int main(int argc, char **argv){
        /*area for any arg init*/
    if(!init_cust_pw
    ){  fprintf(stderr,"Failed to init custom password config");
        exit(-1);}
        /*area for any arg init*/

        char opt = 0;/*TODO: learn getopti, refine system|fix changes*/
        while((opt = getopt(argc, argv, "h:l:p:e:c")) != -1){

                if('h' == opt){/*help*/
                    print_help();
                    exit(0);
                }
                if('l' == opt){/*log actions*/
                    //TODO: add log file
                }
                if('p' == opt){/*custom pwd without encryption*/
                    cust_pw_setting.enable = true;
                    //cust_pw_setting.pwd = crypt(argv[2], argv[2]);
                    cust_pw_setting.pwd = strdup(crypt(optarg, optarg));/*never freed, fine in this case*/
                    cust_pw_setting.crypt = false;
                    lock();
                }
                if('e' == opt){/*custom pwd encrypted already*/
                    cust_pw_setting.enable = true;
                    cust_pw_setting.pwd = optarg;
                    cust_pw_setting.crypt = true;
                    lock();
                }
                if('c' == opt){/*encryption of pwd*/
                    printf("%s\n", crypt(optarg, optarg));
                    exit(0);
                }
        
        }
    print_help();
    exit(0);

}

