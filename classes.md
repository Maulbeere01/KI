# Klassen

## downloadMap.py
Zum Erstellen des Graphen, indem die Karte mit osmnx heruntergeladen wird.
- Koordinate im Zentrum Hamburgs angeben
- Radius um Koordinate angeben 
- Graph von Zentrum bis Radius erstellen und in hamburg.graphml speichern

## explore.py
Verwendet zum Untersuchen des Graphen von osmnx und zum Debuggen.
- lädt den erstellten Graphen rein
- gibt Typ, Knoten, Kanten aus
- gibt alle Attribute des ersten Knoten aus
    - z.B. x/y (Lon/Lat), street_count, highway, ref, railway
- gibt alle Attribute der ersten Kante aus
    - z.B. length, highway, maxspeed, oneway, reversed, geometry, lanes, osmid

## algorithms.py
Die Implementierung der verschiedenen Algorithmen für die Wegsuche durch den Graphen bzw. die Karte.
- alle Algorithmen folgen der einheitlichen Signatur: `algo(G, start, dest) -> (path, expanded)`
    - start & dest -> Knoten-IDs für Start und Ziel
    - G -> der zu untersuchende Graph

### construct_path
Rekonstruiert aus der parent-Map den gefundenen Weg vom Start zum Ziel als Knotenliste.
- rekonstruiert den Weg von Ziel bis Start rückwärts -> über parent-Verweise von Ziel bis Start
- kriegt parent-Map, Start-Knoten, Ziel-Knoten
    - parent-Map besteht aus `Key: Knoten` und `Value: Parent` -> zu jedem Knoten seinen Parent erhalten

### bfs
Die Implementierung der Breitensuche durch den Graphen.
- nutzt Breitensuche mit deque um den Weg vom Start bis zum Ziel zu finden, indem es immer weiter die benachbarten Knoten expandiert und abbricht sobald das Ziel erreicht wurde
- return
    - Erfolg:     path, expanded (Liste der betrachteten Knoten)
    - Misserfolg: None, expanded

## visualize.py
Visualisiert die Suche durch die Graphen.
Macht aus den Ergebnissen (path & expanded) eine animierte Karte -> gespeichert als GIF-Datei.
- je nach Zustand einer Karte wird sie eingefärbt
    - UNVISITED, VISITED, ACTIVE, PATH

### _edges_to_lines
Wandelt die Straßengeometrien des Graphen in zeichenbare Linien sowie Nachschlage-Strukturen zum Einfärben um.
- holt echte Straßengeometrien
- baut 3 Hilfsstrukturen
    - lines (Punktfolgen)
    - index ((u,v,key) -> Position)
    - out_edges (Knoten -> ausgehende Kanten)

### animate_search
Erzeugt aus path und expanded die animierte Karte, welche den Suchverlauf und den Weg schrittweise darstellt.
- legt alle Straßen als LineCollection an
- markiert Start/Ziel
- animiert in zwei Phasen
    1. Suchphase: pro Frame werden expandierte Knoten verarbeitet: 
        - Kanten der Knoten VISITED
        - Kanten ihrer Nachfolger ACTIVE
    2. Pfadphase: Karte leeren, Weg schrittweise weiß nachzeichnen

## metrics.py
Messskript für den Algorithmen-Vergleich. Verwendet um die Werte für die Auswertung zu erhalten.


### path_length(Graph, path)
Summiert die Straßenlänge des Weges (nimmt je Knotenpaar die kürzeste parallele Kante) und liefert die Pfadlänge in km.

### measure(Graph, start, dest, algo)
Führt den angegebenen Algorithmus einmal aus (für Kantenanzahl und expanded), misst dann die Laufzeit über `RUNS = 50` Durchläufe mit `time.perf_counter()` und mittelt sie.

### main
Lädt den Graphen, mappt START & DEST auf Knoten und gibt pro Verfahren eine Zeile aus:
algorithm, edges, expanded, ms, km
für die Tabelle.