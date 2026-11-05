# Graph theory notes

The logistics track can be represented as a graph G consisting of two discreet quantities:
1) A quantity of nodes (a.k.a. vertices) ***V(G)***
2) A quantity of edges ***E(G)***

A graph is a mathematical tool to describe networks of many kinds. An example of this could be a road network.\
In this example edges would be the roads, and the nodes would describe the varies intersections that connect the roades.\
These intersectoins (nodes) can have any number of roads (edges) connected to them.\
A node with only one edge connection wold represent a dead end.\
In graph theory, the number of edges connected to a node is called the *degree og the node* or ***d(v)***.

In the case of this project, the edges are the black lines that our robot has to follow,\
and the nodes would be anywhere where these black lines end in a dead end or cross over eachother


<img src="images\bane.png" alt="drawing" height="350"/>
<img src="images\bane_geogebra.png" alt="drawing" height="350"/>


Using graph theory, we can systematically approch complex problems\
related to finding the shortest or most effective path from one node to another,\
and by combining many of these paths, solve an essential problem like:
* *"What is the most efficient way to collect and dispense all packages to complete the logistics track as fast as possible"*

<br>

First we need to establish a couple key terms used in graph theory:

#### Direction:
- An edge may have a direction. A directed edge allows travel in only one direction along the edge.\
In practical terms we can say that for two nodes ***A*** and ***B*** in a directed edge ***A->B***, ***A*** is adjecent to ***B*** but ***B*** is not adjecent to ***A***.\
If a graph contains at least one directed edge we call it a directed graph.

#### Adjecency:
- Two nodes are said to be adjecent, if an edge exists that connects both nodes.\
If two nodes A and B exist as well as an edge A-B, then A and B are adjecent

#### Paths:

- Paths are lists of nodes in a graph, where each node (appart from the first and last)\
is adjecent to the previous node and the next node in the list.

#### Edge weight:

- Edge weight is number assigned to each edge in a graph.\
What the number represents depends entirely on the network the graph is describing.\
It is commonly an analog for the distance from one end of the edge to the other.\
Edge weight will sometimes also take cost or time into account.

#### Pathfinding Algorithm

- An algotithm for finding the shortest path between two nodes is called a pathfinding algorithm.\
Examples of pathfinding algorithms include Dijkstra's Algorithm and it's more efficient offspring the A* algorithm\
These algorithms insure that the created path has the lowest possible sum of edge weights\
of any path between the starting node and the end node

<br>

### Dijkstra's Algorithm

Dijkstra's Algorithm works like this:

0) A starting node A and an end node B is selected from the graph G

1) All nodes in G are assigned a distance label, which represents the distance to node A.\
Node A is assigned a label of 0 while all other nodes are assigned inf.

2) Starting at a node U with the smallest distance label, the distance to all neighbouring (adjecent) nodes is checked.\
If a neighbours distance label is bigger than the sum of U's label and the edge weight between U and the neighbour,\
the neighbours label is updated to this new sum. When a neighbours distance label is updated, the neighbours new predecessor is set to U.\
After all neighbours have been checked and possibly updated, node U is marked as visited.

3) Step two is repeated, visiting the unvisited node with the smallest distance label each time.\
If the end node B is ever selected in step two, the algorithm terminates.\
The shortest path from A to B is now found by backtracking through the predecessors until node A is reached

<br>

Here is that same algorithm written in pseudo code:

```
function dijkstra(G, start, end):
    for each node v in V(G):
        dist(v) = infinite
        prev(v) = none
    
    dist(start) = 0

    while u != end:
        u = minUnvisited(V(G))
        visited(u) = True

        for each neighbour w of u
            if dist(w) > dist(u) + edge(u, w):
                dist(w) = dist(u) + edge(u, w)
                prev(w) = u

    k = end
    path = empty list

    while k != start:
        insert k in path at index 0
        k = prev(k)
    
    insert start in path with index 0

    return path
```

This pseudo code assumes the existance of a function called minUnvisited.\
This function iterates over every node in the graph and returns the node satisfying these criteria:
1) the node has not been marked as visited
2) the node has the smallest distance label out of all other unvisited nodes

The existance of this function simplifies the code a bit, at the cost of efficiency.\
Because the function must iterate over all nodes in the graph, it has a time complexity of ***O(n)*** which bottle-necks the algorithm to ***O(n^2)***.\
Using a more sophisticated data structure known as a priority queue,
(which has a time complexity of ***O(log(n))*** because of it's use of a binary tree),\
the time complexity of the algorithm is reduced to ***O(n\*log(n))***.\
For the purposes of this project, where the algorithm does not need to be executed in real time\
and has a relatively small graph size, using a function like minUnvisited will not have an impact on the efficiency of our robot.

<br>

### The adjecency list

When representing a graph in code, a usefull data structure is an adjecency list.\
An adjecency list is a look-up table with the same size as V(G), where every entry in the table corrosponds to a node in G,\
and contains all adjecent nodes along with the edge weight of the edge that connects to that specific node.

In python (primary language used in our project) and adjecency list could be represented with a dictionary.

For a weighted graph like this:

<img src="images\graph_example.png" alt="drawing" height="200"/>

<br>

The adjecency list as a python dictionary would look like this:

```py
adj_dict = {
    "A": [("B", 10), ("C", 5)],
    "B": [("A", 10), ("C", 15)],
    "C": [("A", 5), ("B", 15), ("D", 20)]
}
```

<br>
<br>

# Finding the optimal route

To solve for the most optimal path to pick up and deliver all packages,\
we can either write a smart, optimized algorithm that finds the correct path in as little\
time as possible, or we can write a brute force approch that tries every combination and compares them to find the shortest path.

Before we pick our poison, lets simplify the problem to get a better sense of what the algorithm needs to do:

We have 2 dispensers (1 red and 1 white) and 10 drop-offs (5 red and 5 white).\
We know (because the graph is connected), that any two drop-offs and or dispensers must have a path that connects them.\
Therefore, we can simply disregard the other nodes of the graph for now, and we get a graph that looks like this:

<img src="images\simple_graph.png" alt="drawing" height="450"/>

<br>

In this graph the edges represent the optimal paths between the nodes, and the edge weight would be the sum of the edge weights in the path.\
Working with this representation cuts out a large majority of combinations that are obviously not the optimal route.

The problem is now boiled down to arranging 10 "delivery tasks" to have the lowest sum of edge weights.\
Therefore the number of possible combinations of optimal routes we can take is ***10! = 3,628,800***

This number is small enough that it makes sense to go with a brute force approch.

Testing all permutations has a time complexity of ***O(n!)*** where *n=10* in our case.

<br>

# Finding the optimal route with n-capacity for packages

Say we allow for the robot to pick up and hold more than one package at a time.\
We now need a graph that reflects the new possible paths the robot can take to complete its route:

<img src="images\simple_graph_n_capacity.png" alt="drawing" height="450"/>

<br>

By allowing the robot a capacity of ***n*** packages, it should now be able to move from one drop-off\
to another without making a stop at a dispenser in between. One problem arises: to test all permutations of this\
configuration, the number of permutations becomes exponentially larger (too large to brute force).

The bruteforce algorithm of testing every permutation of the list of tasks {W1, W2, W3, W4, W5, R1, R2, R3, R4, R5}\
Works fine for a capacity of ***n = 1***, because we know that every drop off must be preceeded by exactly one pickup,\
but when our capacity increases to ***n***, we essentially have ***n+1*** (pick up 0 to ***n*** packages) decisions before every task.\
The number of combinations becomes ***10! \* (n+1)^10*** 

The number of combinations sky-rockets:

| n | combinations        |
|---|---------------------|
| 2 | 214.277.011.200     |
| 3 | 3.805.072.600.000   |
| 4 | 35.437.500.000.000  |
| 5 | 219.419.660.000.000 |

A more systematic approch is needed, so we return to Dijkstra's algorithm. This time, instead of looking at only the adjecent nodes in our complete graph as the next legal moves,\
we evaluate every legal move that changes the *state* of the robot at every step. Every legal move is evaluated and assigned a distance label (just like in regular dijkstra)\
Then, the algorithm changes state to the match the move of shortest distance and repeats.

We can think of this as running Dijkstra's algorithm on whats called an expanded state graph, where every node (instead of representing a physical location) represents a state.

The state of the robot looks like this:\
***(Current node,  set of undelivered nodes, white packages onboard, red packages on board)***

At any given time in our robot's route, the robot has a list of moves it can perform:
1) pick up a white package
2) pick up a red package
3) deliver a red package to an empty red delivery node (R1, R2, R3, R4 or R5)
4) deliver a white package to an empty white delivery node (W1, W2, W3, W4 or W5)

A set of constraints are put on the robot to disginguish between legal and illegal moves:
1) may only deliver a white package if number of white packages onboard > 0
2) may only deliver a red package if number of red packages onboard > 0
3) may only pick up white package if number of white packages onboard < ***n***
4) may only pick up red package if number of red packages onboard < ***n***

To optimize this algorithm further, i will also implement a priority queue. A priority queue is a list that remains sorted based on some metric.\
The queue has the functions ***Q.push(x, item)*** which inserts the **item** based on hte size of **x**, and ***Q.pop()*** which removes and returns the smallest item from queue.\
A priority queue is more efficient because it uses binary search which has a time complexity of ***O(log(n))***, compared to regular search which scales linearly (***O(n)***)

Below is some abstract pseudocode:

```
function expanded_state_space_dijkstra(G):

    Q = priority queue []

    start = (start_node, set of undelivered nodes, 0 white, 0 red) # set the initial state of the robot
    Q.push(0, start)

    While Q is not empty:

        if all packages delivered:
            route = backtrack(current_state)
            return route

        current_cost, current_state = Q.pop()

        for every legal move:
            new_state, cost = apply_move(current_state, move)

            new_cost = current_cost + cost

            if new_cost < cost(new_state):
                cost(new_state) = new_cost
                new_state.predecessor = current_state

                Q.push(new_cost, new_state)
```

After running the algorithm on n = {1, 2, ... 10} the resulting path lengths are:


| n | Length [m] |
|---|-----|
| 1 | 61.69 |
| 2 | 42.30 |
| 3 | 34.25 |
| 4 | 32.95 |
| 5 | 30.09 |
| 6 | 29.94 |
| 7 | 27.91 |
| 8 | 27.91 |
| 9 | 27.06 |
| 10 | 27.06 |

<img src="images\plot.png" alt="drawing" height="250"/>

NB. after n=3, the returns diminish quickly.

<br>

Using a model where packages are stored in one of two magazines attached to the robot (a red and a white mag), the constraints are slightly altered.\
In the two-magazine configuration (a.k.a Pez) a white package may only be picked up if the number of white packages held is less than the individual mag capacity\
and the same applies to red packages. The capacity of each color is now independent

<img src="images\plot_with_pez.png" alt="drawing" height="250"/>

<br>

The pez model for all ***n*** (except for n=10) is less optimal than the normal model. For n=6 the difference is about 10%.