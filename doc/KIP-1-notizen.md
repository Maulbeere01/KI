KIP-1

# Idee
Routenplaner durch Hamburg 

# Verteilung
- BFS, Bidirektional -> Ben
- Dijkstra, A* -> Raffael

# Tagebuch
- Idee
- Ablauf: Setup, erste Suche
- wie Graph von OSM modelliert ist (gerichtet)
- genutzte Techniken (KI für visualize.py)
- warum Werte so gewählt (Zentrum der Karte, Radius)
- genutzte Algos
- Vergleich der Ergebnisse

# Algorithmen
- Breitensuche, Dijkstra, A* und bidirekt. 

## Breitensuche (BFS)
- legt Knoten in Queue -> FIFO -> zuerst entdeckt, zuerst untersucht
- Ablauf:
    1. Startknoten in Queue & als besucht markieren
    2. ersten Knoten aus Queue nehmen
    3. falls Knoten == Ziel -> fertig (bzw. Pfad wird rekonstruirt)
    4. alle Nachbarknoten des Knoten betrachten
    5. noch unbesuchte Knoten in die Queue packen & als besucht markieren
    6. Schritte 2-5 wiederholen
- Schwächen
- Stärken
- Speicherbedarf
- Komplexität
- Voraussetzungen

## Dijkstra
- nutzt Priority Queue
- jeder Knoten bekommt einen Wert g(n): bisher bekannte Kosten von Start bis zum Knoten
- Ablauf
    1. setzt Kosten des Startknoten auf 0 & Kosten aller anderen Knoten auf unendlich
    2. aus den unbesuchten Knoten den Knoten mit dem kleinsten g(n) wählen
    3. ist betrachteter Knoten == Ziel?
    4. alle Nachbarn des Knoten prüfen: ist Weg über betrachteten Knoten zu dem Nachbarn billiger als bisher bekannte Weg zum Nachbarn, ja -> g(n) des Nachbarn aktualisieren
    5. betrachteten Knoten markieren
    6. Schritte 2-5 wiederholen
- Schwächen
- Stärken
- Speicherbedarf
- Komplexität
- Voraussetzungen

## A*
- baut auf Dijkstra auf
- berechnet aber die Priorität eines Knoten n nicht nur anhand bisheriger Kosten, sondern: 
    - f(n) = g(n) + h(n)
    - g(n): tatsächliche bisherige Kosten von Start bis n (wie bei Dijkstra)
    - h(n): geschätzte Restkosten von n bis Ziel (Heuristik, zB. die Luftlinie)
        - h(n) darf nie überschätzen, daher zB. Luftlinie gut -> garantiert kürzer als Straße
- Schwächen
- Stärken
- Speicherbedarf
- Komplexität
- Voraussetzungen

## Bidirektionale Suche
- 2 Instanzen eines Suchalgorithmus starten bei Start und Ziel
    - zB. 2x BFS oder 2x Dijkstra
    - Vorwärtssuche vom Startknoten
    - Rückwärtssuche vom Zielknoten
- Ablauf abhängig von genutzten Algorithmen
- sobald Knoten entdeckt wird, den beide Suchalgorithmen betrachtet haben -> Abbruch und Teilwege der beiden Algorithmen zusammensetzen
- Schwächen
- Stärken
- Speicherbedarf
- Komplexität
- Voraussetzungen

# Ziel
- kürzesten Weg zwischen 2 Knoten in einem Graphen (in unserem Fall Straßennetz) finden
- Algorithmen / Suche vergleichen, z.B. von der HAW zur Elbphilharmonie 

# Potentielle Fragestellungen
- Wie viele Knoten besucht jedes Verfahren? 
- Was bringt die Heuristik (Luftlinie) bei A*? 
- Überschätzende Heuristik: Wie viel schneller, wie viel längere Route? 

# Python Umsetzung
- Echtes Straßennetz über OpenStreetMap laden (Python osmnx:  https://osmnx.readthedocs.io/en/stable/) 
    - Python Bib um Straßennetze von OSM zu laden, sie virtuell zu durchwandern, analysieren und darzustellen

# Demo
- Karte, auf der eingefärbt wird, welche Knoten jedes Verfahren besucht (Dijkstra breitet sich kreisförmig aus, A* läuft Richtung Ziel) 
- in Diagramm Laufzeit, usw. visualisieren

# Code
## Setup per:
```python
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
```

## Starten per:
```python
    # 2) Karte herunterladen -> data/hamburg.graphml
    python downloadMap.py

    # 3) Suche laufen lassen + Animation erzeugen -> bfs.gif
    python visualize.py
```

## Klassen

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
