import json
from urllib.parse import urlencode
import urllib.request as req

def get_total_features(AUTH_KEY: str,
                       y_min: str,
                       x_min: str,
                       y_max: str,
                       x_max: str) -> int:
    
    url = "https://api.vworld.kr/req/wfs"

    payload = {
        "SERVICE": "WFS",
        "REQUEST": "GetFeature",
        "TYPENAME": "lp_pa_cbnd_bubun",
        "BBOX": f"{y_min},{x_min},{y_max},{x_max}",
        "PROPERTYNAME": "",
        "VERSION": "2.0.0",
        "COUNT": 1,
        "SRSNAME": "EPSG:4326",
        "OUTPUT": "application/json",
        "EXCEPTIONS": "text/xml",
        "KEY": AUTH_KEY
    }

    apiurl = url + "?" + urlencode(payload)
    response = req.urlopen(apiurl).read().decode("utf-8")
    data = json.loads(response)
    return data["totalFeatures"]
