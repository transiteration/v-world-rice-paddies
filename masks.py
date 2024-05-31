import os
import json
import shutil
import argparse
import rasterio
from rasterio.plot import show
from PIL import Image, ImageDraw

def extract_number(filename):
    return int(os.path.splitext(filename.split('_')[-1])[0])

def get_polygons_list(json_dir):    
    polygons_list = []
    for json_file in os.listdir(json_dir):
        if json_file.endswith(".json"):
            with open(os.path.join(json_dir, json_file)) as f:
                data = json.load(f)
                polygons_list.extend([feature["geometry"]["coordinates"][0][0] for feature in data["features"]])
    return polygons_list 

def draw_polygons(tiles_dir: str, masks_dir: str, miscs_dir, json_dir: str) -> None:
    polygons_list = get_polygons_list(json_dir=json_dir)
    sorted_tiles = sorted(
        [file for file in os.listdir(tiles_dir) if file.endswith(".tif")],
        key=extract_number)
    existing_masks = sorted(
        [file for file in os.listdir(masks_dir) if file.endswith(".png")],
        key=extract_number)
    
    last_processed_index = 0
    if existing_masks:
        last_processed_index = extract_number(existing_masks[-1])

    for image_file in sorted_tiles[last_processed_index:]:
        image_path = os.path.join(tiles_dir, image_file)
        mask_image_path = os.path.join(masks_dir, image_file.split(".")[0] + ".png")
        misc_image_path = os.path.join(miscs_dir, image_file)
        with rasterio.open(image_path) as src:
            image = src.read([1, 2, 3])
            extent = rasterio.plot.plotting_extent(src)
            original_resolution = (src.profile["width"], src.profile["height"])

        mask_image = Image.new("L", original_resolution, 0)
        draw = ImageDraw.Draw(mask_image)

        polygons_drawn = False
        for polygon_coords in polygons_list:
            poly_x, poly_y = zip(*polygon_coords)
            if min(poly_x) >= extent[0] and max(poly_x) <= extent[1] and min(poly_y) >= extent[2] and max(poly_y) <= extent[3]:
                poly_x = [(x - extent[0]) / (extent[1] - extent[0]) * original_resolution[0] for x in poly_x]
                poly_y = [(original_resolution[1] - (y - extent[2]) / (extent[3] - extent[2]) * original_resolution[1]) for y in poly_y]
                polygon_coords_transformed = list(zip(poly_x, poly_y))
                draw.polygon(polygon_coords_transformed, outline=255, fill=255)
                polygons_drawn = True

        if polygons_drawn:
            mask_image.save(mask_image_path)
        else:
            shutil.copy2(image_path, misc_image_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--safe_name", type=str, required=True, help="Name of your SAFE folder with saved tiles and responses.")
    args = parser.parse_args()

    tiles_dir = os.path.join("./data/tiles", args.safe_name)
    masks_dir = os.path.join("./data/masks", args.safe_name)
    miscs_dir = os.path.join("./data/miscs", args.safe_name)
    responses_dir = os.path.join("./data/responses", args.safe_name)

    os.makedirs(masks_dir, exist_ok=True)
    os.makedirs(miscs_dir, exist_ok=True)

    draw_polygons(tiles_dir=tiles_dir, masks_dir=masks_dir, miscs_dir=miscs_dir, json_dir=responses_dir)
