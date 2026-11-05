import heapq
import json

class StateGraphDijkstraSolver:
    def __init__(self, adjacency_list: dict, capacity: int):
        self.adjecency_list = adjacency_list
        self.capacity = capacity

        self.current_state = {
            "total cost": 0,
            "node": "START",
            "white undelivered": ["W1", "W2", "W3", "W4", "W5"],
            "red undelivered": ["R1", "R2", "R3", "R4", "R5"],
            "white onboard": 0,
            "red onboard": 0,
            "pred": None,
            "move": None
        }

        self.__unique_counter = 0

        # dictionary to store and look-up the best cost for any unique state
        # if a state is not in the dict, the best cost can be assumed to be inf
        self.previous_states = {}

    def counter(self):
        """
        returns a unique number every time for breaking ties in priority queue
        """
        self.__unique_counter += 1
        return self.__unique_counter

    def get_state_key_string(self, state: dict):
        """
        Return a copy of the state dictionary without "total cost"
        """
        state = state.copy()
        return str({
            "node": state["node"],
            "white undelivered": state["white undelivered"],
            "red undelivered": state["red undelivered"],
            "white onboard": state["white onboard"],
            "red onboard": state["red onboard"]
        })

    def get_adjecent_nodes(self, node: str):
        return list(self.adjecency_list[node].keys())

    def move_is_legal(self, state: dict, move: str):
        """
        Determine if a move is legal from a given state.

        A move is given as a string.
        The first word of the string is either "pickup" or "deliver"
        The second word is the node to goto for pickup or delivery
        like "W1" for a delivery or "1" for a pickup.
        If a move is a pickup, the last word is the number of packages to pick up.
            
        Example of a move: "pickup 1 2"
        """

        move_parts = move.split(" ")

        if move_parts[0] == "pickup":

            goto_node = move_parts[1]
            number_of_packages = move_parts[2]

            node_adjecent = goto_node in self.get_adjecent_nodes(state["node"]) # redundant
            capacity_valid = int(number_of_packages) + state["white onboard"] + state["red onboard"] <= self.capacity

            return node_adjecent and capacity_valid
            
        elif move_parts[0] == "deliver":

            goto_node = move_parts[1]

            node_adjecent = goto_node in self.get_adjecent_nodes(state["node"]) # redundant
            delivery_node_empty = goto_node in state["red undelivered"] or goto_node in state["white undelivered"]
            if goto_node[0] == "W" and state["white onboard"] > 0:
                capacity_valid = True
            elif goto_node[0] == "R" and state["red onboard"] > 0:
                capacity_valid = True
            else:
                capacity_valid = False

            return node_adjecent and delivery_node_empty and capacity_valid


    def apply_move(self, state: dict, move: str):
        """
        Returns a state that is the result of the input state and the input move as well as the cost to perfrom the move.

        A move is given as a string.
        The first word of the string is either "pickup" or "deliver"
        The second word is the node to go to for pickup or delivery
        like "W1" for a delivery or "1" for a pickup.
        If a move is a pickup, the last word is the number of packages to pick up.
            
        Example of a move: "pickup 1 2"

        return cost, new_state
        """

        new_state = state.copy()
        new_state["white undelivered"] = list(state["white undelivered"]) # lists are re-copied to avoid sharing with parent state because .copy() produces a shallow copy
        new_state["red undelivered"] = list(state["red undelivered"])

        move_parts = move.split(" ")

        # update cost
        goto_node = move_parts[1]
        cost = self.adjecency_list[new_state["node"]][goto_node][0]
        new_state["total cost"] += cost
        
        if move_parts[0] == "pickup":
            
            number_of_packages = move_parts[2]

            if goto_node == "1": 
                color_key = "white onboard"
            elif goto_node == "2": 
                color_key = "red onboard"

            new_state["node"] = goto_node
            new_state[color_key] += int(number_of_packages)
            
        elif move_parts[0] == "deliver":

            if goto_node[0] == "W": 
                new_state["white onboard"] -= 1
                new_state["white undelivered"].remove(goto_node)
            elif goto_node[0] == "R":
                new_state["red onboard"] -= 1
                new_state["red undelivered"].remove(goto_node)

            new_state["node"] = goto_node

        return cost, new_state

    def get_legal_moves(self, state):
        moves = []
        # pickups
        for node in ["1", "2"]:
            for i in range(1, self.capacity+1):
                moves.append("pickup " + node + " " + str(i))
        # deliveries
        for node in ["R1", "R2", "R3", "R4", "R5", "W1", "W2", "W3", "W4", "W5"]:
            moves.append("deliver " + node)

        legal_moves = []

        for m in moves:
            if self.move_is_legal(state, m):
                legal_moves.append(m)

        return legal_moves

    def backtrack(self, final_state: dict):
        route = []
        state = final_state
        while True:
            #print(f"move: {state["move"]}\nstate: {state}")
            route = [(state["node"], state["move"])] + route
            
            if state["node"] == "START":
                break

            state = state["pred"]

        return route

    def solve(self):
        Q = []
        heapq.heappush(Q, (0, self.counter(), self.current_state))

        while len(Q) > 0:

            state = heapq.heappop(Q)[2]

            if len(state["white undelivered"]) + len(state["red undelivered"]) == 0:
                return self.backtrack(state)

            for move in self.get_legal_moves(state):
                # apply the move
                new_state = self.apply_move(state, move)[1]
                costless_state_string = self.get_state_key_string(new_state)

                # check if state has been seen before
                if costless_state_string in self.previous_states:
                    # if the cost of new_state is better than the previous best cost, the predecessor and best cost are updated
                    if new_state["total cost"] < self.previous_states[costless_state_string]["total cost"]:
                        self.previous_states[costless_state_string]["total cost"] = new_state["total cost"] # update cost
                        new_state["pred"] = state
                        new_state["move"] = move
                        heapq.heappush(Q, (new_state["total cost"], self.counter(), new_state))
                else:
                    self.previous_states[costless_state_string] = new_state # update cost
                    new_state["pred"] = state
                    new_state["move"] = move
                    heapq.heappush(Q, (new_state["total cost"], self.counter(), new_state))



class SolverDualMagazines(StateGraphDijkstraSolver):
    def __init__(self, adjacency_list, capacity):
        """
        Capacity = capacity per magazine
        """
        super().__init__(adjacency_list, capacity)

    def move_is_legal(self, state: dict, move: str):
            """
            Determine if a move is legal from a given state.
            Overides the move_is_legal method to use the 2_magazines model of storing packages
    
            A move is given as a string.
            The first word of the string is either "pickup" or "deliver"
            The second word is the node to goto for pickup or delivery
            like "W1" for a delivery or "1" for a pickup.
            If a move is a pickup, the last word is the number of packages to pick up.
                
            Example of a move: "pickup 1 2"
            """
    
            move_parts = move.split(" ")
    
            if move_parts[0] == "pickup":
    
                goto_node = move_parts[1]
                number_of_packages = move_parts[2]
    
                node_adjecent = goto_node in self.get_adjecent_nodes(state["node"]) # redundant
                if goto_node == "1":
                    capacity_valid = int(number_of_packages) + state["white onboard"] <= self.capacity
                elif goto_node == "2":
                    capacity_valid = int(number_of_packages) + state["red onboard"] <= self.capacity
    
                return node_adjecent and capacity_valid
                
            elif move_parts[0] == "deliver":
    
                goto_node = move_parts[1]
    
                node_adjecent = goto_node in self.get_adjecent_nodes(state["node"]) # redundant
                delivery_node_empty = goto_node in state["red undelivered"] or goto_node in state["white undelivered"]
                if goto_node[0] == "W" and state["white onboard"] > 0:
                    capacity_valid = True
                elif goto_node[0] == "R" and state["red onboard"] > 0:
                    capacity_valid = True
                else:
                    capacity_valid = False
    
                return node_adjecent and delivery_node_empty and capacity_valid


def get_complete_path(route: list[tuple]):
    
    path = []
    total_cost = 0

    for i in range(len(route)-1):
        sub_path = adj_list[route[i][0]][route[i+1][0]][1]
        total_cost += adj_list[route[i][0]][route[i+1][0]][0]
        for node in sub_path:
            if len(path) != 0:
                if path[-1] != node:
                    path.append(node)
            else:
                path.append(node)

    return total_cost, path


with open("simple_graph_adjacency_list.json", "r", encoding="utf-8") as f:
    adj_list = json.load(f)


optimal_routes = {}

for capacity in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
    solver = StateGraphDijkstraSolver(adj_list, capacity)
    solved_route = solver.solve()
    optimal_routes[str(capacity)] = (solved_route, get_complete_path(solved_route))
    print(f"Route with capacity {capacity} solved ({capacity}/10)")

with open("optimal_paths_dijkstra.json", "w", encoding="utf-8") as f:
    json.dump(optimal_routes, f, indent=4, ensure_ascii=False)

optimal_routes_with_two_mags = {}

for capacity in [1, 2, 3, 4, 5]:
    solver = SolverDualMagazines(adj_list, capacity)
    solved_route = solver.solve()
    optimal_routes_with_two_mags[str(capacity)] = (solved_route, get_complete_path(solved_route))
    print(f"Route with capacity {capacity} solved ({capacity}/10)")

with open("optimal_routes_with_two_mags.json", "w", encoding="utf-8") as f:
    json.dump(optimal_routes_with_two_mags, f, indent=4, ensure_ascii=False)
    