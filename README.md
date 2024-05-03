## V-World API to get Rice Paddy Information

### How to use V-World API to get Rice Paddy Information from Specific Area

1. Clone this repository:
    
    `git clone https://github.com/transiteration/v-world-rice-paddies.git`

2. Run `get_rice.py` with authentication key and `BBOX` arguments(example):

    `python3 get_rice.py --auth_key your_api_key --y_min 34.633611 --x_min 126.470000  --y_max 34.729722 --x_max 126.597500`

### Result

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


### How to Draw polygons on Satellite Image by using cooridinates from JSON file

First, we need to obtain the `.tiff` of the area we provided earlier. You can use [EO Browser](https://apps.sentinel-hub.com/eo-browser/) or [Copernicus Browser](https://browser.dataspace.copernicus.eu/) to get the Satellite Image. You can use this sample [image](https://drive.google.com/file/d/19QOePKGuPF2HOMnSDXN73BP0QJQSvUoJ/view?usp=sharing) to draw polygons. The area in the image corresponds to the `BBOX` provided previously when running `get_rice.py`.

Then, run this script to draw polygons on rice paddies:

`python3 to_mask.py --img_path path/to/image.tiff --out_path path/to/masked_image.png`

### Result

![Resulted Image with Polygons](https://drive.google.com/uc?export=view&id=1oFR1UXcygZJzx3cITk9t8K7h_MJJuaPg)

#### Report

Read the full [notion report](https://www.notion.so/thankscarbon/V-World-Open-API-5b36f03cef914d9b89316d4a4da3440c) here.

