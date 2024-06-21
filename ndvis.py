import os
import glob
import shutil
import argparse
import rasterio
import subprocess
import numpy as np
from osgeo import gdal
from rasterio.windows import Window

def read_band(band_path):
    dataset = gdal.Open(band_path, gdal.GA_ReadOnly)
    band = dataset.GetRasterBand(1).ReadAsArray()
    return band

def write_band(band, reference_path, output_path, ndvi=False):
    dataset = gdal.Open(reference_path, gdal.GA_ReadOnly)
    driver = gdal.GetDriverByName("GTiff")
    if ndvi:
        out_dataset = driver.Create(output_path, dataset.RasterXSize, dataset.RasterYSize, 1, gdal.GDT_Float32)
    else:
        out_dataset = driver.Create(output_path, dataset.RasterXSize, dataset.RasterYSize, 1, gdal.GDT_Byte)
    out_dataset.SetGeoTransform(dataset.GetGeoTransform())
    out_dataset.SetProjection(dataset.GetProjection())
    out_dataset.GetRasterBand(1).WriteArray(band)
    out_dataset.FlushCache()
    out_dataset = None

def hist_stretching(band, lower_percentile=2, upper_percentile=98, gamma=1.0):
    non_black_mask = band > 0
    non_black_band = band[non_black_mask]
    p_lower, p_upper = np.percentile(non_black_band, (lower_percentile, upper_percentile))
    band_stretched = np.zeros_like(band, dtype=np.float32)
    band_stretched[non_black_mask] = np.clip((band[non_black_mask] - p_lower) * 255.0 / (p_upper - p_lower), 0, 255)
    band_stretched[non_black_mask] = np.power(band_stretched[non_black_mask] / 255.0, gamma) * 255
    return band_stretched.astype(np.uint8)

def crop_black_borders(image_path, cropped_image_path):
    with rasterio.open(image_path) as src:
        image_array = src.read()
        if image_array.shape[0] == 1:
            band = image_array[0]
        else:
            band = image_array[0]

        non_black_pixels = band != 0
        non_black_coords = np.argwhere(non_black_pixels)
        if non_black_coords.size == 0:
            return False

        top_left = non_black_coords.min(axis=0)
        bottom_right = non_black_coords.max(axis=0)

        window = Window.from_slices(
            (top_left[0], bottom_right[0] + 1),
            (top_left[1], bottom_right[1] + 1))

        cropped_image_array = src.read(window=window)
        if cropped_image_array.shape[1] < 64 or cropped_image_array.shape[2] < 64:
            return False
        
        transform = src.window_transform(window)

        meta = src.meta.copy()
        meta.update({
            "height": cropped_image_array.shape[1],
            "width": cropped_image_array.shape[2],
            "transform": transform
        })

        with rasterio.open(cropped_image_path, "w", **meta) as dst:
            dst.write(cropped_image_array)
        return True

def process_directories(tiles_dir, sentinel_dir,):
    for safe_dir in os.listdir(sentinel_dir):
        safe_path = os.path.join(sentinel_dir, safe_dir)
        if not os.path.isdir(safe_path):
            continue

        nir_path = glob.glob(safe_path + '*/*/*/*/*/*B08_10m.jp2')[0] 
        red_path = glob.glob(safe_path + '*/*/*/*/*/*B04_10m.jp2')[0]

        refs_dir = "./data/ndvi_ref"

        os.makedirs(refs_dir, exist_ok=True)
        os.makedirs(tiles_dir, exist_ok=True)

        nir = read_band(nir_path)
        red = read_band(red_path)

        nir_hs = hist_stretching(nir)
        red_hs = hist_stretching(red)

        new_nir_path = os.path.join(os.path.dirname(nir_path), os.path.basename(nir_path).replace('.jp2', '_new_nir.tif'))
        new_red_path = os.path.join(os.path.dirname(red_path), os.path.basename(red_path).replace('.jp2', '_new_red.tif'))

        write_band(nir_hs, nir_path, new_nir_path)
        write_band(red_hs, red_path, new_red_path)

        ref_filename = os.path.basename(red_path).replace("_B04_10m.jp2", ".tif")
        ref_path = os.path.join(refs_dir, ref_filename)
        vrt_path = ref_path.replace(".tif", ".vrt")
        wgs_path = ref_path.replace(".tif", "_wgs84.tif")

        subprocess.run([
            "gdalbuildvrt",
            "-separate",
            vrt_path,
            new_nir_path,
            new_red_path, 
        ])
        subprocess.run([
            "gdal_translate",
            "-of", "GTiff",
            vrt_path,
            ref_path
        ])
        subprocess.run([
            "gdalwarp",
            "-t_srs", "EPSG:4326",
            ref_path,
            wgs_path
        ], check=True)

        os.rename(wgs_path, ref_path)
        tile_output_dir = os.path.join(tiles_dir, ref_filename.split(".")[0])
        os.makedirs(tile_output_dir, exist_ok=True)
        subprocess.run([
            "gdal_retile.py",
            "-ps", "512", "512",
            "-targetDir", tile_output_dir,
            ref_path
        ], check=True)

        for filename in os.listdir(tile_output_dir):
            if filename.endswith(".tif") or filename.endswith(".jpg"):
                input_tile_path = os.path.join(tile_output_dir, filename)
                cropped_tile_path = os.path.join(tile_output_dir, "cropped_" + filename)

                try:
                    crop_res = crop_black_borders(input_tile_path, cropped_tile_path)
                    if crop_res:
                        os.remove(input_tile_path)
                        os.rename(cropped_tile_path, input_tile_path)
                    else:
                        os.remove(input_tile_path)

                except Exception as e:
                    print(f"Error processing {filename}: {e}")

        tiles = glob.glob(os.path.join(tile_output_dir, "*.tif"))
        tiles.sort()
        for idx, tile in enumerate(tiles, start=1):
            new_name = os.path.join(tile_output_dir, f"{os.path.basename(ref_path).replace('.tif', '')}_{idx}.tif")
            os.rename(tile, new_name)

        for filename in os.listdir(tile_output_dir):
            tile_path = os.path.join(tile_output_dir, filename)
            ndvi_path = os.path.join(tile_output_dir, filename.replace(".tif", "_ndvi.tif"))
            dataset = gdal.Open(tile_path, gdal.GA_ReadOnly)
            b8 = dataset.GetRasterBand(1).ReadAsArray().astype(np.float32)
            b4 = dataset.GetRasterBand(2).ReadAsArray().astype(np.float32)
            ndvi = np.zeros_like(b8, dtype=np.float32)
            valid_mask = (b8 + b4) != 0
            ndvi[valid_mask] = (b8[valid_mask] - b4[valid_mask]) / (b8[valid_mask] + b4[valid_mask])
            ndvi = np.nan_to_num(ndvi)
            ndvi = np.clip(ndvi, -1, 1)
            write_band(ndvi, tile_path, ndvi_path, ndvi=True)
            os.remove(tile_path)
            os.rename(ndvi_path, tile_path)
        shutil.rmtree(refs_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data_path", type=str, default="./data", help="Path to create a folder with dataset")
    parser.add_argument("-s", "--sentinel_dir", type=str, default="./sentinel_folder", help="Path to directory with .SAFE folders from Copernicus Browser")
    args = parser.parse_args()
    tiles_dir = os.path.join(args.data_path, "tiles_ndvi")

    os.makedirs(args.data_path, exist_ok=True)
    os.makedirs(tiles_dir, exist_ok=True)
    
    process_directories(tiles_dir=tiles_dir,
                        sentinel_dir=args.sentinel_dir)