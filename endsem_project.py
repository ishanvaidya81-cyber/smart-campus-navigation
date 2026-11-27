import json
import os

# ==============================================================================
# SMART CAMPUS NAVIGATION SYSTEM 
# ==============================================================================

# ------------------------------------------------------------------------------
# MEMBER 1: Default Campus Dataset & File Persistence (JSON Load / Save)
# ------------------------------------------------------------------------------
DATA_FILE = "campus_data.json"

# Default campus map if no JSON file exists yet
DEFAULT_DATA = {
    "locations": [
        "Main Gate",
        "Academic Block A",
        "Academic Block B",
        "Library",
        "Cafeteria",
        "Sports Complex",
        "Hostel Block",
        "Old Annex",
    ],
    "paths": [
        {"from": "Main Gate", "to": "Academic Block A", "distance": 120},
        {"from": "Main Gate", "to": "Cafeteria", "distance": 200},
        {"from": "Academic Block A", "to": "Academic Block B", "distance": 150},
        {"from": "Academic Block A", "to": "Library", "distance": 300},
        {"from": "Academic Block B", "to": "Library", "distance": 100},
        {"from": "Academic Block B", "to": "Cafeteria", "distance": 180},
        {"from": "Library", "to": "Hostel Block", "distance": 250},
        {"from": "Cafeteria", "to": "Sports Complex", "distance": 220},
        {"from": "Sports Complex", "to": "Hostel Block", "distance": 160},
    ],
}


# 1. Load data from JSON file
def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA

    try:
        file = open(DATA_FILE, "r")
        data = json.load(file)
        file.close()
        return data
    except:
        print("Error reading file. Using default campus data.")
        return DEFAULT_DATA


# 2. Save data to JSON file
def save_data(data):
    file = open(DATA_FILE, "w")
    json.dump(data, file, indent=4)
    file.close()


# ------------------------------------------------------------------------------
# MEMBER 2: Graph Builder & Case-Insensitive Location Lookup Helper
# ------------------------------------------------------------------------------
# 3. Convert JSON locations & paths into a graph dictionary
def build_graph(data):
    graph = {}
    for loc in data["locations"]:
        graph[loc] = {}

    for path in data["paths"]:
        place1 = path["from"]
        place2 = path["to"]
        dist = path["distance"]

        # Walking paths work in both directions
        if place1 in graph and place2 in graph and dist > 0:
            graph[place1][place2] = dist
            graph[place2][place1] = dist

    return graph


# 4. Find exact location name even if user types lowercase/uppercase
def find_exact_name(user_text, locations_list):
    user_text = user_text.strip().lower()
    for loc in locations_list:
        if loc.lower() == user_text:
            return loc
    return None


# ------------------------------------------------------------------------------
# MEMBER 3: Shortest Path Engine (Dijkstra's Algorithm & Route Display)
# ------------------------------------------------------------------------------
# 5. Dijkstra's Algorithm using set for unvisited nodes & tuple return 
def dijkstra(graph, start, end):
    distances = {}
    previous = {}
    unvisited = set(graph.keys())

    # Set all initial distances to a huge number (999999)
    for node in graph:
        distances[node] = 999999
        previous[node] = None

    distances[start] = 0

    while len(unvisited) > 0:
        # Step A: Find the unvisited location with the smallest distance
        current = None
        smallest_dist = 999999

        for node in unvisited:
            if distances[node] < smallest_dist:
                smallest_dist = distances[node]
                current = node

        # Stop if destination is reached or remaining places are unreachable
        if current is None or current == end:
            break

        unvisited.remove(current)

        # Step B: Check neighbors of the current location
        neighbors = graph[current]
        for neighbor in neighbors:
            if neighbor in unvisited:
                new_dist = distances[current] + neighbors[neighbor]
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current

    # If end distance is still 999999, no path exists
    if distances[end] == 999999:
        return None, 0

    # Step C: Trace backwards from 'end' to 'start' to build the route
    route = []
    step = end
    while step is not None:
        route.append(step)
        step = previous[step]

    route.reverse()  # Flip the list so it goes start -> end
    return route, distances[end]


# 8. Menu Option 3: Find shortest route 
def find_shortest_route(data, graph):
    print("\n--- Find Shortest Route ---")
    start_input = input("Enter starting location: ")
    end_input = input("Enter destination location: ")

    start = find_exact_name(start_input, data["locations"])
    end = find_exact_name(end_input, data["locations"])

    if start is None or end is None:
        print("Error: Invalid location entered.")
        return

    if start == end:
        print("Start and destination are the same! Distance: 0 meters.")
        return

    route, total_distance = dijkstra(graph, start, end)

    if route is None:
        print("No route available between", start, "and", end)
    else:
        has_food_stop = any("cafeteria" in stop.lower() for stop in route)
        print("\n==============================")
        print("SHORTEST ROUTE:", " -> ".join(route))
        print("TOTAL DISTANCE:", total_distance, "meters")
        print("PASSES CAFETERIA:", has_food_stop)
        print("==============================")


# ------------------------------------------------------------------------------
# MEMBER 4: Campus Map Admin Features (Add Location & Add / Update Path)
# ------------------------------------------------------------------------------
# 9. Menu Option 4: Add a new location
def add_location(data):
    new_loc = input("\nEnter new location name: ").strip().title()
    if new_loc == "":
        print("Error: Name cannot be empty.")
        return

    if find_exact_name(new_loc, data["locations"]) is not None:
        print("This location already exists.")
        return

    data["locations"].append(new_loc)
    save_data(data)
    print("Added new location:", new_loc)


# 10. Menu Option 5: Add or update a path
def add_or_update_path(data):
    print("\n--- Add / Update Walking Path ---")
    loc1_input = input("Enter first location: ")
    loc2_input = input("Enter second location: ")

    loc1 = find_exact_name(loc1_input, data["locations"])
    loc2 = find_exact_name(loc2_input, data["locations"])

    if loc1 is None or loc2 is None:
        print("Error: Both locations must exist first.")
        return

    if loc1 == loc2:
        print("Error: Cannot connect a location to itself.")
        return

    try:
        dist = int(input("Enter distance in meters: "))
        if dist <= 0:
            print("Error: Distance must be greater than 0.")
            return
    except:
        print("Error: Please enter a valid number.")
        return

    # Check if path already exists and update it
    for path in data["paths"]:
        if (path["from"] == loc1 and path["to"] == loc2) or (
            path["from"] == loc2 and path["to"] == loc1
        ):
            path["distance"] = dist
            save_data(data)
            print("Updated distance to", dist, "meters.")
            return

    # Otherwise add as a brand new path
    data["paths"].append({"from": loc1, "to": loc2, "distance": dist})
    save_data(data)
    print("New path saved!")


# ------------------------------------------------------------------------------
# MEMBER 5: Campus Directory Viewing, Search & Main Interactive CLI Menu
# ------------------------------------------------------------------------------
# 6. Menu Option 1: View all locations 
def view_locations(data):
    print("\n--- Campus Locations ---")
    for count, loc in enumerate(data["locations"], start=1):
        print(f"{count}. {loc}")


# 7. Menu Option 2: Search location & see neighbors (E4: strip, lower)
def search_location(data, graph):
    keyword = input("\nEnter location name to search: ").strip().lower()
    if keyword == "":
        print("Please enter a valid name.")
        return

    found = False
    print("\n--- Search Results ---")
    for loc in data["locations"]:
        if keyword in loc.lower():
            found = True
            print("Location:", loc)
            neighbors = graph[loc]
            if len(neighbors) == 0:
                print("  Connected to: None")
            else:
                for place in neighbors:
                    print("  -> " + place + " (" + str(neighbors[place]) + "m)")

    if not found:
        print("No matching location found.")


# 11. Main Program Loop 
def main():
    while True:
        data = load_data()
        graph = build_graph(data)

        print("\n=====================================")
        print("   SMART CAMPUS NAVIGATION SYSTEM    ")
        print("=====================================")
        print("1. View All Campus Locations")
        print("2. Search Location & Connected Paths")
        print("3. Find Shortest Walking Route")
        print("4. Add New Campus Location")
        print("5. Add / Update Walking Path")
        print("6. Exit")
        print("=====================================")

        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            view_locations(data)
        elif choice == "2":
            search_location(data, graph)
        elif choice == "3":
            find_shortest_route(data, graph)
        elif choice == "4":
            add_location(data)
        elif choice == "5":
            add_or_update_path(data)
        elif choice == "6":
            print("Thank you for using Smart Campus Navigation!")
            break
        else:
            print("Invalid choice! Please enter 1 to 6.")


main()