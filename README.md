## V-World API to get Rice Paddy Information

### How to use

1. Clone this repository:
    
    `git clone https://github.com/transiteration/v-world-rice-paddies.git`

2. Run `rice_info_api.py` with authentication key and `BBOX` arguments(example):

    `python3 rice_info_api.py --auth_key your_api_key --y_min 34.633611 --x_min 126.470000  --y_max 34.729722 --x_max 126.597500`

### Result

The sample of one future from JSON file to observe the content of the gathered information:
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

