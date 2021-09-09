"""
The Scene object handles:

 - Registration of all entities and ensuring consistency
 - Loading and saving of entity scenes
 - Exposing the scene to the engine
 - Exposing the scene to the renderer

This is a single-document-interface application, so there's only one scene
at a time, though this doesn't really need to be enforced.

A Scene is stateless once set-up (i.e. w.r.t. to `t`), and there aren't really
any re-entrancy concerns.

"""

# TODO ensure caching is similarly thread safe

from .entities import (
    Entity, Anchor, Line, Slider, Circle, Intersection,
    Distance, Angle, Control, Bumper, PolyLine
)

from collections import defaultdict
import functools


class InputError(Exception):
    """ Something wrong with input scene def
    """


class Scene():
    """ The Scene object. Creat one of these and either
    explicity add entities:

    ```
        from najork.scene import Scene
        from najork.entities import Anchor

        s = Scene()
        s.create_entity(Anchor, (1.0, 1.0))
    ```

    ...or use the loader:

    ```
        from najork.scene import Scene
        import yaml

        s = Scene()
        with open("scene.yml") as inp:
            y1 = yaml.load(inp.read(), Loader=yaml.Loader)
            s.load_from_dict(y1)
    ```

    """

    def __init__(self):
        self._registry = {}
        self._sequences = defaultdict(lambda: 1)

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

    def all(self):
        return self._registry.values()

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
                      key=lambda x: x.rank)

    def load_from_dict(self, scene_def: dict):
        """ Build a scene from dict `scene_def` parsed from YAML
        (order something else, we don't care)
        x angle
        x circle
        x distance
        x bumper
        x slider
        x intersection
        x line
        x anchor
        x polyline
        x control
        roller
        """
        for rank in scene_def["layers"]:
            for e in rank["children"]:
                entity: Entity = None

                if e["entity"] == "anchor":
                    entity = Anchor(e["id"], rank["rank"], tuple(e["coords"]))

                elif e["entity"] == "line":
                    p1 = self.get_by_id(e["parents"][0])
                    p2 = self.get_by_id(e["parents"][1])
                    entity = Line(e["id"], rank["rank"], [p1, p2])

                    # TODO default_child_velocity

                elif e["entity"] == "polyline":
                    p1 = self.get_by_id(e["parents"][0])
                    p2 = self.get_by_id(e["parents"][1])
                    midpoints = e.get("midpoints", [])
                    entity = PolyLine(e["id"], rank["rank"], [p1, p2], midpoints)

                    # TODO default_child_velocity

                elif e["entity"] == "circle":
                    p1 = self.get_by_id(e["centre"])
                    entity = Circle(e["id"],
                                    rank["rank"],
                                    p1,
                                    e["radius"],
                                    e["orientation"])

                    # TODO default_child_velocity

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
                    entity = Angle(e["id"], rank["rank"],
                                      [p1, p2])

                elif e["entity"] == "control":
                    entity = Control(e["id"], rank["rank"],
                                     e["coords"][0], e["coords"][1],
                                     e["path"].encode()
                                     )
                    for connection, input_id in e.get("connections", {}).items():
                        entity.add_input(connection, self.get_by_id(input_id))
                    entity.msg.set_data(e.get("data", []))

                elif e["entity"] == "bumper":
                    p1 = self.get_by_id(e["parent"])
                    c1 = self.get_by_id(e["collides"])
                    inherit_vel: bool = False
                    vel: float = 0.0
                    if type(e["velocity"]) == str and e["velocity"] == "inherit":
                        inherit_vel = True
                    else:
                        vel = float(e["velocity"])
                    entity = Bumper(e["id"], rank["rank"],
                                     p1,
                                     e["progression"], vel,
                                     c1,
                                     e["path"].encode(),
                                     e.get("loop", False),
                                     inherit_vel
                                     )
                    for connection, input_id in e.get("connections", {}).items():
                        entity.add_input(connection, self.get_by_id(input_id))
                    entity.msg.set_data(e.get("data", []))


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

