#include<stdio.h>
#include<stdlib.h>
#include<stdbool.h>
#include<time.h>
#include<X11/Xlib.h>
#include<X11/Xutil.h>
#include<X11/Xos.h>

Display *dis;
int screen;
Window win;
GC gc;

void init_x();
bool draw_squre_screen_coord(int x1, int y1, int x2, int y2);

int main(){
        init_x();
        return 0;
}

bool draw_squre_screen_coord(int x1, int y1, int x2, int y2){
        return true;
}

void init_x() {
        unsigned long black,white;
        XSetWindowAttributes attrib;

        dis=XOpenDisplay(0);
        screen=DefaultScreen(dis);
        black=BlackPixel(dis,screen);
        white=WhitePixel(dis, screen);

        if (dis== NULL) {
                fprintf(stderr, "xtrlock: cannot open display\n");
                exit(1);
        }

        attrib.override_redirect = True;
        attrib.background_pixel = BlackPixel(dis, DefaultScreen(dis));

        /* once the display is initialized, create the window.
         *     This window will be have be 200 pixels across and 300 down.
         *         It will have the foreground white and background black
         *          */
        win=XCreateSimpleWindow(dis,DefaultRootWindow(dis),0,0,
                        200, 300, 5, white, black);
        win= XCreateWindow(dis, DefaultRootWindow(dis), /*init blank window*/
                        0, 0, DisplayWidth(dis, DefaultScreen(dis)),
                        DisplayHeight(dis, DefaultScreen(dis)),
                        0, DefaultDepth(dis, DefaultScreen(dis)), CopyFromParent, DefaultVisual(dis, DefaultScreen(dis)),
                        CWOverrideRedirect | CWBackPixel, &attrib);


        /* here is where some properties of the window can be set.
         *     The third and fourth items indicate the name which appears
         *         at the top of the window and the name of the minimized window
         *             respectively.
         *              */
        XSetStandardProperties(dis,win,"My Window","HI!",None,NULL,0,NULL);

        /* create the Graphics Context */
        gc=XCreateGC(dis, win, 0,0);

        /* here is another routine to set the foreground and background
         *     colors _currently_ in use in the window.
         *      */
        XSetBackground(dis,gc,white);
        XSetForeground(dis,gc,black);
        XMapWindow(dis,win);
        /* clear the window and bring it on top of the other windows */
        XClearWindow(dis, win);
        XMapRaised(dis, win);
        while(true){}


        /*XFreeGC(dis, gc);
          XDestroyWindow(dis,win);
          XCloseDisplay(dis);
          */
}

