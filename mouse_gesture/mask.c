#include<stdio.h>
#include<stdlib.h>
#include<stdbool.h>
#include<time.h>
#include<X11/Xlib.h>
#include<X11/Xutil.h>
#include<X11/Xos.h>

#define OVERRIDE True
//#define OVERRIDE False

/*#define DEBUG*/

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


Display *display;
int screen;
Window win,blank_win, trans_window;
GC gc;

unsigned long black,white,bgcol,fgcol;
XSetWindowAttributes attrib;
void init_x();
bool square_screen_coord(int x1, int y1, int x2, int y2,unsigned long col);
bool draw_square_screen_coord(int x1, int y1, int x2, int y2);
bool erase_square_screen_coord(int x1, int y1, int x2, int y2);
void mask_show();
void mask_hide();
void mask_clear();
void put_str(char* txt,int x, int y);
void close_x();
int abs(int a);

/** Notice: Square coordinate starts from -100,-100 to wid,hei**/

int main(){
    init_x();
    mask_show();
    draw_square_screen_coord(0,0,100,100);
    erase_square_screen_coord(0,0-10,100+10,100+10);
    draw_square_screen_coord(-100,-100,100,100);
    draw_square_screen_coord(100,100,200,200);
    draw_square_screen_coord(200,200,300,300);
    put_str("this is a test",10,10);
    while(true){}
    return 0;
}

void init_x() {
    display=XOpenDisplay(0);
    screen=DefaultScreen(display);
    black=BlackPixel(display,screen);
    white=WhitePixel(display, screen);
    if (display== NULL) {
        fprintf(stderr, "xtrlock: cannot open displayplay\n");
        exit(1);
    }

    attrib.override_redirect = OVERRIDE;/*full screen*/
    attrib.background_pixel=white;

    blank_win= XCreateWindow(display, DefaultRootWindow(display), /*init blank window*/
            0, 0, DisplayWidth(display, DefaultScreen(display)),
            DisplayHeight(display, DefaultScreen(display)),
            0, DefaultDepth(display, DefaultScreen(display)), CopyFromParent, DefaultVisual(display, DefaultScreen(display)),
            CWOverrideRedirect | CWBackPixel, &attrib);
    win=blank_win;
    //XMapWindow(display,win);
    gc=XCreateGC(display, win, 0,0);
    XSetBackground(display,gc,bgcol=white);
    XSetForeground(display,gc,fgcol=black);
    XSync(display, False);
}
bool erase_square_screen_coord(int x1, int y1, int x2, int y2){
    square_screen_coord(x1,y1,x2,y2,bgcol);
}

bool draw_square_screen_coord(int x1, int y1, int x2, int y2){
    square_screen_coord(x1,y1,x2,y2,fgcol);
}

bool square_screen_coord(int x1, int y1, int x2, int y2,unsigned long col){
    XSetForeground(display,gc,col);
    int x=(x1+x2)/2;
    int y=(y1+y2)/2;
    int sizex=abs(x1-x2)/2;
    int sizey=abs(y1-y2)/2;
    XDrawRectangle(display, win, gc, x, y, sizex, sizey);
    XSync(display, False);
    return true;
}

void mask_show(){
    debug_print("Mask show\n");
    XMapWindow(display,win);
    XSync(display, False);
}
void mask_hide(){
    debug_print("Mask hide\n");
    XUnmapWindow(display,win);
    XSync(display, False);
}


void close_x(){
    debug_print("Closed and released\n");
    XFreeGC(display, gc);
    XDestroyWindow(display,win);
    XCloseDisplay(display);
}

void mask_clear(){
    debug_print("Mask cleared\n");
    XClearWindow(display, win);
}

void put_str(char* txt, int x, int y){
    XDrawString(display, win, gc, x, y, txt, strlen(txt));
    XFlush(display);
    debug_print("Added \"%s\" on the screen\n",txt);
}


int abs(int a){
    if(a<0) return -a;
    else return a;
}
