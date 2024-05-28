import os
import json
import argparse
import urllib.request as req
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def get_rice_info(AUTH_KEY: str,
                  y_min: str,
                  x_min: str,
                  y_max: str,
                  x_max: str,
                  json_dir: str,
                  start_index = 0) -> None:
    url = "https://api.vworld.kr/req/wfs"
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

    def fetch_data(start):
        payload = payload_template.copy()
        payload["STARTINDEX"] = start
        apiurl = url + "?" + urlencode(payload)
        response = req.urlopen(apiurl).read().decode("utf-8")
        data = json.loads(response)
        
        filtered_features = [
            feature for feature in data["features"] 
            if feature["properties"].get("jibun") and "답" in feature["properties"]["jibun"]
            or feature["properties"].get("bonbun") and "답" in feature["properties"]["bonbun"]
        ]
        return data, filtered_features

    with ThreadPoolExecutor() as executor:
        future_to_index = {executor.submit(fetch_data, i): i for i in range(start_index, total_features, features_per_request)}
        for future in as_completed(future_to_index):
            start = future_to_index[future]
            try:
                data, filtered_features = future.result()
                if filtered_features:
                    filtered_data = {
                        "type": data["type"],
                        "totalFeatures": data["totalFeatures"],
                        "fileFeatures": len(filtered_features),
                        "features": filtered_features
                    }
                    file_path = os.path.join(json_dir, f"response_{start // 1000}.json") 
                    with open(file_path, "w") as json_file:
                        json.dump(filtered_data, json_file, indent=4, ensure_ascii=False)
                        json_file.write("\n")
                    print(f"Filtered response saved successfully as {file_path}")
                else:
                    print("No filtered features found. Skipping saving the JSON file.")
            except Exception as exc:
                print(f"Failed to fetch data for start index {start}: {str(exc)}")

    print("All the Information about Rice Paddies has been gathered from the Specified Area!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--auth_key", type=str, required=True, help="Issued V-World Authentication Key")
    parser.add_argument("-y", "--y_min", type=str, required=True, help="EPSG:4326 Latitude of Bottom-Left Box")
    parser.add_argument("-x", "--x_min", type=str, required=True, help="EPSG:4326 Longtitude of Bottom-Left Box")
    parser.add_argument("-ym", "--y_max", type=str, required=True, help="EPSG:4326 Latitude of Upper-Right Box")
    parser.add_argument("-xm", "--x_max", type=str, required=True, help="EPSG:4326 Longtitude of Upper-Right Box")
    parser.add_argument("-j", "--json_dir", type=str, required=True, help="Path to Directory to Save JSON Files")
    args = parser.parse_args()
    
    get_rice_info(AUTH_KEY=args.auth_key,
                  y_min=args.y_min,
                  x_min=args.x_min,
                  y_max=args.y_max,
                  x_max=args.x_max,
                  json_dir=args.json_dir)