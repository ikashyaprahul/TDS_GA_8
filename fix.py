import json

with open("movies.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

for i, obj in enumerate(data, 1):
    if not obj["title"].startswith(str(i) + ". "):
        obj["title"] = f"{i}. {obj['title']}"

with open("movies.json", 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

with open("solve.py", 'w', encoding='utf-8') as f:
    f.write('import json\n\ndef extract():\n    return ' + repr(json.dumps(data, indent=2)) + '\n\nif __name__=="__main__":\n    print(extract())\n')

print(json.dumps(data, indent=2))
