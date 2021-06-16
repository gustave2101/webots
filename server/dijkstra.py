from hungarian_algorithm import algorithm

INF = float('inf')

class Tile:
    def __init__(self, is_obstacle):
        self.visited = False
        self.distance = INF
        self.previous = None
        self.is_obstacle = is_obstacle

class Map:
    def __init__(self, text_map):
        self.width, self.height = Map.calculate_dimensions(text_map)
        self.tiles = list()

        for y, line in enumerate(text_map):
            for x, character in enumerate(line):
                if character == '.': # not an obstacle
                    self.tiles.append(Tile(False))
                elif character == 'O': # obstacle
                    self.tiles.append(Tile(True))
                else:
                    raise ValueError(
                        f'unknown tile type: \'{character}\' '
                        f'at ({str(x)}, {str(y)})'
                    )

    # returns tile at a position
    def at(self, position):
        return self.tiles[position[0] + position[1] * self.width]

    # checks whether a position is in the bounds of the map
    def in_bounds(self, position):
        return (
            position[0] >= 0 and position[0] < self.width
            and position[1] >= 0 and position[1] < self.height
        )
    
    # surrounding tiles, diagonals do not count
    def neighbors(self, position):
        p = position

        neighbors = [
            (p[0] - 1, p[1]),
            (p[0] + 1, p[1]),
            (p[0], p[1] - 1),
            (p[0], p[1] + 1)
        ]

        neighbors = [n for n in neighbors if self.in_bounds(n)]

        return neighbors
    
    def dijkstra(self, source, destination):
        self.at(source).distance = 0 # start gets a distance of 0

        while True:
            current_position = None
            current_distance = INF

            # find not visited tile with smallest distance
            for y in range(self.height):
                for x in range(self.width):
                    tile = self.at((x, y))

                    # pick any tile if no tile has been picked yet, else only pick
                    # the tile if the distance is smaller
                    # and ignore visited tiles and obstacles
                    if (
                        (tile.distance < current_distance or current_position == None)
                        and not (tile.visited or tile.is_obstacle)
                    ):
                        current_position = (x, y)
                        current_distance = tile.distance
            
            # mark tile as visited
            self.at(current_position).visited = True
            
            # positions of surrounding tiles
            neighbor_positions = self.neighbors(current_position)

            for position in neighbor_positions:
                if not self.at(position).is_obstacle:
                    tile = self.at(position)
                    distance = current_distance + 1 # all edges have a length of 1
                    if distance < tile.distance: # update distance if it is smaller
                        tile.distance = distance
                        tile.previous = current_position

            # return path if destination has been reached
            if current_position == destination:
                path = list()
                while current_position != None:
                    path.append(current_position)
                    current_position = self.at(current_position).previous # trace back
                path.reverse() # convert from last to first
                return path

    # calculates the dimensions of a text map, raises error if the map is jagged
    @staticmethod
    def calculate_dimensions(text):
        height = len(text)
        width = len(text[0])
        
        for row in text:
            if len(row) != width:
                raise ValueError('jagged list')
        
        return width, height

map = Map([
#     0    1    2    3    4
    ['.', '.', '.', '.', '.'], # 0
    ['.', '.', 'O', '.', '.'], # 1
    ['.', 'O', 'O', '.', '.'], # 2
    ['.', 'O', '.', '.', '.'], # 3
    ['.', 'O', '.', '.', '.'], # 4
])

path = map.dijkstra((0, 0), (2,3))
print(path)

targets = ((9,9),(9,8))

def calc_number_of_steps(path):

    return len(path)

print(calc_number_of_steps(path))

distances_to_targets = {
	'robot_1': { '1,1': 23, '9,8': 14} # "target:" : nr_of_steps
}

#print(algorithm.find_matching(H, matching_type = 'min', return_type = 'list' ))