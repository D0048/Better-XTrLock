/*
 * simple-drawing.c - demonstrate drawing of pixels, lines, arcs, etc.
 *                    on a window. All drawings are done in black color
 *                    over a white background.
 */

#include <X11/Xlib.h>`

#include <stdio.h>`

#include <stdlib.h>     /* getenv(), etc. */`

#include <unistd.h>     /* sleep(), etc.  */`

#include <png.h>`



Window
create_simple_window(Display* display, int width, int height, int x, int y)

{

  int screen_num = DefaultScreen(display);

  int win_border_width = 2;

  Window win;


  win = XCreateSimpleWindow(display, RootWindow(display, screen_num),
                            x, y, width, height, win_border_width,
                            BlackPixel(display, screen_num),
                            WhitePixel(display, screen_num));

  /* make the window actually appear on the screen. */

  XMapWindow(display, win);

  /* flush all pending requests to the X server. */

  XFlush(display);

  return win;

}

GC create_gc(Display* display, Window win, int reverse_video)

{

  GC gc;                /* handle of newly created GC.  */

  unsigned long valuemask = 0;      /* which values in 'values' to  */

                    /* check when creating the GC.  */

  XGCValues values;         /* initial values for the GC.   */

  unsigned int line_width = 2;      /* line width for the GC.       */

  int line_style = LineSolid;       /* style for lines drawing and  */

  int cap_style = CapButt;      /* style of the line's edje and */

  int join_style = JoinBevel;       /*  joined lines.       */

  int screen_num = DefaultScreen(display);

  gc = XCreateGC(display, win, valuemask, &values);

  if (gc < 0) {

    fprintf(stderr, "XCreateGC: \n");

  }

  /* allocate foreground and background colors for this GC. */

  if (reverse_video) {

    XSetForeground(display, gc, WhitePixel(display, screen_num));

    XSetBackground(display, gc, BlackPixel(display, screen_num));

  }

  else {

    XSetForeground(display, gc, BlackPixel(display, screen_num));

    XSetBackground(display, gc, WhitePixel(display, screen_num));

  }


  XSetLineAttributes(display, gc, line_width, line_style, cap_style, join_style);


  XSetFillStyle(display, gc, FillSolid);

  return gc;

}

static void TeardownPng (png_structp png, png_infop info)
{

        if (png) {

                png_infop *realInfo = (info? &info: NULL);

                png_destroy_read_struct (&png, realInfo, NULL);

        }

}

void LoadPng (FILE *file, unsigned char** data, char **clipData, unsigned int *width, unsigned int *height, unsigned int *rowbytes)

{

        size_t size = 0,  clipSize = 0;

        png_structp png = NULL;

        png_infop info = NULL;

        unsigned char **rowPointers = NULL;

        int depth = 0,
            colortype = 0,
            interlace = 0,
            compression = 0,
            filter = 0;

        unsigned clipRowbytes = 0;


png = png_create_read_struct (PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);

info = png_create_info_struct (png);

        png_init_io (png, file);

        png_read_info (png, info);

        png_get_IHDR (png, info, (png_uint_32*)width, (png_uint_32*)height, &depth, &colortype, &interlace, &compression, &filter);



        *rowbytes = png_get_rowbytes (png, info);

        if (colortype == PNG_COLOR_TYPE_RGB) {

                // X hates 24bit images - pad to RGBA
                png_set_filler (png, 0xff, PNG_FILLER_AFTER);

                *rowbytes = (*rowbytes * 4) / 3;

        }

        png_set_bgr (png);


        *width = png_get_image_width (png, info);

        *height = png_get_image_height (png, info);

        size = *height * *rowbytes;

        clipRowbytes = *rowbytes/32;

        if (*rowbytes % 32)

                ++clipRowbytes;

        clipSize = clipRowbytes * *height;

        // This gets freed by XDestroyImage

        *data = (unsigned char*) malloc (sizeof (png_byte) * size);

        rowPointers = (unsigned char**) malloc (*height * sizeof (unsigned char*));

        png_bytep cursor = *data;

    int i=0,x=0,y=0;

        for (i=0; i<*height; ++i, cursor += *rowbytes)

                rowPointers[i] = cursor;

        png_read_image (png, rowPointers);

        *clipData = (char*) calloc (clipSize, sizeof(unsigned char));

        if (colortype == PNG_COLOR_TYPE_RGB) {

                memset (*clipData, 0xff, clipSize);

        } else {

                // Set up bitmask for clipping fully transparent areas

                for (y=0; y<*height; ++y, cursor+=*rowbytes) {

                        for (x=0; x<*rowbytes; x+=4) {

                                // Set bit in mask when alpha channel is nonzero

                                if(rowPointers[y][x+3])

                                        (*clipData)[(y*clipRowbytes) + (x/32)] |= (1 << ((x/4)%8));

                        }

                }

        }

        TeardownPng (png, info);

    free (rowPointers);

}

void
main(int argc, char* argv[])

{

  Display* display;     /* pointer to X Display structure.           */

  int screen_num;       /* number of screen to place the window on.  */

  Window win;           /* pointer to the newly created window.      */

  unsigned int display_width,
               display_height;  /* height and width of the X display.        */

  unsigned int width, height;   /* height and width for the new window.      */

  char *display_name = getenv("DISPLAY");  /* address of the X display.      */

  GC gc;            /* GC (graphics context) used for drawing    */

                /*  in our window.               */

  unsigned width_ = 0, height_ = 0;


        unsigned char *data = NULL;

        char *clip = NULL;

        unsigned rowbytes = 0;

        unsigned long *image, *mask;

  /* open connection with the X server. */

  display = XOpenDisplay(display_name);

  if (display == NULL) {

    fprintf(stderr, "%s: cannot connect to X server '%s'\n",
            argv[0], display_name);

    exit(1);

  }

  /* get the geometry of the default screen for our display. */
  screen_num = DefaultScreen(display);

  display_width = DisplayWidth(display, screen_num);

  display_height = DisplayHeight(display, screen_num);

  /* make the new window occupy 1/9 of the screen's size. */

  width = (display_width / 3);

  height = (display_height / 3);

  printf("window width - '%d'; height - '%d'\n", width, height);



  win = create_simple_window(display, width, height, 0, 0);


  gc = create_gc(display, win, 0);

  XSync(display, False);

/* catch expose events */

  XSelectInput(display, win, ExposureMask);

  /* wait for the expose event */

  XEvent ev;

  XNextEvent(display, &ev);

// Load image

        FILE *file = fopen ("/games/splash_image.png", "r");

        if (!file)

                return;

        LoadPng (file, &data, &clip, &width_, &height_, &rowbytes);

        if (!data)

                return;
   XImage *ximage = XCreateImage (display, DefaultVisual (display, DefaultScreen (display)), 32, ZPixmap, 0, (char*)data, width, height, 8, rowbytes);

        if (ximage) {

                XPutImage (display, win, gc, ximage, 0, 0, 0, 0, width, height);

        XNextEvent(display, &ev);

        } else {

                free (data);

        }

//        free (clip);

// Load Image end


  /* flush all pending requests to the X server. */

  XFlush(display);

  XSync(display, False);

  /* make a delay for a short period. */

  sleep(4);

  /* close the connection to the X server. */

  XCloseDisplay(display);

}
