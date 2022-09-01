from typing import Callable, List
from pyglet.window import key
from game import resources


def four_direction_decorator(func: Callable):
    """Convenience decorator for algorithms requiring searching in four directions

    Args:
        func (function): Function to be executed four times
    """

    def wrapper(x: int, y: int, *args, **kwargs) -> List:
        # One function in path_finder requires the returned values
        returned_values = [
            func(x + 1, y, *args, **kwargs),
            func(x - 1, y, *args, **kwargs),
            func(x, y + 1, *args, **kwargs),
            func(x, y - 1, *args, **kwargs),
        ]
        return returned_values

    return wrapper


# for path_finder method

# Used to retrieve the coordinates of the tiles in the path
# 0, 1, 2, 3 represents right, left, up, down respectively
coord_dict = {
    0: lambda x, y: (x + 1, y),
    1: lambda x, y: (x - 1, y),
    2: lambda x, y: (x, y + 1),
    3: lambda x, y: (x, y - 1),
}
path_resources = resources.path_arrows_dict
arrow_dict = {
    (0, 0): "straightHorizontal",
    (0, 2): "elbowLeftUp",
    (0, 3): "elbowLeftDown",
    (1, 1): "straightHorizontal",
    (1, 2): "elbowRightUp",
    (1, 3): "elbowRightDown",
    (2, 0): "elbowRightDown",
    (2, 1): "elbowLeftDown",
    (2, 2): "straightVertical",
    (3, 0): "elbowRightUp",
    (3, 1): "elbowLeftUp",
    (3, 3): "straightVertical",
}
arrow_head_list = [
    "arrowLeft",
    "arrowRight",
    "arrowDown",
    "arrowUp",
]
arrow_image_config = {
    "straightHorizontal": (80, 40, 40, 20),
    "straightVertical": (40, 80, 20, 40),
    "elbowLeftUp": (60, 60, 40, 20),
    "elbowLeftDown": (60, 60, 40, 40),
    "elbowRightUp": (60, 60, 20, 20),
    "elbowRightDown": (60, 60, 20, 40),
    "arrowLeft": (40, 80, 0, 40),
    "arrowRight": (40, 80, 40, 40),
    "arrowDown": (80, 40, 40, 0),
    "arrowUp": (80, 40, 40, 40),
}
root_config = {
    "rootLeft": (40, 20),
    "rootRight": (0, 20),
    "rootUp": (20, 0),
    "rootDown": (20, 40),
}

# on_key_press
arrow_key_dict = {
    key.RIGHT: (1, 0),
    key.LEFT: (-1, 0),
    key.UP: (0, 1),
    key.DOWN: (0, -1),
}
