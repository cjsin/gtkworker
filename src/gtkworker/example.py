import time
import datetime
import subprocess

from gtkworker.gtkworker import *

class ExampleButton(Gtk.VBox):
    def __init__(self, text):
        super().__init__()
        self.l = Gtk.Label(label="")
        GLib.timeout_add(500, self._timeout)
        self.b = Gtk.Button(label=text)
        self.pack_start(self.l, False, False, 0)
        self.pack_start(self.b, False, False, 0)
        self.work = GtkWorkQueue(4)
        self.b.connect("clicked", self._clicked)
        self.counter = 0

    def _timeout(self):
        self.l.set_text(self._now())
        return 1
    
    def _now(self):
        return datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    
    def _clicked(self, *_args):
        x = self.counter
        self.counter += 1
        self.work.submit(self._longrunning_work, self._done, "a", "1", x=x)
    
    def _longrunning_work(self, arg1, arg2, x=None):
        time.sleep(3)
        date = subprocess.check_output(["date"], universal_newlines=True)
        return "{} arg1={}, arg2={}, x={}".format(date, arg1, arg2, x)

    def _done(self, result):
        self.b.set_label(self._now() + " " + result)

def test_examplebutton():
    w = Gtk.Window()
    w.add(ExampleButton("click me"))
    w.show_all()
    Gtk.main()

if __name__ == "__main__":
    test_examplebutton()
