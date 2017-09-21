#include<stdio.h>
#include<stdlib.h>
#include<stdbool.h>
#include<time.h>
#include<X11/Xlib.h>
#include<X11/Xutil.h>
#include<X11/Xos.h>

Display *dis;
int screen;
Window win,blank_win, trans_window;
GC gc;

unsigned long black,white;
XSetWindowAttributes attrib;

void init_x();
bool draw_squre_screen_coord();

int main(){
        init_x();
        while(true){}
        return 0;
}

bool draw_squre_screen_coord(int x1, int y1, int x2, int y2){
        XDrawRectangle(dis, win, gc, x1, y1, x2, y2);
        XSync(dis, False);
        return true;
}

void init_x() {
        dis=XOpenDisplay(0);
        screen=DefaultScreen(dis);
        black=BlackPixel(dis,screen);
        white=WhitePixel(dis, screen);
        if (dis== NULL) {
                fprintf(stderr, "xtrlock: cannot open display\n");
                exit(1);
        }

        attrib.override_redirect = False;
        attrib.background_pixel=white;

        blank_win= XCreateWindow(dis, DefaultRootWindow(dis), /*init blank window*/
                        0, 0, DisplayWidth(dis, DefaultScreen(dis)),
                        DisplayHeight(dis, DefaultScreen(dis)),
                        0, DefaultDepth(dis, DefaultScreen(dis)), CopyFromParent, DefaultVisual(dis, DefaultScreen(dis)),
                        CWOverrideRedirect | CWBackPixel, &attrib);
        win=blank_win;

        XMapWindow(dis,win);
        gc=XCreateGC(dis, win, 0,0);
        XSync(dis, False);
}

void close_x(){
        XFreeGC(dis, gc);
        XDestroyWindow(dis,win);
        XCloseDisplay(dis);
}
