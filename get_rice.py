import json
import argparse
from pathlib import Path
import urllib.request as req
from urllib.parse import urlencode
from utils import get_total_features

def get_rice_info(AUTH_KEY: str,
                  y_min: str,
                  x_min: str,
                  y_max: str,
                  x_max: str) -> None:

    url = "https://api.vworld.kr/req/wfs"

    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)

    features_per_request = 1000
    total_features = get_total_features(AUTH_KEY=AUTH_KEY,
                                        y_min=y_min,
                                        x_min=x_min,
                                        y_max=y_max,
                                        x_max=x_max)    

    payload_template = {
        "SERVICE": "WFS",
        "REQUEST": "GetFeature",
        "TYPENAME": "lp_pa_cbnd_bubun",
        "BBOX": f"{y_min},{x_min},{y_max},{x_max}",
        "PROPERTYNAME": "pnu,jibun,bchk,std_sggcd,bubun,bonbun,addr,gosi_year,gosi_month,jiga,ag_geom",
        "VERSION": "2.0.0",
        "COUNT": features_per_request,
        "SRSNAME": "EPSG:4326",
        "OUTPUT": "application/json",
        "EXCEPTIONS": "text/xml",
        "KEY": AUTH_KEY
    }

    start_index = 0
    while start_index < total_features:
        try:
            payload = payload_template.copy()
            payload["STARTINDEX"] = start_index

            apiurl = url + "?" + urlencode(payload)
            response = req.urlopen(apiurl).read().decode("utf-8")
            data = json.loads(response)

            filtered_features = [feature for feature in data["features"] if "답" in feature["properties"]["jibun"] or "답" in feature["properties"]["bonbun"]]

            filtered_data = {
                "type": data["type"],
                "totalFeatures": data["totalFeatures"],
                "features": filtered_features
            }

            file_path = data_dir / f"response_{start_index}.json"
            with open(file_path, "w") as json_file:
                json.dump(filtered_data, json_file, indent=4, ensure_ascii=False)
                json_file.write("\n")
    
            print(f"Filtered response saved successfully as {file_path}")
            
        except Exception as e:
            print("An error occurred:", e)
        
        start_index += features_per_request
    print("All the Information about Rice Paddies has been gathered from the Specified Area!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--auth_key", type=str, required=True, help="Issued V-World Authentication Key")
    parser.add_argument("-x", "--x_min", type=str, required=True, help="EPSG:4326 Longtitude of Bottom-Left Box")
    parser.add_argument("-y", "--y_min", type=str, required=True, help="EPSG:4326 Latitude of Bottom-Left Box")
    parser.add_argument("-xm", "--x_max", type=str, required=True, help="EPSG:4326 Longtitude of Upper-Right Box")
    parser.add_argument("-ym", "--y_max", type=str, required=True, help="EPSG:4326 Latitude of Upper-Right Box")
    args = parser.parse_args()
    
    get_rice_info(AUTH_KEY=args.auth_key,
                       y_min=args.y_min,
                       x_min=args.x_min,
                       y_max=args.y_max,
                       x_max=args.x_max)