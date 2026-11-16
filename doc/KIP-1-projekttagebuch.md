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
- Wie lange ist der gefundene Weg in Kilometer und Anzahl der Kanten im Weg?
- Welchen Einfluss hat eine Heuristik? 

Die Ergebnisse werden als Animation auf der Karte in Form eines GIF dargestellt.


## 2. Projektablauf

Das Projekt wurde schrittweise angegangen.
1. Projekt-Setup und erste Untersuchung: Projektumgebung, Karte heruntergeladen, Graph inspiziert
2. Visualisierung vorbereiten: KI-unterstützte Python-Funktionen zur Visualisierung der Algorithmen erstellt
3. Vorbereitung: einlesen in Algorithmen, notieren der Abläufe, Vorgehen und Verteilung planen
4. Erster Algorithmus: BFS implementiert
5. Visualisierung: BFS-Suche animiert dargestellt, Export als GIF
6. Weitere Algorithmen umgesetzt und visualisiert
7. Doku fortlaufend angepasst
8. Ergebnisse der Algorithmen ausgewertet


## 3. Setup & Starthilfe

Die Umgebung wird über eine virtuelle Python-Umgebung und `requirements.txt` eingerichtet. Die Karte wird einmalig mit `downloadMap.py` als `data/hamburg.graphml` gespeichert und danach von den übrigen Skripten geladen.

### Setup
```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
```

### Starthilfe
```bash
    # Karte herunterladen -> data/hamburg.graphml
    python downloadMap.py

    # Suche laufen lassen + Animation erzeugen -> z.B. bfs.gif
    python visualize.py
```


## 4. Genutzte Techniken

- **osmnx:** Laden, Speichern und Durchlaufen des OpenStreetMap-Straßennetzes.
- **matplotlib:** Darstellung der Karte über `LineCollection` und Animation über `FuncAnimation`.
- **NumPy:** Effiziente Verwaltung der Kantenzustände während der Animation.
- **Pillow:** Export der Animation als GIF.
- **Virtuelle Umgebung und Pyright:** Reproduzierbares Setup und statische Typprüfung im Editor.

Der visuelle Stil der Animation wurde an ein öffentliches Beispielprojekt angelehnt (siehe Quellen; MIT-Lizenz).

Zur Erstellung von `visualize.py`, um die Pfadsuche zu visualisieren, wurde KI verwendet. 


## 5. Graph-Modellierung aus OpenStreetMap

Das Straßennetz wird mit osmnx über `graph_from_point` geladen und als `MultiDiGraph` gespeichert. Für den aktuell geladenen Ausschnitt ergibt sich:

- **Typ:** MultiDiGraph (gerichtet, Mehrfachkanten möglich)
- **Knoten:** 5.491
- **Kanten:** 12.244

Der Aufbau des Graphen ist wie folgt:

- Der Graph ist gerichtet, damit Einbahnstraßen abgebildet werden können. Normale Straßen bestehen aus zwei gegenläufigen Kanten, Einbahnstraßen nur aus einer.
- Die Mehrfachkanten entstehen, wenn zwischen zwei Knoten mehrere Straßensegmente verlaufen.
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

**Breitensuche (BFS).** Die BFS nutzt eine Queue nach dem FIFO-Prinzip und untersucht den Graphen schichtweise. Sie findet einen Weg mit möglichst wenigen Kanten. Da alle Kanten gleich behandelt werden, ist dieser Weg nicht zwingend der kürzeste gemessen an der Straßenlänge. Führt etwa eine einzelne Kante von 10 km Länge zum Ziel und alternativ ein Weg aus zwei Kanten von je 100 m, wählt die Breitensuche die 10-km-Kante, weil sie nur einen Schritt statt zwei braucht.

**Bidirektionale BFS.** Hier laufen zwei Breitensuchen, die sich Ebene für Ebene abwechseln: eine vorwärts vom Start, eine rückwärts vom Ziel. Die Rückwärtssuche folgt den Kanten entgegen ihrer Richtung, also zu den Vorgängern eines Knotens, damit Einbahnstraßen korrekt berücksichtigt werden. Sobald eine der Suchen einen Knoten entdeckt, den die andere schon kennt, werden die beiden Teilwege zu einem Gesamtweg zusammengesetzt. Das ebenenweise Abwechseln ist wichtig. Die Breitensuche garantiert den kürzesten Weg nur, weil sie eine Ebene vollständig abarbeitet, bevor sie die nächste beginnt. Wechseln die Suchen dagegen nach jedem einzelnen Knoten, kann eine Seite auf einem Ast schon eine Ebene tiefer sein als auf einem anderen und die andere Suche über einen Umweg treffen, bevor der kürzere Treffpunkt geprüft wurde. Wechseln sie ebenenweise, haben alle Treffpunkte einer Ebene dieselbe Gesamtlänge, und schon der erste ist optimal.

**Dijkstra.** Dijkstra nutzt eine Priority Queue, die Knoten nach ihren bisher bekannten Kosten `g(n)` sortiert. Der Startknoten beginnt mit Kosten 0, alle anderen Knoten werden mit Kosten unendlich initialisiert. In jedem Schritt wird der Knoten mit den geringsten Kosten entnommen und bearbeitet, danach werden die Kosten seiner Nachbarn angepasst (falls der Weg über den aktuellen Knoten günstiger ist). Als Kantenkosten dient hier die Straßenlänge `length`. Da alle Kanten nur positive Kosten haben, ist der beim Erreichen des Ziels gefundene Weg der kürzeste bezogen auf die Straßenlänge. Im Unterschied zur BFS berücksichtigt Dijkstra also die tatsächlichen Kantengewichte und nicht nur die Anzahl der Kanten.

**A\*.** A\* erweitert Dijkstra um eine Heuristik. Statt nur die bisherigen Kosten `g(n)` zu betrachten, bewertet es jeden Knoten mit `f(n) = g(n) + h(n)`, wobei `h(n)` die geschätzten Restkosten bis zum Ziel sind. Als Heuristik wird die Luftlinie zum Ziel verwendet. Da die Luftlinie nie länger ist als der tatsächliche Straßenweg, überschätzt `h(n)` die Restkosten nicht (zulässige Heuristik). A\* findet damit weiterhin einen optimalen Weg, expandiert aber in der Regel deutlich weniger Knoten, weil die Suche zielgerichtet läuft. Ist die Heuristik 0, verhält sich A\* wie Dijkstra und je genauer die Heuristik ist, desto stärker wird die Suche in Richtung Ziel laufen.

| Verfahren | Stärken | Schwächen | Speicherbedarf | Zeitkomplexität (worst case) | Voraussetzungen |
|---|---|---|---|---|---|
| BFS | einfach, optimal bei ungewichteten Graphen (finden Weg mit wenigsten Kanten), vollständig bei endlichem Graphen | ignoriert Kantengewichte -> findet nicht zwingend den kürzesten Straßenweg, expandiert breit in alle Richtungen | O(V) (ca. 1 Eintrag pro Knoten -> Queue (zu untersuchen), visited (gesehen), parent-Map (Weg zurück)) | $O(V+E)$ | ungewichtete/gleich gewichtete Kanten, Durchlauf nur vorwärts über successors, Weg von Start bis Ziel muss existieren |
| Bidirektionale BFS | weniger expandierte Knoten als einseitige BFS, findet bei ebenenweisem Wechsel zwischen beiden Seiten weiterhin Weg mit minimaler Kantenzahl | höherer Implementierungsaufwand, ignoriert Gewichte wie BFS, korrekte Abbruchbedingung nötig | O(V) (max. 2 Einträge pro Knoten -> je eine Queue (zu untersuchen), visited (gesehen), parent-Map (Vorwärts- und Rückwärtssuche)) | $ O(V+E) $ | Zugriff auf Vorgänger (gerichtete Kanten), ebenenweiser Wechsel zwischen beiden Seiten, beide Suchen können sich erreichen |
| Dijkstra | optimal bei nicht-negativen Gewichten, berücksichtigt Gewichte bzw. Straßenlänge | expandiert in alle Richtungen und damit viele Knoten, bei ungewichteten Graphen langsamer als BFS | O(V) (ca. 1 Eintrag pro Knoten -> Distanzen (bisherige Kosten), parent-Map (Weg zurück), Priority Queue (offene Knoten)) | $O((V+E) logV)$ | nicht-negative Kantengewichte, erreichbares Ziel |
| A\* | zielgerichtet - bevorzugt durch Heuristik bei Auswahl des nächsten Knotens diejenigen die dem Ziel näher sind, meist deutlich weniger Expansionen als Dijkstra, optimal bei zulässiger Heuristik | Qualität hängt stark von der Heuristik ab (schwache Heuristik ca. gleich Dijkstra) | O(V) (ca. 1 Eintrag pro Knoten -> Distanzen (Kosten), parent-Map (Weg zurück), offene Menge (entdeckte, noch nicht untersuchte Knoten), geschlossene Menge (vollständig expandierte Knoten)) | $O((V+E) logV)$ | zulässige (für Effizienz konsistente) Heuristik, nicht-negative Kantengewichte |


## 8. Vergleich der Ergebnisse

Zum Vergleichen der verschiedenen Algorithmen wenden wir sie alle auf denselben Graphen des Hamburger Straßennetzes an und betrachten folgende Werte:

- Anzahl der Kanten im Weg
- Anzahl der expandierten Knoten
- benötigte Laufzeit
- Länge des gefundenen Weges in km
- Auswirkung der Luftlinien-Heuristik bei A\*
- Verhalten einer bewusst überschätzenden Heuristik (schneller, aber ggf. längerer Weg)

### Ergebnisse (HAW → Elbphilharmonie)

| Verfahren | Kanten im Weg | expandierte Knoten | Laufzeit (ms) | Länge (km) |
|---|---|---|---|---|
| BFS | 30 | 1903 | 0,5 | 3,95 |
| Bidirektionale BFS | 30 | 567 | 0,1 | 3,95 |
| Dijkstra | 35 | 1936 | 5.31 | 3.46 |
| A\* | | | | |

TODO: Aufbereitung
- als Tabelle
- als animierte Karte (per visualize.py)


## 9. Herausforderungen

- **Overpass-API ausgelastet:** Der Kartendownload schlug zeitweise mit `502 Bad Gateway` fehl, da der öffentliche Overpass-Server an seiner Kapazitätsgrenze war. Das ist kein Fehler im Code; als Lösung dienen ein erneuter Versuch, ein anderer Endpunkt oder die bereits gespeicherte `.graphml`-Datei.
- **Richtung bei der Rückwärtssuche:** Die bidirektionale Suche muss rückwärts über Vorgänger laufen, sonst würden Einbahnstraßen falsch behandelt werden.
- **Größe/Performance der Animation:** Der GIF-Export ist groß und die Erzeugung dauert, das wurde über Parameter wie Knoten pro Frame und den Kartenradius ausbalanciert.


## 10. Ausblick

Aufbauend auf den Erkenntnissen sowie den Ergebnissen dieses Projekts wären folgende Punkte denkbar:
- **Andere Verkehrsmittel:** Das Routing über `network_type` auch für Fuß- und Radwege oder multimodal anbieten, statt nur für Autos.
- **Realistischere Gewichtung:** Die Fahrzeit statt der Straßenlänge (unter Beachtung von Tempolimits, Abbiegekosten) verwenden, um realistischere Routen zu erhalten.
- **Interaktive Anwendung:** Eine Oberfläche mit frei wählbarem Start und Ziel sowie einer Live-Darstellung der Suche, statt der festen Beispielstrecke und dem GIF-Export.
- **Systematische Auswertung:** Den Vergleich auf viele Start-/Ziel-Paare und größere Kartenausschnitte ausweiten und gegen eine Referenz (z.B. networkx) validieren.
- **Live-Daten:** Verkehrs- oder Baustellendaten einbinden, um dynamisches Routing zu ermöglichen.

Offene Fragen, die in dem Zusammenhang bleiben: 
- Wie verhalten sich die Verfahren auf deutlich größeren Netzen bzw. anderen Städten?


## 11. Klassen

### downloadMap.py
Zum Erstellen des Graphen, indem die Karte mit osmnx heruntergeladen wird.
- Koordinate im Zentrum Hamburgs angeben
- Radius um Koordinate angeben 
- Graph von Zentrum bis Radius erstellen und in hamburg.graphml speichern

### explore.py
Verwendet zum Untersuchen des Graphen von osmnx und zum Debuggen.
- lädt den erstellten Graphen rein
- gibt Typ, Knoten, Kanten aus
- gibt alle Attribute des ersten Knoten aus
    - z.B. x/y (Lon/Lat), street_count, highway, ref, railway
- gibt alle Attribute der ersten Kante aus
    - z.B. length, highway, maxspeed, oneway, reversed, geometry, lanes, osmid

### algorithms.py
Die Implementierung der verschiedenen Algorithmen für die Wegsuche durch den Graphen bzw. die Karte.
- alle Algorithmen folgen der einheitlichen Signatur: `algo(G, start, dest) -> (path, expanded)`
    - start & dest -> Knoten-IDs für Start und Ziel
    - G -> der zu untersuchende Graph

#### construct_path
Rekonstruiert aus der parent-Map den gefundenen Weg vom Start zum Ziel als Knotenliste.
- rekonstruiert den Weg von Ziel bis Start rückwärts -> über parent-Verweise von Ziel bis Start
- kriegt parent-Map, Start-Knoten, Ziel-Knoten
    - parent-Map besteht aus `Key: Knoten` und `Value: Parent` -> zu jedem Knoten seinen Parent erhalten

#### bfs
Die Implementierung der Breitensuche durch den Graphen.
- nutzt Breitensuche mit deque um den Weg vom Start bis zum Ziel zu finden, indem es immer weiter die benachbarten Knoten expandiert und abbricht sobald das Ziel erreicht wurde
- return
    - Erfolg:     path, expanded (Liste der betrachteten Knoten)
    - Misserfolg: None, expanded

TODO - die anderen Algorithmen-Funktionen?

### visualize.py
Visualisiert die Suche durch die Graphen.
Macht aus den Ergebnissen (path & expanded) eine animierte Karte -> gespeichert als GIF-Datei.
- je nach Zustand einer Karte wird sie eingefärbt
    - UNVISITED, VISITED, ACTIVE, PATH

#### _edges_to_lines
Wandelt die Straßengeometrien des Graphen in zeichenbare Linien sowie Nachschlage-Strukturen zum Einfärben um.
- holt echte Straßengeometrien
- baut 3 Hilfsstrukturen
    - lines (Punktfolgen)
    - index ((u,v,key) -> Position)
    - out_edges (Knoten -> ausgehende Kanten)

#### animate_search
Erzeugt aus path und expanded die animierte Karte, welche den Suchverlauf und den Weg schrittweise darstellt.
- legt alle Straßen als LineCollection an
- markiert Start/Ziel
- animiert in zwei Phasen
    1. Suchphase: pro Frame werden expandierte Knoten verarbeitet: 
        - Kanten der Knoten VISITED
        - Kanten ihrer Nachfolger ACTIVE
    2. Pfadphase: Karte leeren, Weg schrittweise weiß nachzeichnen

### metrics.py
Messskript für den Algorithmen-Vergleich. Verwendet um die Werte für die Auswertung zu erhalten.


#### path_length(Graph, path)
Summiert die Straßenlänge des Weges (nimmt je Knotenpaar die kürzeste parallele Kante) und liefert die Pfadlänge in km.

#### measure(Graph, start, dest, algo)
Führt den angegebenen Algorithmus einmal aus (für Kantenanzahl und expanded), misst dann die Laufzeit über `RUNS = 50` Durchläufe mit `time.perf_counter()` und mittelt sie.

#### main
Lädt den Graphen, mappt START & DEST auf Knoten und gibt pro Verfahren eine Zeile aus:
algorithm, edges, expanded, ms, km
für die Tabelle.

## Quellen

- osmnx-Dokumentation: https://osmnx.readthedocs.io/en/stable/
- OpenStreetMap / Overpass-API: https://wiki.openstreetmap.org/wiki/Overpass_API
- Visueller Stil der Animation, angelehnt an: https://github.com/felipearosr/Shortest_Path (MIT-Lizenz)
- Dijkstra: https://www.geeksforgeeks.org/dsa/time-and-space-complexity-of-dijkstras-algorithm/
- A*: https://www.datacamp.com/de/tutorial/a-star-algorithm