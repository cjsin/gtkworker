#!/bin/env python3
import time
import datetime
import subprocess
import random
import types
from collections.abc import Iterable

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import GLib, Gtk

from gtkworker.gtkworker import GtkWorkQueue

def datestr(d):
    return d.strftime("%Y-%m-%d-%H-%M-%S")

def now():
    return datetime.datetime.now()

def do_work():
    try:
        sleepsec = random.randint(0,500) / 100.0 
        cmd = [ "sleep", str(sleepsec) ]
        #cmd = [ "find", "/usr" ]
        p = subprocess.Popen(cmd)
        p.wait()
        return datestr(now())
    except:
        return None

def return_1(func):
    def ret():
        func()
        return 1
    return ret

def return_0(func):
    def ret():
        func()
        return 0
    return ret

class AttrTableModel(Gtk.ListStore):
    def _cell(self, rowobj, attrname):
        v = getattr(rowobj, attrname)
        if type(v) == types.MethodType:
            v = v()
        if v is None:
            v = ""
        else:
            v = str(v)
        return v

    def __init__(self, columns, items=None):
        if items is None:
            items = []
        self.columns = columns
        datatypes = [str for c in columns]
        super().__init__(*datatypes)
        self.add_all(items)

    def add_object(self, o):
        self.append([ self._cell(o, c) for c in self.columns])

    def add_all(self, items):
        if isinstance(items, dict):
            for i in items.values():
                self.add_object(i)
        elif isinstance(items, Iterable):
            for i in list(items):
                self.add_object(i)
        else:
            raise ValueError("Bad argument to add_all" + str(items))

class ObjAttrTreeView(Gtk.TreeView):
    def __init__(self, model=None):
        super().__init__(model=model)
        columns = model.columns
        for idx, name in enumerate(columns):
            column = Gtk.TreeViewColumn(name, Gtk.CellRendererText(), text=idx)
            column.xalign = 1.0
            column.set_alignment(1.0)
            self.append_column(column)
        self.set_grid_lines(True)
        self.set_headers_visible(True)
        self.show()

class TestWindow(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.work = GtkWorkQueue(max_workers=5, completion_handler=self._completed)
        self.box = Gtk.VBox()
        self.box.show()
        self.status = self._label()
        self.when = self._label()
        self.box.pack_start(self._button("Start"), False, False, 0)
        self.box.pack_start(self.when, False, False, 0)
        self.columns = [ "key", "status", "result", "exception" ]
        self.running = self._create_model()
        self.completed = []
        self.rview = ObjAttrTreeView(model=self.running)
        self.cview = ObjAttrTreeView(model=self._create_model())
        self.box.pack_start(self._label("Running:"), False, False, 2)
        self.box.pack_start(self.rview, True, True, 0)
        self.box.pack_start(self._label("Completed:"), False, False, 2)
        self.box.pack_start(self.cview, True, True, 0)
        self.box.pack_start(self.status, False, False, 0)
        self.box.pack_start(self._button("Cancel"), False, False, 0)
        self.box.pack_start(self._button("Quit"), False, False, 0)
        self.add(self.box)
        GLib.timeout_add(1000, return_1(self._update_gui))
        self.show()

    def _completed(self, workitem):
        self.completed.append(workitem)
        self._update_gui()

    def _create_model(self, values=None):
        return AttrTableModel(self.columns, values)

    def _update_models(self):
        self.running = self._create_model(self.work.get_all().values())
        self.rview.set_model(self.running)
        self.cview.set_model(self._create_model(self.completed))

    def _label(self, text=None):
        if text is None:
            text = ""
        lbl = Gtk.Label(label=text)
        lbl.show()
        return lbl

    def _button(self, text):
        btn = Gtk.Button(label=text)
        btn.connect("clicked", getattr(self, "_"+text.lower()))
        btn.show()
        return btn

    def _update_gui(self):
        self._update_text()
        self._update_models()

    def _update_text(self):
        self.when.set_text("{} [{}]".format(datestr(now()), self.work.nrunning()))

    def _done(self, *args):
        self.status.set_text(args[0])
        self._update_gui()

    def _start(self, *_args):
        self.work.submit(do_work, self._done)
        self._update_gui()
    
    def _cancel(self, *_args):
        self.work.cancel_all()
        self._update_gui()

    def _quit(self, *_args):
        self.work.cancel_all()
        Gtk.main_quit()

def test_gtk_futures():
    w = TestWindow()
    w.present()
    Gtk.main()

if __name__ == "__main__":
    test_gtk_futures()
