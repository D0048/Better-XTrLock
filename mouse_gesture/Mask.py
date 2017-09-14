import gi
from Xlib import *
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class Mask(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Hello World")
        self.darea=Gtk.DrawingArea()
        self.darea.set_size_request(3000,3000)
        self.add(self.darea)


if __name__ == "__main__":
    win = Mask()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    pass
