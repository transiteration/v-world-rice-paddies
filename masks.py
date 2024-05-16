import os
import io
import json
import shutil
import rasterio
from PIL import Image
from rasterio.plot import show
import matplotlib.pyplot as plt

def draw_polygons(tiles_dir: str, masks_dir: str, json_dir: str, misc_dir = "./dataset/miscs") -> None:
    polygons_list = []
    for json_file in os.listdir(json_dir):
        if json_file.endswith(".json"):
            with open(os.path.join(json_dir, json_file)) as f:
                data = json.load(f)
                polygons_list.extend([feature["geometry"]["coordinates"][0][0] for feature in data["features"]])
    
    os.makedirs(masks_dir, exist_ok=True)
    for image_file in os.listdir(tiles_dir):
        if image_file.endswith(".tif"):
            image_path = os.path.join(tiles_dir, image_file)
            mask_image_path = os.path.join(masks_dir, image_file)
            misc_image_path = os.path.join(misc_dir, image_file)
            with rasterio.open(image_path) as src:
                image = src.read([1, 2, 3])
                extent = rasterio.plot.plotting_extent(src)

            fig, ax = plt.subplots(figsize=(10, 10))
            show(image, extent=extent, ax=ax)
            ax.axis("off")

            polygons_drawn = False
            for polygon_coords in polygons_list:
                poly_x, poly_y = zip(*polygon_coords)
                if min(poly_x) >= extent[0] and max(poly_x) <= extent[1] and min(poly_y) >= extent[2] and max(poly_y) <= extent[3]:
                    ax.fill(poly_x, poly_y, color="red", alpha=0.5)
                    polygons_drawn = True

            if polygons_drawn:
                buf = io.BytesIO()
                plt.savefig(buf, format="png", dpi=300, bbox_inches="tight", pad_inches=0)
                buf.seek(0)
                pil_image = Image.open(buf)

                with rasterio.open(image_path) as src:
                    original_resolution = src.profile["width"], src.profile["height"]

                pil_image = pil_image.resize(original_resolution)
                pil_image.save(mask_image_path)
                plt.close()
            else:
                # print(f"No polygons drawn for image: {image_path}, Moving to miscellaneous folder.")
                shutil.copy2(image_path, misc_image_path)
                plt.close()

SAFE_NAME = ""
tiles_dir = os.path.join("./dataset/tiles", SAFE_NAME)
masks_dir = os.path.join("./dataset/masks", SAFE_NAME)
responses_dir = os.path.join("./dataset/responses", SAFE_NAME)

draw_polygons(tiles_dir=tiles_dir, masks_dir=masks_dir, json_dir=responses_dir)
