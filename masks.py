import os
import json
import shutil
import argparse
import rasterio
from rasterio.plot import plotting_extent
from rasterio.transform import from_bounds
from rasterio.enums import Resampling
import numpy as np
from PIL import Image, ImageDraw


def extract_number(filename):
    return int(os.path.splitext(filename.split("_")[-1])[0])


def get_polygons_list(json_dir):
    polygons_list = []
    for json_file in os.listdir(json_dir):
        if json_file.endswith(".json"):
            with open(os.path.join(json_dir, json_file)) as f:
                data = json.load(f)
                polygons_list.extend(
                    [
                        feature["geometry"]["coordinates"][0][0]
                        for feature in data["features"]
                    ]
                )
    return polygons_list


def draw_polygons(
    tiles_dir: str, masks_dir: str, miscs_dir: str, json_dir: str
) -> None:
    polygons_list = get_polygons_list(json_dir=json_dir)
    sorted_tiles = sorted(
        [file for file in os.listdir(tiles_dir) if file.endswith(".tif")],
        key=extract_number,
    )
    existing_masks = sorted(
        [file for file in os.listdir(masks_dir) if file.endswith(".tif")],
        key=extract_number,
    )

    last_processed_index = 0
    if existing_masks:
        last_processed_index = extract_number(existing_masks[-1])

    for image_file in sorted_tiles[last_processed_index:]:
        image_path = os.path.join(tiles_dir, image_file)
        mask_image_path = os.path.join(masks_dir, image_file)
        misc_image_path = os.path.join(miscs_dir, image_file)

        with rasterio.open(image_path) as src:
            extent = plotting_extent(src)
            original_resolution = (src.width, src.height)
            transform = src.transform
            crs = src.crs

        mask_data = np.zeros(
            (original_resolution[1], original_resolution[0]), dtype=np.uint8
        )

        polygons_drawn = False
        for polygon_coords in polygons_list:
            poly_x, poly_y = zip(*polygon_coords)
            if (
                min(poly_x) >= extent[0]
                and max(poly_x) <= extent[1]
                and min(poly_y) >= extent[2]
                and max(poly_y) <= extent[3]
            ):
                poly_x = [
                    (x - extent[0]) / (extent[1] - extent[0]) * original_resolution[0]
                    for x in poly_x
                ]
                poly_y = [
                    (
                        original_resolution[1]
                        - (y - extent[2])
                        / (extent[3] - extent[2])
                        * original_resolution[1]
                    )
                    for y in poly_y
                ]
                polygon_coords_transformed = list(zip(poly_x, poly_y))

                mask_image = Image.new("L", original_resolution, 0)
                draw = ImageDraw.Draw(mask_image)
                draw.polygon(polygon_coords_transformed, outline=1, fill=1)
                mask_array = np.array(mask_image)

                mask_data = np.maximum(mask_data, mask_array)
                polygons_drawn = True

        if polygons_drawn:
            with rasterio.open(
                mask_image_path,
                "w",
                driver="GTiff",
                height=original_resolution[1],
                width=original_resolution[0],
                count=1,
                dtype="uint8",
                crs=crs,
                transform=transform,
            ) as dst:
                dst.write(mask_data, 1)
        else:
            shutil.copy2(image_path, misc_image_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--safe_name",
        type=str,
        required=True,
        help="Name of your SAFE folder with saved tiles and responses.",
    )
    args = parser.parse_args()

    tiles_dir = os.path.join("./data/tiles", args.safe_name)
    masks_dir = os.path.join("./data/masks", args.safe_name)
    miscs_dir = os.path.join("./data/miscs", args.safe_name)
    responses_dir = os.path.join("./data/responses", args.safe_name)

    os.makedirs(masks_dir, exist_ok=True)
    os.makedirs(miscs_dir, exist_ok=True)

    draw_polygons(
        tiles_dir=tiles_dir,
        masks_dir=masks_dir,
        miscs_dir=miscs_dir,
        json_dir=responses_dir,
    )
