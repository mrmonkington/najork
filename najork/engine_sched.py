""" The engine:

  - advances the clock
  - warms up the scene cache
  - sends OSC messages

It uses a scheduler in a thread, which may seem a little mad
but it's the best way I've found to ensure realtime-ish delivery
of OSC packets.


"""

import sched
import threading
import time

import logging
logging.basicConfig(level=logging.DEBUG)

from .scene import Scene

from pythonosc.udp_client import SimpleUDPClient

CV_FRAME_TIME = 1.0 / 24.0  # let's do PAL for now

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

    def __init__(self, scene: Scene, settings: dict):
        self._scene = scene
        self._pos = 0.0
        self._running = False
        self._end_time = 0.0  # secs - 0 is run forever

        self.state_lock = threading.Lock()

        self._s = sched.scheduler(time.monotonic, time.sleep)

        self.setup_osc(settings)
        self.spawn()

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
            self._osc_client = SimpleUDPClient(ip, port)
        else:
            logging.debug("Clearing OSC client")
            self._osc_client = None

    def spawn(self):
        self._alive = True
        self._t = threading.Thread(target=self._run)
        self._t.start()

    def send_osc_msg(self, path, data):
        if self._osc_client is not None:
            logging.debug("Sending OSC message {}={}".format(path, data))
            self._osc_client.send_message(path, data)


    def _run(self):
        # I think this is right :-)
        # block if any events are sheduled, else just freewheel?
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

    def shutdown(self):
        self.pause()
        self._alive = False
        self._t.join()

    def next_time(self):
        return self._last + CV_FRAME_TIME

    def start(self):
        # reset the stopclock
        self._last = time.monotonic()
        if not self._running:
            self._s.enterabs(self.next_time(), 1, self.tick)
            self._running = True

    def pause(self):
        if self._running:
            self._running = False
            # terminate any outstanding events (hopefully <= 1)
            for ev in self._s.queue:
                self._s.cancel(ev)

    def rewind(self):
        # we should pause and restart to clear any pending scheduled
        # events
        self.pause()
        with self.state_lock:
            self._pos = 0.0
        self.start()

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
            self.pause()

        elif self._running:
            # schedule next tick straight away
            self._last = self.next_time()
            self._s.enterabs(self.next_time(), 1, self.tick)
