""" The engine:

  - advances the clock
  - warms up the scene cache
  - sends OSC messages

It uses a scheduler in a thread, which may seem a little mad
but it's the best way I've found to ensure realtime-ish delivery
of OSC packets and not spend too long burning CPU in a python loop.

"""

import sched
import threading
import time
import logging

from .scene import Scene
from .config import settings

from oscpy.client import OSCClient


CV_FRAME_TIME = 1.0 / settings["clock_rate"]

class Engine:

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, new_val: float):
        if not self._running:
            with self.state_lock:
                self._pos = new_val
        else:
            # just ignore - should we error?
            pass

    @property
    def running(self):
        return self._running

    def __init__(self, scene: Scene, settings: dict):
        self._scene = scene
        self._pos = 0.0
        self._running = False
        self._end_time = 0.0  # secs - 0 is run forever

        self.state_lock = threading.Lock()

        # use time.monotonic so NTP can't mess things up for us
        self._s = sched.scheduler(time.monotonic, time.sleep)

        self.setup_osc(settings)
        self.spawn()

    def get_scene(self) -> Scene:
        return self._scene

    def setup_osc(self, settings):
        if (
                "osc" in settings
                and "ip" in settings["osc"]
                and "port" in settings["osc"]
        ):
            ip = settings["osc"]["ip"]
            port = settings["osc"]["port"]
            logging.debug(
                "Creating OSC client to deliver to {}:{}".format(ip, port)
            )
            self._osc_client = OSCClient(ip, port)
        else:
            logging.debug("Clearing OSC client")
            self._osc_client = None

    def spawn(self):
        """ Build it up
        """
        self._alive = True
        self._t = threading.Thread(target=self._run)
        self._t.start()

    def shutdown(self):
        """ Tear it down
        """
        self.pause()
        self._alive = False
        self._t.join()

    def send_osc_msg(self, path, data):
        """ Construct and dispatch and OSC message
        to pre-configured endpoint
        """
        if self._osc_client is not None:
            logging.debug("Sending OSC message {}={}".format(path, data))
            self._osc_client.send_message(path, data)

    def _run(self):
        """ Internal thread worker
        """
        # I think this is right :-)
        # block if any events are sheduled, else just freewheel?
        # another approach is to just do a 100us sleep in a loop
        # https://github.com/ideoforms/isobar/blob/master/isobar/timeline/clock.py#L65
        while self._alive:
            self._s.run(blocking=True)
            # this loop should spend most time blocking in above call.
            # if for some reason we don't have any frames to schedule
            # then we should add some idle time to stop
            # the thread chewing up CPU
            if self._running:
                # a tick should be scheduled very shortly
                time.sleep(0.001)
            else:
                # you can chill a bit - nothing realtime
                # is happening
                time.sleep(CV_FRAME_TIME)

    def __del__(self):
        # clear all events and kill execution thread
        self.shutdown()


    def _next_time(self):
        """ Internal thread worker
        """
        return self._last + CV_FRAME_TIME

    def start(self):
        """ Start the engine running wherever the internal
        timeline clock currently is
        """
        # reset the stopclock
        self._last = time.monotonic()
        if not self._running:
            self._s.enterabs(self._next_time(), 1, self.tick)
            self._running = True

    def pause(self):
        """ Pauses the engine in a resumable way
        """
        if self._running:
            self._running = False
            # terminate any outstanding events (hopefully <= 1)
            for ev in self._s.queue:
                self._s.cancel(ev)

    def rewind(self):
        """ Pauses the engine in a resumable way
        """
        # we should pause and restart to clear any pending scheduled
        # events
        if self._running:
            self.pause()
            with self.state_lock:
                self._pos = 0.0
            self.start()
        else:
            with self.state_lock:
                self._pos = 0.0

    def tick(self):
        logging.debug("Engine::Tick")
        with self.state_lock:
            # do_engine_stuff()
            # event though our events are scheduled for frame
            # time increments, we can't rely on them arriving in
            # time, and so to ensure output is deterministic
            # we must keep out own idealised engine clock (pos)
            self._pos += CV_FRAME_TIME

        if self._end_time > 0.0 and self._pos > self._end_time:
            # end time == 0.0 means run forever
            self.pause()

        elif self._running:
            # schedule next tick straight away
            self._last = self._next_time()
            self._s.enterabs(self._next_time(), 1, self.tick)

        if self._running:
            self._triggers(self._pos)

        logging.debug(" -> Frame time: %f", self._pos)

    def _triggers(self, t: float):
        """ Iterate through all the message sending entities
        and see if they need to do anything
        """
        controls = self._scene.list_by_class("control")
        for c in controls:
            self.send_osc_msg(c.msg.get_path(t), c.msg.get_data(t))
        bumpers = self._scene.list_by_class("bumper")
        for b in bumpers:
            if b.test_collision(t, t+CV_FRAME_TIME):
                self.send_osc_msg(b.msg.get_path(t), b.msg.get_data(t))
