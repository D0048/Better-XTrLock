from Xlib import *
#from XtrlockGuesture import *


class Size:
    x1, y1, x2, y2 = 0, 0, 0, 0

    def __init__(self, x1=0, y1=0, x2=0, y2=0):
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        pass


class ScreenMask:
    msg = ""
    display = display.Display()
    screen = display.screen()
    window = None

    def __init__(self, display, msg, size):
        self.display = display
        self.msg = msg

        self.screen = self.display.screen()
        self.window = self.screen.root.create_window(
            size.x1,  #x1
            size.y1,  #y1
            size.x2,  #x2
            size.y2,  #y2
            1,  #bd
            self.screen.root_depth,
            background_pixel=self.screen.white_pixel,
            event_mask=X.ExposureMask | X.KeyPressMask, )
        self.gc = self.window.create_gc(
            foreground=self.screen.black_pixel,
            background=self.screen.white_pixel, )

        self.window.map()

    def add_square(self, x, y, l=30, w=30):
        self.window.fill_rectangle(self.gc, x, y, l, w)
        pass

    def loop(self):
        while True:
            e = self.display.next_event()

            if e.type == X.Expose:
                self.window.draw_text(self.gc, 10, 50,
                                      str(self.msg).encode("utf-8"))
                #self.window.draw_text(self.gc, 10, 50, self.msg)
            elif e.type == X.KeyPress:
                raise SystemExit
            pass
        pass


if __name__ == "__main__":
    ScreenMask(display.Display(), "Hello, World!", Size(0, 0, 10000,
                                                        10000)).loop()
