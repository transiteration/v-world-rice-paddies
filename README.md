## V-World API to get Rice Paddy Information

### How to use V-World API to get Rice Paddy Information from Specific Area

1. Clone this repository:
    
    `git clone https://github.com/transiteration/v-world-rice-paddies.git`

2. Run `to_get_rice.py` with authentication key issued from V-World and `BBOX` argumentsexample():
```
python3 to_get_rice.py \
--auth_key your_api_key \
--y_min 34.633611 \
--x_min 126.470000 \
--y_max 34.729722 \
--x_max 126.597500 \
--json_dir path/to/save/jsons
```
***Result:***

The sample of one Feature from JSON file to observe the content of the gathered information:
```
{
    "type": "FeatureCollection",
    "totalFeatures": 40566,
    "features": [
        {
            "type": "Feature",
            "id": "lp_pa_cbnd_bubun.19132972",
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [
                                126.47847241482602,
                                34.641344934997825
                            ],
                            [
                                126.47946236983401,
                                34.64100447320692
                            ],
                            [
                                126.47904604725733,
                                34.64017185344935
                            ],
                            [
                                126.4780506371792,
                                34.640513911091304
                            ],
                            [
                                126.47847241482602,
                                34.641344934997825
                            ]
                        ]
                    ]
                ]
            },
            "geometry_name": "ag_geom",
            "properties": {
                "pnu": "4682041023110230000",
                "jibun": "1023 답",
                "bchk": "1",
                "std_sggcd": "46820",
                "bubun": null,
                "bonbun": "1023답",
                "addr": "전라남도 해남군 산이면 덕호리 1023",
                "gosi_year": "2023",
                "gosi_month": "01",
                "jiga": "8470",
                "bbox": [
                    126.4780506371792,
                    34.64017185344935,
                    126.47946236983401,
                    34.641344934997825
                ]
            }
        }
    ]
}
```

### How to Draw Polygons on Satellite Image by Using Cooridinates from JSON File

First, we need to obtain the `.tiff` of the area we provided earlier. You can use [EO Browser](https://apps.sentinel-hub.com/eo-browser/) or [Copernicus Browser](https://browser.dataspace.copernicus.eu/) to get the Satellite Image. You can use this sample [image](https://drive.google.com/file/d/19QOePKGuPF2HOMnSDXN73BP0QJQSvUoJ/view?usp=sharing). The area in the sample image corresponds to the bounding box provided previously when running `to_get_rice.py`.

Then, run this script to draw polygons on rice paddies:

`python3 to_mask.py --img_path path/to/image.tiff --out_path path/to/masked_image.png --json_dir path/to/jsons`

***Result:***

![Resulted Image with Polygons](https://drive.google.com/uc?export=view&id=1HJ8NXRdNX6835p4eEH6n7Trd3tIW5B8z)

### How to Collect a Masked Dataset 

First, download the Sentinel-2 dataset for your specific area from the [Copernicus Browser](https://browser.dataspace.copernicus.eu/). Extract the downloaded folder and place it in the `sentinel_folder` directory, or update the code to point to your custom path. Next, run `tiles.py` to apply preprocessing methods. This script will:

* Convert the dataset to the WGS84 coordinate system.
* Crop the black borders.
* Cut the dataset into tiles.

Run the following command:

`python3 tiles.py`

Secondly, when `tiles.py` is executed, it creates a JSON file containing the bounding box for the provided dataset. Use this JSON file to get all rice paddies polygons coordinates from that area by running `response.py`. 

If an error occurs while requesting data from the V-World Open API, or if it takes too long to process the whole area, you can stop the script and run it later from the previously saved JSON file.

Run the following command:

`python3 response.py`

P.S edit the script to provide the correct SAFE folder name

Finally, run `masks.py` to mask the tiles using the coordinates from the JSON files:

Run the following command:

`python3 masks.py`

P.S edit the script to provide the correct SAFE folder name

***Example of the Dataset:***

![Example of the Dataset](https://drive.google.com/uc?export=view&id=1yidZ8NWaMX_D9kcUih_0iwvsvNj0-3wS)

### Explanation in Details in Notion Report

Read the full [notion report](https://www.notion.so/thankscarbon/V-World-Open-API-5b36f03cef914d9b89316d4a4da3440c) here.

