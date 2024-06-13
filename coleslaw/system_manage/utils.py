from PIL import ImageOps, Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

def resize_with_padding(img, expected_size=(1280, 1280), fill=(255,255,255)):
    '''
        Pillow > 10.0.0 (Image.Resampling.LANCZOS)
        Pillow < 10.0.0 (Image.ANTIALIAS)
    '''

    img.thumbnail((expected_size[0], expected_size[1]), Image.Resampling.LANCZOS)

    delta_width = expected_size[0] - img.size[0]
    delta_height = expected_size[1] - img.size[1]
    pad_width = delta_width // 2
    pad_height = delta_height // 2

    padding = (
        pad_width,
        pad_height,
        delta_width - pad_width,
        delta_height - pad_height,
    )
    img = img.convert("RGBA")
    return ImageOps.expand(img, padding, fill=fill)
