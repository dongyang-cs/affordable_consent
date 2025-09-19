import path
import json

country_index_dict = json.load(open(path.DATA_DIR / "countries_enrich.json", "r"))
for k, v in country_index_dict.items():
    del v["groups"]


json.dump(country_index_dict, open(path.DATA_DIR / "country_dict.json", "w"), indent=2)
