from PIL import Image


def filter_tileset(tileset_path, tile_size, output_path):
    img = Image.open(tileset_path)  # original image
    img2 = img.convert("L")  # converted to flat color value
    pixels = img2.load()

    def is_solid_box(start_x, start_y):
        val = pixels[start_x, start_y]
        for y in range(tile_size):
            for x in range(tile_size):
                if pixels[x + start_x, y + start_y] != val:
                    return False
        return True

    # gets all non black boxes
    boxes = []
    for y in range(0, img.size[1], tile_size):
        for x in range(0, img.size[0], tile_size):
            if not is_solid_box(x, y):
                boxes.append((x, y))

    # creates blank image to edit
    new_width = img.size[0]
    new_height = len(boxes) // (new_width // tile_size) * tile_size
    padding_required = len(boxes) % (new_width // tile_size) != 0
    if padding_required:
        new_height += tile_size
    edited = Image.new("RGB", (new_width, new_height))

    # pastes non black boxes onto blank image
    curr_x, curr_y = 0, 0
    for x, y in boxes:
        edited.paste(
            img.crop((x, y, x + tile_size, y + tile_size)),
            (curr_x, curr_y, curr_x + tile_size, curr_y + tile_size),
        )
        curr_x += tile_size
        if curr_x >= new_width:
            curr_x = 0
            curr_y += tile_size

    # fills in padding row
    if padding_required:
        curr_box = 0
        for x in range(curr_x, new_width, tile_size):
            box_x, box_y = boxes[curr_box]
            curr_box += 1
            edited.paste(
                img.crop((box_x, box_y, box_x + tile_size, box_y + tile_size)),
                (x, curr_y, x + tile_size, curr_y + tile_size),
            )

    edited.save(output_path)
