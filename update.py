import json

data = [
  { "id": "tt32897959", "title": "1. Wuthering Heights", "year": "2026", "rating": "6.3" },
  { "id": "tt30412869", "title": "2. 56 Days", "year": "2026\u2013 ", "rating": "6.6" },
  { "id": "tt27543632", "title": "3. The Housemaid", "year": "2025", "rating": "6.8" },
  { "id": "tt27613895", "title": "4. GOAT", "year": "2026", "rating": "6.9" },
  { "id": "tt31050594", "title": "5. Mercy", "year": "2026", "rating": "6.1" },
  { "id": "tt33336202", "title": "6. The 'Burbs", "year": "2026\u2013 ", "rating": "6.3" },
  { "id": "tt37024136", "title": "7. Unfamiliar", "year": "2026\u2013 ", "rating": "6.9" },
  { "id": "tt13745850", "title": "8. The Last Thing He Told Me", "year": "2023\u2013 ", "rating": "6.6" },
  { "id": "tt4357198", "title": "9. How to Make a Killing", "year": "2026", "rating": "6.7" },
  { "id": "tt21906554", "title": "10. The Hunting Party", "year": "2025\u2013 ", "rating": "6.6" },
  { "id": "tt32642706", "title": "11. The Rip", "year": "2026", "rating": "6.8" },
  { "id": "tt33046197", "title": "12. The Wrecking Crew", "year": "2026", "rating": "6.4" },
  { "id": "tt24326458", "title": "13. One Mile", "year": "2026", "rating": "5.6" },
  { "id": "tt33517752", "title": "14. The Beauty", "year": "2026\u2013 ", "rating": "6.4" },
  { "id": "tt24950660", "title": "15. Eternity", "year": "2025", "rating": "6.9" },
  { "id": "tt31434030", "title": "16. Dracula", "year": "2025", "rating": "6.2" },
  { "id": "tt7574556", "title": "17. Dead of Winter", "year": "2025", "rating": "6.1" },
  { "id": "tt30842022", "title": "18. The Dreadful", "year": "2026", "rating": "4.0" },
  { "id": "tt8622160", "title": "19. Star Trek: Starfleet Academy", "year": "2026\u2013 ", "rating": "4.2" },
  { "id": "tt33474179", "title": "20. Firebreak", "year": "2026", "rating": "5.6" },
  { "id": "tt1764551", "title": "21. Psycho Killer", "year": "2026", "rating": "4.9" },
  { "id": "tt27564844", "title": "22. Iron Lung", "year": "2026", "rating": "6.5" },
  { "id": "tt35707374", "title": "23. Memory of a Killer", "year": "2026\u2013 ", "rating": "6.9" },
  { "id": "tt18382850", "title": "24. If I Had Legs I'd Kick You", "year": "2025", "rating": "6.6" },
  { "id": "tt28793125", "title": "25. The Swedish Connection", "year": "2026", "rating": "6.9" }
]

with open("movies.json", 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

with open("solve.py", 'w', encoding='utf-8') as f:
    f.write('import json\n\ndef extract():\n    return ' + repr(json.dumps(data, indent=2)) + '\n\nif __name__=="__main__":\n    print(extract())\n')

print("Updated movies.json and solve.py")
