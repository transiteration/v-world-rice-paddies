import os
import io
import json
import argparse
import rasterio
from PIL import Image
from rasterio.plot import show
import matplotlib.pyplot as plt

def draw_polygons(image_path: str, output_image_path: str, json_dir: str) -> None:
    polygons_list = []
    for json_file in os.listdir(json_dir):
        if json_file.endswith(".json"):
            with open(os.path.join(json_dir, json_file)) as f:
                data = json.load(f)
                polygons_list.extend([feature["geometry"]["coordinates"][0][0] for feature in data["features"]])

    with rasterio.open(image_path) as src:
        image = src.read([1, 2, 3])
        extent = rasterio.plot.plotting_extent(src)

    fig, ax = plt.subplots(figsize=(10, 10))
    show(image, extent=extent, ax=ax)

    for polygon_coords in polygons_list:
        poly_x, poly_y = zip(*polygon_coords)
        if min(poly_x) >= extent[0] and max(poly_x) <= extent[1] and min(poly_y) >= extent[2] and max(poly_y) <= extent[3]:
            ax.fill(poly_x, poly_y, color="red", alpha=0.5)

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(output_image_path)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=300, bbox_inches="tight", pad_inches=0)
    buf.seek(0)
    pil_image = Image.open(buf)

    with rasterio.open(image_path) as src:
        original_resolution = src.profile["width"], src.profile["height"]

    pil_image = pil_image.resize(original_resolution)
    pil_image.save(output_image_path)
    plt.close(fig)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--img_path", type=str, required=True, help="Path to your image .tif file")
    parser.add_argument("-o", "--out_path", type=str, required=True, help="Path to save your masked image")
    parser.add_argument("-j", "--json_dir", type=str, required=True, help="Path to Directory with JSON Files")
    args = parser.parse_args()
    
    draw_polygons(image_path=args.img_path,
                  output_image_path=args.out_path,
                  json_dir=args.json_dir)