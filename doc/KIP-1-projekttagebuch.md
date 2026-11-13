# KIP-1 – Projekttagebuch

- **Titel:** Routenplaner durch Hamburg
- **Ziel:** Kürzeste Wege zwischen zwei Knoten in einem echten Straßennetz finden und verschiedene Suchverfahren vergleichen.
- **Verfahren:** Breitensuche (BFS), bidirektionale BFS, Dijkstra, A*
- **Beispielstrecke:** HAW Hamburg zur Elbphilharmonie
- **Werkzeuge:** Python, osmnx (OpenStreetMap), matplotlib, NumPy
- **Abgabe:** 18.11.2026

## Aufbau
1. Idee
2. Projektablauf
3. Setup & Starthilfe
4. Genutzte Techniken
5. Graph-Modellierung aus OpenStreetMap
6. Warum diese Werte gewählt wurden
7. Genutzte Algorithmen
8. Vergleich der Ergebnisse
9. Herausforderungen
10. Ausblick
11. Klassen
12. Quellen


## 1. Idee

Ziel des Projekts ist ein Routenplaner, der auf dem realen Hamburger Straßennetz den kürzesten Weg zwischen zwei Punkten berechnet. Statt eines künstlichen Beispielgraphen wird das Straßennetz direkt aus OpenStreetMap geladen. So lassen sich echte Fragestellungen untersuchen, etwa wie sich verschiedene Suchalgorithmen auf einem realistischen Graphen verhalten.

Neben dem reinen Finden eines Weges steht der Vergleich der Verfahren im Vordergrund: 
- Wie viele Knoten muss ein Algorithmus untersuchen?
- Wie lange dauert die Suche?
- Welchen Einfluss hat eine Heuristik? 

Die Ergebnisse werden als Animation auf der Karte in Form eines Gif dargestellt.


## 2. Projektablauf

Das Projekt wurde schrittweise angegangen.
1. Projekt-Setup und erste Untersuchung: Projektumgebung, Karte heruntergeladen, Graph inspiziert
2. Visualiserung vorbereiten: KI-unterstützt Python-Funktionen zur Visualisierung der Algorithmen erstellt
3. Vorbereitung: einlesen in Algorithmen, notieren der Abläufe, Vorgehen und Verteilung planen
4. Erster Algorithmus: BFS implementiert
5. Visualisierung: BFS-Suche animiert dargestellt, Export als GIF
6. Weitere Algorithmen umgesetzt und visualisiert
7. Doku fortlaufend angepasst
8. Ergebnisse der Algorithmen ausgewertet


## 3. Setup & Starthilfe

Die Umgebung wird über eine virtuelle Python-Umgebung und `requirements.txt` eingerichtet. Die Karte wird einmalig mit `downloadMap.py` als `data/hamburg.graphml` gespeichert und danach von den übrigen Skripten geladen.

### Setup
```python
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
```

### Starthilfe
```python
    # 2) Karte herunterladen -> data/hamburg.graphml
    python downloadMap.py

    # 3) Suche laufen lassen + Animation erzeugen -> bfs.gif
    python visualize.py
```


## 4. Genutzte Techniken

- **osmnx:** Laden, Speichern und Durchlaufen des OpenStreetMap-Straßennetzes.
- **matplotlib:** Darstellung der Karte über `LineCollection` und Animation über `FuncAnimation`.
- **NumPy:** Effiziente Verwaltung der Kantenzustände während der Animation.
- **Pillow:** Export der Animation als GIF.
- **Virtuelle Umgebung und Pyright:** Reproduzierbares Setup und statische Typprüfung im Editor.

Der visuelle Stil der Animation wurde an ein öffentliches Beispielprojekt angelehnt (siehe Quellen; MIT-Lizenz).

Zur Erstellung von `visualize.py` um die Visualisierung der Pfadsuche zu realisieren, wurde KI verwendet. 
TODO: mehr zur Nutzung von KI um diesen Code zu erstellen?


## 5. Graph-Modellierung aus OpenStreetMap

Das Straßennetz wird mit osmnx über `graph_from_point` geladen und als `MultiDiGraph` gespeichert. Für den aktuell geladenen Ausschnitt ergibt sich:

- **Typ:** MultiDiGraph (gerichtet, Mehrfachkanten möglich)
- **Knoten:** 5.491
- **Kanten:** 12.244

Der Aufbau des Graphen ist wie folgt:

- Der Graph ist gerichtet, weil viele Straßen Einbahnstraßen sind.
- Die Mehrfachkanten entstehen, wenn zwischen zwei Knoten mehrere Straßensegmente verlaufen.. 
- Die Knoten tragen unter anderem Koordinaten (`x`/`y` als Länge/Breite) und `street_count`.
- Die Kanten besitzen Attribute wie `length`, `highway`, `oneway`, `reversed` und `geometry`.
- Die Geometrie beschreibt den tatsächlichen Straßenverlauf, der für die Darstellung genutzt wird.
- Start- und Zielpunkt werden als Koordinaten angegeben und über `nearest_nodes` auf die nächstgelegenen Knoten im Graphen abgebildet.


## 6. Warum diese Werte gewählt wurden

Für den Kartendownload werden ein Mittelpunkt in Hamburg (`53.5490, 10.0030`) und ein Radius von `5000` Metern verwendet.

Der Mittelpunkt liegt im zentralen Bereich Hamburgs, er wurde gewählt, damit die Beispielstrecke von der HAW zur Elbphilharmonie innerhalb des geladenen Gebiets liegt. Der Radius ist ein Kompromiss, das Ziel war es einen Graphen zu erhalten, der groß genug ist um sinnvolle Routen durch die Innenstadt zu ermöglichen, aber klein genug, damit der Graph mit rund 5.500 Knoten überschaubar bleibt und die Suche sowie die Animation flüssig laufen. Ein deutlich größerer Radius würde die Laufzeit und die Größe der Animation stark erhöhen.

Mit `network_type="drive"` werden nur befahrbare Straßen geladen. Das passt zum Anwendungsfall eines Routenplaners für Autos und hält den Graphen kleiner als das vollständige Wegenetz.


## 7. Genutzte Algorithmen

Alle Verfahren folgen derselben Signatur `algo(G, start, dest) -> (path, expanded)`. Zurückgegeben werden der gefundene Weg als Knotenliste sowie die Reihenfolge der untersuchten Knoten, die für die Visualisierung benötigt wird. Der Weg wird über eine `parent`-Map rekonstruiert, die zu jedem Knoten seinen Vorgänger speichert.

**Breitensuche (BFS).** Die BFS nutzt eine Queue nach dem FIFO-Prinzip und untersucht den Graphen schichtweise. Sie findet einen Weg mit möglichst wenigen Kanten. Da alle Kanten gleich behandelt werden, ist dieser Weg nicht zwingend der kürzeste gemessen an der Straßenlänge.

**Bidirektionale BFS.** Hier laufen zwei Suchen gleichzeitig: eine vorwärts vom Start und eine rückwärts vom Ziel. Sobald sich die beiden Suchfronten treffen, werden die Teilwege zu einem Gesamtweg zusammengesetzt. Dadurch muss in der Regel weniger expandiert werden als bei einer einseitigen Suche.

**Dijkstra.** Dijkstra nutzt eine Priority Queue und berücksichtigt die tatsächlichen Kantenkosten, hier die Straßenlänge. Jeder Knoten erhält die bisher bekannten Kosten `g(n)` vom Start; der jeweils günstigste Knoten wird als Nächstes expandiert. Damit ergibt sich der kürzeste Weg bezogen auf die Länge. *Status: geplant.*

**A\*.** A\* erweitert Dijkstra um eine Heuristik: `f(n) = g(n) + h(n)`. Als Schätzung der Restkosten `h(n)` bietet sich die Luftlinie zum Ziel an. Sie überschätzt die tatsächliche Straßendistanz nicht und ist damit zulässig, sodass A\* einen optimalen Weg garantiert. *Status: geplant.*

TODO: für jeden Algorithmus
- Schwächen
- Stärken
- Speicherbedarf
- Komplexität
- Voraussetzungen


## 8. Vergleich der Ergebnisse

Zum Vergleichen der verschiedenen Algorithmen wenden wir sie alle auf denselben Graphen des Hamburger Straßennetzes an und betrachten folgende Werte:

- Anzahl der untersuchten Knoten je Verfahren
- benötigte Laufzeit
- Länge des gefundenen Weges
- Auswirkung der Luftlinien-Heuristik bei A\*
- Verhalten einer bewusst überschätzenden Heuristik (schneller, aber ggf. längerer Weg)

TODO: Aufbereitung
- als Tabelle
- als animierte Karte (per visualuze.py)


## 9. Herausforderungen

- **Overpass-API ausgelastet:** Der Kartendownload schlug zeitweise mit `502 Bad Gateway` fehl, da der öffentliche Overpass-Server an seiner Kapazitätsgrenze war. Das ist kein Fehler im Code; als Lösung dienen ein erneuter Versuch, ein anderer Endpunkt oder die bereits gespeicherte `.graphml`-Datei.

TODO: Das hier dient eher als Platzfüller, vielleicht kann man noch weitere Dinge aufschreiben


## 10. Ausblick
TODO: am Ende hier vielleicht offene Dinge aufschreiben, was könnte auf der Projektgrundlage aufbauend noch machen? Was für offene Fragen gibt es?


## 11. Klassen

### downloadMap.py
zum Erstellen des Graphen / Herunterladen der Karte
- Koordinate im Zentrum Hamburgs angeben
- Radius um Koordinate angeben 
- graph von Zentrum bis Radius erstellen und in hamburg.graphml speichern

### explore.py
zum Debuggen
- lädt den erstellten Graphen rein
- gibt Typ, Knoten, Kanten aus
- gibt alle Attribute des ersten Knoten aus
    - z.B. x/y (Lon/Lat), osmid, street_count
- gibt alle Attribute der ersten Kante aus
    - z.B. length, speed_kph, highway, geometry

### algorithms.py
Wegsuche durch den Graphen / die Karte
- alle Algorithmen folgen der einheitlichen Signatur: algo(G, start, dest) -> (path, expanded)
- gegeben sind START / DEST -> Koordinaten für Start und Ziel

#### construct_path
- rekonstruirt den Weg von Ziel bis Start rückwärts -> über parent-Verweise von Ziel bis Start
- kriegt parent-Map, Start-Knoten, Ziel-Knoten
    - parent-Map -> Key: Knoten, Value: Parent -> zu jedem Knoten seinen Parent erhalten

#### bfs
- nutzt Breitensuche mit deque um Weg von Start bis Ziel zu finden indem es immer weiter die benachbarten Knoten expandiert und abbricht sobald Ziel erreicht wurde
- return
    - Erfolt:     path, expanded (Liste der betrachteten Knoten)
    - Misserfolg: None, expanded

### visualize.py
Visualisiert die Suche durch die Graphen.
Macht aus den Ergebnissen (path & expanded) eine animierte Karte -> gespeichert als gif (zB. bfs.gif)
- je nach Zustand einer Karte wird sie eingefärbt
    - UNVISITED, VISITED, ACTIVE, PATH

#### _edges_to_lines
- holt echte Straßengeometrien
- baut 3 Hilfsstrukturen
    - lines (Punktfolgen)
    - index ((u,v,key) -> Position)
    - out_edges (Knoten -> ausgehende Kanten)

#### animate_search
- legt alle Straßen als LineCollection an
- markiert Start/Ziel
- animiert in zwei Phasen
    1. Suchphase: pro Frame werden expandierte Knoten verarbeitet: 
        - Kanten der Knoten VISITED
        - Kanten ihrer Nachfolger ACTIVE
    2. Pfadphase: Karte leeren, Weg schrittweise weiß nachzeichnen


## Quellen

- osmnx-Dokumentation: https://osmnx.readthedocs.io/en/stable/
- OpenStreetMap / Overpass-API: https://wiki.openstreetmap.org/wiki/Overpass_API
- Visueller Stil der Animation, angelehnt an: https://github.com/felipearosr/Shortest_Path (MIT-Lizenz)