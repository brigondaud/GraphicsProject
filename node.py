from transform import *
from itertools import cycle
from bisect import bisect_left      # search sorted keyframe lists

# ------------  Scene object classes ------------------------------------------
class KeyFrames:
    """ Stores keyframe pairs for any value type with interpolation_function"""
    def __init__(self, time_value_pairs, interpolation_function=lerp):
        if isinstance(time_value_pairs, dict):  # convert to list of pairs
            time_value_pairs = time_value_pairs.items()
        keyframes = sorted(((key[0], key[1]) for key in time_value_pairs))
        self.times, self.values = zip(*keyframes)  # pairs list -> 2 lists
        self.interpolate = interpolation_function

    def value(self, time):
        """ Computes interpolated value from keyframes, for a given time """

        # 1. ensure time is within bounds else return boundary keyframe
        if time <= self.times[0]:
            return self.values[0]
        elif time >= self.times[-1]:
            return self.values[-1]
        # 2. search for closest index entry in self.times, using bisect_left function
        i = bisect_left(self.times, time) - 1
        # 3. using the retrieved index, interpolate between the two neighboring values
        # in self.values, using the initially stored self.interpolate function
        fraction = (time - self.times[i]) / (self.times[i+1] - self.times[i])
        return self.interpolate(self.values[i], self.values[i+1], fraction)

class TransformKeyFrames:
    """ KeyFrames-like object dedicated to 3D transforms """
    def __init__(self, translate_keys, rotate_keys, scale_keys):
        """ stores 3 keyframe sets for translation, rotation, scale """
        self.translate = KeyFrames(translate_keys)
        self.rotate = KeyFrames(rotate_keys, quaternion_slerp)
        self.scale = KeyFrames(scale_keys)

    def value(self, time):
        """ Compute each component's interpolation and compose TRS matrix """
        t = self.translate.value(time)
        q = self.rotate.value(time)
        s = self.scale.value(time)
        mat = translate(t[0], t[1], t[2]) @ quaternion_matrix(q) @ scale(s, s, s)
        return mat

class Node:
    """ Scene graph transform and parameter broadcast node """
    def __init__(self, name='', children=(), transform=identity(), **param):
        self.transform, self.param, self.name = transform, param, name
        self.children = list(iter(children))

    def add(self, *drawables):
        """ Add drawables to this node, simply updating children list """
        self.children.extend(drawables)

    def draw(self, projection, view, model, **param):
        """ Recursive draw, passing down named parameters & model matrix. """
        # merge named parameters given at initialization with those given here
        param = dict(param, **self.param)
        model = model @ self.transform
        for child in self.children:
            child.draw(projection, view, model, **param)
            
    def print_pretty(self, indent="") :
        print(indent, self)
        for child in self.children:
            child.print_pretty(indent + "==")


class KeyFrameControlNode(Node):
    """ Place node with transform keys above a controlled subtree """
    def __init__(self, translate_keys, rotate_keys, scale_keys, **kwargs):
        super().__init__(**kwargs)
        self.keyframes = TransformKeyFrames(translate_keys, rotate_keys, scale_keys)

    def draw(self, projection, view, model, **param):
        """ When redraw requested, interpolate our node transform from keys """
        self.transform = self.keyframes.value(glfw.get_time())
        super().draw(projection, view, model, **param)


class RotationControlNode(Node):
    def __init__(self, key_up, key_down, axis, angle=0, **param):
        super().__init__(**param)   # forward base constructor named arguments
        self.angle, self.axis = angle, axis
        self.key_up, self.key_down = key_up, key_down

    def draw(self, projection, view, model, win=None, **param):
        assert win is not None
        self.angle += 2 * int(glfw.get_key(win, self.key_up) == glfw.PRESS)
        self.angle -= 2 * int(glfw.get_key(win, self.key_down) == glfw.PRESS)
        self.transform = rotate(self.axis, self.angle)

        # call Node's draw method to pursue the hierarchical tree calling
        super().draw(projection, view, model, win=win, **param)
