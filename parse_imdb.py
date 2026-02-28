import json
import re

with open("output_utf8.html", "r", encoding="utf-8") as f:
    html_content = f.read()

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_content, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    
    movies = []
    seen_ids = set()
    
    def find_movies(d):
        if isinstance(d, dict):
            if "id" in d and str(d["id"]).startswith("tt") and "titleText" in d:
                if d["id"] not in seen_ids:
                    movies.append(d)
                    seen_ids.add(d["id"])
            for k, v in d.items():
                find_movies(v)
        elif isinstance(d, list):
            for item in d:
                find_movies(item)
                
    find_movies(data)
    
    results = []
    for node in movies:
        id_val = node.get("id", "")
        
        title = ""
        if "titleText" in node and "text" in node["titleText"]:
            title = node["titleText"]["text"]
            
        year = ""
        if "releaseYear" in node and node["releaseYear"] is not None and "year" in node["releaseYear"]:
            year = str(node["releaseYear"]["year"])
            
        rating = ""
        if "ratingsSummary" in node and node["ratingsSummary"] is not None and "aggregateRating" in node["ratingsSummary"]:
            rating = str(node["ratingsSummary"]["aggregateRating"])
            
        if id_val and title:
            results.append({
                "id": id_val,
                "title": title,
                "year": year,
                "rating": rating
            })
            
    if results:
        # Sort by popularity or just take first 25. Usually they are in order of appearance in JSON
        results = results[:25]
        with open("movies.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print("Successfully extracted Top 25 movies.")
        print(f"Found {len(movies)} movies in total.")
        print(json.dumps(results[:2], indent=2))
    else:
        print("Could not find any nodes with 'id' and 'titleText' in JSON.")

else:
    print("Could not find __NEXT_DATA__")
