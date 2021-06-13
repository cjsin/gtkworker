""" example usage of gtkworker """

# pylint: disable=invalid-name

import time
import datetime
import subprocess

from gtkworker.gtkworker import Gtk, GLib, GtkWorkQueue

class ExampleButton(Gtk.VBox):
    """
    A box with a clock label and a button that starts some long running work when
    clicked, and then updates the button label with the result.
    The clock label should be updated each second.
    The button label will be updated when the work has finished (some time after clicking it).
    """
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
        # pylint: disable=no-self-use
        return datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    def _clicked(self, *_args):
        x = self.counter
        self.counter += 1
        self.work.submit(self._longrunning_work, self._done, "a", "1", x=x)

    def _longrunning_work(self, arg1, arg2, x=None):
        # pylint: disable=no-self-use
        time.sleep(3)
        date = subprocess.check_output(["date"], universal_newlines=True)
        return "{} arg1={}, arg2={}, x={}".format(date, arg1, arg2, x)

    def _done(self, result):
        self.b.set_label(self._now() + " " + result)

def test_examplebutton():
    """ Show a window with an button that can be clicked """
    w = Gtk.Window()
    w.add(ExampleButton("click me"))
    w.show_all()
    w.connect('delete-event', lambda *_args: Gtk.main_quit())
    Gtk.main()

if __name__ == "__main__":
    test_examplebutton()
