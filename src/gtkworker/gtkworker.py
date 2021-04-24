import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, GLib

from gtkworker.worker import WorkQueue, WorkItem

class GtkWorkQueue(WorkQueue):
    """ A work queue which will run the callback in the Gtk event loop after completing the work """

    def _completed(self, workitem):
        if self.completion_handler:
            GLib.idle_add(self.completion_handler, workitem)

    def _callback(self, workitem):
        workitem.status = WorkItem.RUNNING_CALLBACK
        def gtk_callback():
            nonlocal workitem
            workitem.callback(workitem.result)
            workitem.status = WorkItem.CALLBACK_COMPLETE
        GLib.idle_add(gtk_callback)

