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

#ifdef SHADOW_PWD
#include <shadow.h>
#endif

Display *display;
Window window, root;
//#define DEBUG
#ifdef DEBUG
#define debug_print(...)             \
        do {                         \
                printf(__VA_ARGS__); \
        } while (0)
#else
#define debug_print(...) \
        do {             \
        } while (0)
#endif

#define TIMEOUTPERATTEMPT 30000
#define MAXGOODWILL  (TIMEOUTPERATTEMPT*5)
#define INITIALGOODWILL MAXGOODWILL
#define GOODWILLPORTION 0.3

struct passwd *pw;
int passwordok(const char *s) {
#if 0
  char key[3];
  char *encr;
  
  key[0] = *(pw->pw_passwd);
  key[1] =  (pw->pw_passwd)[1];
  key[2] =  0;
  encr = crypt(s, key);
  return !strcmp(encr, pw->pw_passwd);
#else
  /* simpler, and should work with crypt() algorithms using longer
     salt strings (like the md5-based one on freebsd).  --marekm */
  return !strcmp(crypt(s, pw->pw_passwd), pw->pw_passwd);
#endif
        debug_print("%s, %i\n", s, (int)strlen(s));
                debug_print("Entered_de: %s\n", s);
                debug_print("Original_de: %s\n", cust_pw_setting.pwd);
                debug_print("Entered:  %s\n", enter);
                debug_print("Original: %s\n", original);
                debug_print("Entered_de:  %s\n", result);
                debug_print("Original_de: %s\n", pw->pw_passwd);
}

int main(int argc, char **argv){
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

  if (argc != 1) {
    fprintf(stderr,"xtrlock: no arguments allowed\n");
    exit(1);
  }
  
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

  for (;;) {
    XNextEvent(display,&ev);
    switch (ev.type) {
    case KeyPress:
      if (ev.xkey.time < timeout) { XBell(display,0); break; }
      clen= XLookupString(&ev.xkey,cbuf,9,&ks,0);
      switch (ks) {
      case XK_Escape: case XK_Clear:
        rlen=0; break;
      case XK_Delete: case XK_BackSpace:
        if (rlen>0) rlen--;
        break;
      case XK_Linefeed: case XK_Return:
        if (rlen==0) break;
        rbuf[rlen]=0;
        if (passwordok(rbuf)) goto loop_x;
        XBell(display,0);
        rlen= 0;
        if (timeout) {
          goodwill+= ev.xkey.time - timeout;
          if (goodwill > MAXGOODWILL) {
            goodwill= MAXGOODWILL;
          }
                debug_print("Passwd sensed:%s\n", pw->pw_passwd);
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
      }
      break;
    default:
      break;
    }
  }
 loop_x:
  exit(0);
        debug_print("Read seed from /dev/rand: %u\n", seed);
                debug_print("rand%i:%c\n", 10 - i, rand_ch());
                        debug_print("salt_generated: %s\n", f_salt);
                        debug_print("locked immidiently\n");
                        debug_print("blank_screen mode \n");
}
