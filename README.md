# antennae
Python implementation of pheromone-based routing of ants.

## Requirements
This module is written in Python 3. External dependencies are 
* NumPy
* Networkx
* Matplotlib (optional)

## Running
Clone the repository with 
```bash
git clone https://github.com/0mar/antennae.git
cd antennae
python3 simulation.py
```

If you want to change the number of ants, the number of nodes, pheromone decay rate or other parameters, edit `params.py`.

## What am I looking at?

[Ants](https://en.wikipedia.org/wiki/Ant) have limited individual capacities but work very well together in [colonies](https://en.wikipedia.org/wiki/Ant_colony). 
In spite of their limited sensory and deductive capabilities, they are able to find and communicate a food source and an optimal path towards that source based on [pheromone signals](https://en.wikipedia.org/wiki/Pheromone).

Basically, as soon as an ant finds a source of food, he returns to the nest and marks his path with a chemical that the other ants can interpret as a guide towards the food. When more ants go looking for this food, they try to follow the pheromone and if they are succesful, they return as well, leaving a trail of their own. 

Meanwhile, the pheromone slowly decreases over time. This results in the shorter paths being more popular than the longer ones, and over time the colony discovers the optimal route to the food.

## What is happening?

The code generates a random graph with a certain degree of [connectivity](). It sets a nest node and a food node. 
Subsequently, all ants are released from the nest node and move randomly towards the food node. 
At each node, an ant chooses a random direction based on the amount of pheromone present on each of the edges.
Initially, all edges carry the same amount of pheromone. But when an ant reaches the food node, they backtrace their path towards the nest node, leaving a trail of pheromone along the edges they pass.
When the ants return to the nest node, they dump the food, forget about their trip, and try to find the food node again, guided by the pheromone trails.

## Who thought of this?

Not me. There is a lot of research done in this area, check for instance [here](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.161.9541&rep=rep1&type=pdf), or [here](http://faculty.washington.edu/paymana/swarm/colorni92-ecal.pdf), or [here](http://ieeexplore.ieee.org/document/484436/). 
