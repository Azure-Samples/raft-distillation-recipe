def get_pdf_image(doc_path):
    from wand.image import Image as WImage
    from pathlib import Path
    img = None
    if Path(doc_path).exists() and Path(doc_path).is_file():
        img = WImage(filename=doc_path)

        # make background of img white
        img.format = 'png'
        img.background_color = 'white'
        img.alpha_channel = 'remove'
    return img
