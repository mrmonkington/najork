"""
Scene handles

 - Registration of all entities and ensuring consistency
 - Loading and saving of entity scenes
 - Exposing the scene to the renderer

This is a single-document-interface application, so there's only one scene
at a time, though this doesn't really need to be enforced.

"""

from .entities import (
    Entity, Anchor, Line, Slider, Circle, Intersection, Distance, Angle
)

from collections import defaultdict
import functools

class InputError(Exception):
    """ Something wrong with input scene def
    """

class Scene():

    def __init__(self):
        self._registry = {}
        self._sequences = defaultdict(lambda:1)

    def get_next_id(self, classname: str) -> str:
        """ Get a unique sequence ID with which to register
        a class (unique only for each classname)

        e.g. `get_next_id("anchor")` -> `"000001"`
        """
        uid = self._sequences[classname]
        self._sequences[classname] += 1
        # 999999 is a reasonable ceiling, but this won't break if
        # it overflows, the list just won't be as simple to sort
        return "%0.6i" % uid

    def add(self, entity: Entity):
        """ Register an entity
        """
        self._registry[entity.uid] = entity

    def get_by_id(self, uid: str) -> Entity:
        """ Fetch registered entity identified by `uid`
        """
        return self._registry[uid]

    def list_by_class(self, classname: str):
        """ List all entities registered for a given entity class
        """
        # TODO pregroup
        return [x for x in self._registry.values() if x.classname == classname]

    def list_by_rank(self, rank: int):
        """ List all entities registered for a given rank
        """
        return [x for x in self._registry.values() if x.rank == rank]

    def sort_by_rank(self):
        """ List all entities registered, ordered by ascending rank
        """
        # TODO presort
        return sorted(self._registry.values(),
                      lambda x: x.rank)

    def load_from_dict(self, scene_def: dict):
        """ Build a scene from dict `scene_def` parsed from YAML
        (order something else, we don't care)
        x angle
        x circle
        x distance
        bumper
        x slider
        x intersection
        x line
        x point
        polyline
        port
        roller
        """
        for rank in scene_def["layers"]:
            for e in rank["children"]:
                entity = None

                if e["entity"] == "point":
                    entity = Anchor(e["id"], rank["rank"], tuple(e["coords"]))

                elif e["entity"] == "line":
                    p1 = self.get_by_id(e["parents"][0])
                    p2 = self.get_by_id(e["parents"][1])
                    entity = Line(e["id"], rank["rank"], [p1, p2])

                elif e["entity"] == "circle":
                    p1 = self.get_by_id(e["centre"])
                    entity = Circle(e["id"],
                                    rank["rank"],
                                    p1,
                                    e["radius"],
                                    e["orientation"])

                elif e["entity"] == "slider":
                    par = self.get_by_id(e["parent"])
                    entity = Slider(e["id"],
                                    rank["rank"],
                                    par,
                                    e.get("position", 0.0),
                                    e.get("velocity", 0.0),
                                    e.get("loop", False),
                                    e.get("inherit_velocity", 0.0))
                elif e["entity"] == "intersection":
                    p1 = self.get_by_id(e["parents"][0])
                    p2 = self.get_by_id(e["parents"][1])
                    entity = Intersection(e["id"], rank["rank"],
                                          [p1, p2])

                elif e["entity"] == "distance":
                    p1 = self.get_by_id(e["parents"][0])
                    p2 = self.get_by_id(e["parents"][1])
                    entity = Distance(e["id"], rank["rank"],
                                      [p1, p2])

                elif e["entity"] == "angle":
                    p1 = self.get_by_id(e["parents"][0])
                    p2 = self.get_by_id(e["parents"][1])
                    entity = Distance(e["id"], rank["rank"],
                                      [p1, p2])

                else:
                    raise InputError(
                        "Unknown entity classname {}".format(e["entity"])
                    )

                if entity is not None:
                    self.add(entity)

    def save_to_dict(self) -> str:
        """ Parse YAML and load it
        """

    def create_entity(self, cls, *args, **kwargs):
        """ Factory for new entites which will
            - choose a UID
            - define rank automatically
            - register in all the right places
        """

        # TODO optimise
        max_rank = max([e.rank for e in self._registry.values()] + [0]) + 1

        uid = cls.classname + "-" + self.get_next_id(cls.classname)

        # class NewEntity(cls):
        #     __init__ = functools.partialmethod(cls.__init__, uid=uid, rank=max_rank)

        c = cls(uid, max_rank, *args, **kwargs)
        c.rank = c.calc_parent_rank() + 1
        self.add(c)
        return c

