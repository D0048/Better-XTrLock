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
bool draw_squre_screen_coord(int x1, int y1, int x2, int y2);
void mask_show();
void mask_hide();
void close_x();
int abs(int a);

int main(){
        init_x();
        draw_squre_screen_coord(0,0,100,100);
        draw_squre_screen_coord(100,100,200,200);
        draw_squre_screen_coord(200,200,300,300);
        while(true){}
        return 0;
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

        attrib.override_redirect = True;/*full screen*/
        attrib.background_pixel=white;

        blank_win= XCreateWindow(dis, DefaultRootWindow(dis), /*init blank window*/
                        0, 0, DisplayWidth(dis, DefaultScreen(dis)),
                        DisplayHeight(dis, DefaultScreen(dis)),
                        0, DefaultDepth(dis, DefaultScreen(dis)), CopyFromParent, DefaultVisual(dis, DefaultScreen(dis)),
                        CWOverrideRedirect | CWBackPixel, &attrib);
        win=blank_win;

        gc=XCreateGC(dis, win, 0,0);
        XSync(dis, False);
}
bool draw_squre_screen_coord(int x1, int y1, int x2, int y2){
        int x=(x1+x2)/2;
        int y=(y1+y2)/2;
        int sizex=abs(x1-x2)/2;
        int sizey=abs(y1-y2)/2;
        XDrawRectangle(dis, win, gc, x, y, sizex, sizey);
        XSync(dis, False);
        return true;
}

void mask_show(){
        XMapWindow(dis,win);
}
void mask_hide(){
        XUnmapWindow(dis,win);
}


void close_x(){
        XFreeGC(dis, gc);
        XDestroyWindow(dis,win);
        XCloseDisplay(dis);
}

int abs(int a){
        if(a<0) return -a;
        else return a;
}
