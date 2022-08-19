from pyglet.sprite import Sprite
from pyglet.gl import (
    glBindTexture,
    glTexParameteri,
    GL_TEXTURE_MAG_FILTER,
    GL_NEAREST,
    GL_SRC_ALPHA,
    GL_ONE_MINUS_SRC_ALPHA,
)


def set_texture_mag_filter(texture):
    glBindTexture(texture.target, texture.id)
    glTexParameteri(texture.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    # glTexParameteri(texture.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    # glBindTexture(texture.target, 0)


class GBASprite(Sprite):
    def __init__(
        self,
        img,
        x=0,
        y=0,
        blend_src=GL_SRC_ALPHA,
        blend_dest=GL_ONE_MINUS_SRC_ALPHA,
        batch=None,
        group=None,
        usage="dynamic",
        subpixel=False,
    ):
        super().__init__(
            img, x, y, blend_src, blend_dest, batch, group, usage, subpixel
        )
        set_texture_mag_filter(self._texture)
