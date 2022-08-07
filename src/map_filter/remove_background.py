from PIL import Image

# mainly taken from https://stackoverflow.com/questions/765736/how-to-use-pil-to-make-all-white-pixels-transparent
def remove_background(image_path, output_path):
    img = Image.open(image_path).convert("RGBA")
    data = img.getdata()

    newData = []
    for item in data:
        if item[0] == 128 and item[1] == 160 and item[2] == 128:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    img.save(output_path)


remove_background(
    r"C:\\Users\\knpmt\\IdeaProjects\\Fire-Emblem-Clone\\resources\\characters\\Knight Lord (M) Eliwood Sword {IS}-stand.png",
    "test3.png",
)
