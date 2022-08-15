from pyglet.gl import glBindTexture, glTexParameteri, GL_TEXTURE_MAG_FILTER, GL_NEAREST

TILE_SIZE = 16
TILE_SCALE = 5

CAMERA_EDGE = 2

SELECTOR_SIZE = 24

BLUE_TINT = (10, 100, 255)
RED_TINT = (255, 0, 50)
GREEN_TINT = (0, 255, 255)
NORMAL_TINT = (255, 255, 255)
GRAY_TINT = (150, 150, 150)

S_RANK = 5
DOUBLING_CONST = 4


def set_texture_mag_filter(texture):
    glBindTexture(texture.target, texture.id)
    glTexParameteri(texture.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    # glTexParameteri(
    #         texture.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST
    #     )
    # glBindTexture(texture.target, 0)
