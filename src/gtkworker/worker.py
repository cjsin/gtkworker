#!/bin/env python3
""" Provides WorkItem and WorkQueue classes for capturing work results in a queue """
from concurrent.futures import ThreadPoolExecutor
from collections import OrderedDict
from locked_dict.locked_dict import LockedDict

class WorkItem:
    """ Data structure for capturing the work to be done and the result """
    # pylint: disable=too-few-public-methods,too-many-instance-attributes
    CREATED           = 'created'
    REGISTERED        = 'registered'
    EXECUTING         = 'executing'
    EXECUTED          = 'executed'
    EXECUTION_DONE    = 'execution-done'
    FAILED            = 'failed'
    CANCELLING        = 'cancelling'
    CANCELLED         = 'cancelled'
    RUNNING_CALLBACK  = 'running-callback'
    CALLBACK_COMPLETE = 'callback-complete'
    #DELETING          = 'deleting'
    #DELETED           = 'deleted'

    def __init__(self, func=None, callback=None, name=None, key=None, owner=None):
        # pylint: disable=too-many-arguments
        self.func = func
        self.callback = callback
        self.name = name
        self.key = key
        self.owner = owner
        self.future = None
        self.args = None
        self.kwargs = None
        self.status = WorkItem.CREATED
        self.result = None
        self.done = False
        self.exception = None
        self.cancelled = False
        self.running = False

class WorkQueue:
    """
    A queue which can have work submitted to it with a handler to be called
    when the work completes
    """
    def __init__(self, max_workers=None, completion_handler=None):
        self.max_workers = max_workers or 1
        # pylint: disable=consider-using-with
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.running = LockedDict()
        self.counter = 0
        self.completion_handler = completion_handler

    def nrunning(self):
        """
        Returns
          int - the number of tasks still running
        """
        ret = 0
        with self.running:
            ret = len(self.running)
        return ret

    def _generate_name(self):
        ret = None
        with self.running:
            ret = "{}-{}".format(id(self), self.counter)
            self.counter += 1
        return ret

    def _execute(self, workitem):
        # pylint: disable=no-self-use
        workitem.status = WorkItem.EXECUTING
        result = workitem.func(*(workitem.args), **workitem.kwargs)
        # The workitem may have been marked as being cancelled.
        # In that case we do not change the status
        if workitem.status == WorkItem.EXECUTING:
            workitem.status = WorkItem.EXECUTED
        return result

    def _register(self, workitem):
        with self.running:
            self.running[workitem.key] = workitem
            workitem.status = WorkItem.REGISTERED

    def submit(self, func, callback, *args, **kwargs):
        """
        Sumbits some work to be performed.

        Parameters:
            func : callable
                The function which performs the work
            callback: callable
                The function which will receive the results
            args
                Arguments to the func
            kwargs
                Keyword arguments to the func

        Returns:
            WorkItem : a WorkItem object encapsulating the submitted job information
        """
        workitem = WorkItem()
        workitem.func = func
        workitem.callback = callback
        workitem.owner = self
        workitem.key = self._generate_name()
        workitem.args = args
        workitem.kwargs = kwargs
        workitem.future = self.executor.submit(self._execute, workitem)
        self._register(workitem)
        workitem.future.add_done_callback(lambda f, w=workitem: self._done(w))
        return workitem

    def _callback(self, workitem):
        # pylint: disable=no-self-use
        workitem.status = WorkItem.RUNNING_CALLBACK
        workitem.callback(workitem.result)
        workitem.status = WorkItem.CALLBACK_COMPLETE

    def _run_callback(self, workitem):
        if workitem.callback:
            self._callback(workitem)

    def cancel(self, workitem):
        """
        Cancel a workitem
        """
        # pylint: disable=no-self-use
        workitem.status = WorkItem.CANCELLING
        cancel_result = workitem.future.cancel()
        return cancel_result

    def get_all(self):
        """
        Return all work items still running
        """
        items = OrderedDict()
        with self.running:
            for k in sorted(list(self.running.keys())):
                items[k] = self.running[k]
        return items

    def cancel_all(self):
        """
        Cancel all items still running
        """

        # The future.cancel() method seems to block, and therefor
        # cannot be used while self.running is locked, without causing deadlock
        # So we have to copy out the running items and then cancel them.
        for _key, workitem in self.get_all().items():
            self.cancel(workitem)

    def _done(self, workitem):
        # pylint: disable=invalid-name
        f = workitem.future
        if f.done():
            f.done = True
            if f.cancelled():
                workitem.status = WorkItem.CANCELLED
                workitem.cancelled = True
            elif f.exception():
                workitem.exception = f.exception()
                workitem.status = WorkItem.FAILED
            else:
                # python is unable to interrupt threads reasonably so
                # instead what we do here is just discard the result
                # or at least not invoke the callback, if the work item
                # was marked as being cancelled.
                if workitem.status != WorkItem.CANCELLING:
                    workitem.result = f.result()
                    workitem.status = WorkItem.EXECUTION_DONE
                    self._run_callback(workitem)
                else:
                    workitem.status = WorkItem.CANCELLED
        with self.running:
            del self.running[workitem.key]
        self._completed(workitem)

    def _completed(self, workitem):
        if self.completion_handler:
            self.completion_handler(workitem)
