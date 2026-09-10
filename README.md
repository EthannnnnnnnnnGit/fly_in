*This project has been created as part of the 42 curriculum by eel-kerc.*

## <font color="#A7C7E7">Description</font>

Fly-in is a 42 project which consist into **drone simulation**.   
Given a `graph`, the most efficient route should be choosen for as much drones as given from `start hub` to `end hub`.   
The graph is made of `hubs` and `connections`. For hubs, mandatory data can be specified such as type, name, coordinates.
More data can be add such as the max number of drones, the hub color or the zone-type.   
The zone type modify priority like following:

- **Priority:** Must be choose in priority between two path of same cost
- **Restricted:** Takes two turn to go through the hub
- **Normal:** Normal behaviour, one turn to access
- **Blocked:** Can't access the hub

At each turn, each drones move should be displayed in the format `starting_hub-destination_hub`.   

Program should provide a visual representation of graph and drones using terminal or any python library.



## <font color="#848884">Instructions</font>

To run the project, you must first `install dependencies` with the following commands:

```
make install
```

Then run it with:

```
make run
```
For debuggin using pdb, run: 
```
make debug
```

To **erase** tempory **files and caches**, run:

```
make clean

```
To check project's `norm`, run:

```
make lint
make lint-strict
```

## <font color="#FAC898">Algorithm choices</font>

The algorithm choosen was Dijkstra.   
`Dijkstra` is a graph algorithm that is able to find the shortest way of a weighted graph.   
It works by setting all shortest path to the start hub at infinity and then at simulation modifying them by the shortest weight found.   
Each hub has his own weight from the start and the previous hub that is the shortest path from the start.

Dijkstra was implemented with a `heapqueue` getting track of weight in the simulation and a set of visited hub.   
A hashmap is implemented that stock the number of drones in each hubs and connections for each turn to avoid hubs overload.   
- The program starts at start_hub and iterate while there is hub to that aren't visited yet in the queue.   
- The hub in the queue that has the minimum cost is choosen and every neighbor of that hub is add into the queue with the `hub cost + neighbor access cost`.   
- A should_wait method is implemented to define is there is enough place in the hub and connection, and add the hub with a turn add if it should wait on the hub.   
- The algorithm return a list of hubs and connections if hubs are restricted, and is iterate over the number of drones.


## <font color="#93C572">Visual representation</font>

Visual representation is made with library PyQt6 in 3D.   
For visual, a main window is created that handle every event.   

The main window is made of `commands`, `3d window` and `filetree` for map selection.   
A list of input define in the commands part allow interaction with the 3d visual.   
Here is the following input interaction:
- Q: Quit simulation
- WASD: Move camera
- Right Drag: Look around
- Scroll: Zoom
- Left / Right: Change turn
- R: Run/Stop simulation
- Up / Down Camera intensity"
- 2: 2D view
- 3: 3D view

## <font color="#F88379">Example Usage</font>

### Input
The simulation takes a formatted map file detailing the drone count, zones with optional metadata, and connections:
```
nb_drones: 5
start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=restricted color=red]
hub: roof2 6 2 [zone=normal color=blue]
hub: corridorA 4 3 [zone=priority color=green max_drones=2]
hub: tunnelB 7 4 [zone=normal color=red]
hub: obstacleX 5 5 [zone=blocked color=gray]
connection: hub-roof1
connection: hub-corridorA
connection: roof1-roof2
connection: roof2-goal
connection: corridorA-tunnelB [max_link_capacity=2]
connection: tunnelB-goal
```

### Expected Output
The simulation outputs the step-by-step movement of drones, where each line represents a single turn and lists the movements in a `D<ID>-<zone>` format:
```
D1-roof1 D2-corridorA
D1-roof2 D2-tunnelB
D1-goal D2-goal
```

## <font color="#5F9EA0">Resources</font>

- [Dependencies](https://docs.astral.sh/uv/)
- [Learning regex](https://www.w3schools.com/python/python_regex.asp)
- [Pydantic usage](https://pydantic.dev/docs/validation/latest/concepts/fields/)
- [Dijkstra comprehension](https://www.datacamp.com/fr/tutorial/dijkstra-algorithm-in-python)
- [Heapqueue](https://www.geeksforgeeks.org/python/heap-queue-or-heapq-in-python/)
- [Visual](https://www.pythonguis.com/pyqt6-tutorial/)
- [Keybaord events](https://note.com/goro_131241d/n/n4766f1165722?hl=en)
- [Positionning Button](https://koor.fr/Python/Tutoriel_PySide/pyside_layout_sans.wp)
- [Making boat in blender](https://www.youtube.com/watch?v=FxrpxP0rLgA) 
- [Mermaid](https://mermaid.ai/open-source/intro/)

#### AI Usage

- Understanding regex and using regex (parsing)
- Understanding and using PyQt6 (visual)
- Solving make-lint
