from collections import deque
import heapq


class Game:
    def __init__(self, game_map_string):
        self.game_map = []
        lines = game_map_string.split('\n')
        for i in range(len(lines)):
            line = [cell.split("/") for cell in lines[i].strip().split()]
            self.game_map.append(line)

        self.height = len(self.game_map)
        self.width = len(self.game_map[0])
        number_of_boxes = game_map_string.count('B')
        number_of_portals = game_map_string.count('P')
        self.boxes = [0] * number_of_boxes
        self.goals = [0] * number_of_boxes
        self.portals = [[] for _ in range(number_of_portals // 2)]
        self.map_size = len(lines)
        self.num_boxes = number_of_boxes

        # Initialize positions
        for i in range(len(self.game_map)):
            for j in range(len(self.game_map[i])):
                static_element = '.'
                for k in range(len(self.game_map[i][j])):
                    cell_val = self.game_map[i][j][k]
                    if cell_val.startswith('H'):
                        self.player_pos = (i, j)
                    elif cell_val.startswith('B'):
                        idx = int(cell_val[1:]) - 1
                        self.boxes[idx] = (i, j)
                    elif cell_val.startswith('G'):
                        idx = int(cell_val[1:]) - 1
                        self.goals[idx] = (i, j)
                        static_element = cell_val
                    elif cell_val.startswith('P'):
                        idx = int(cell_val[1:]) - 1
                        self.portals[idx].append((i, j))
                        static_element = cell_val
                    elif cell_val.startswith('W'):
                        static_element = 'W'

                # We only save the static element in the map array for optimization
                self.game_map[i][j] = static_element

    def clone(self):
        blank_map_lines = []
        for _ in range(self.height):
            blank_map_lines.append(' '.join(['.' for _ in range(self.width)]))
        blank_map_string = '\n'.join(blank_map_lines)
        new_game = Game(blank_map_string)

        # Copy
        new_game.game_map = [row[:] for row in self.game_map]
        new_game.height = self.height
        new_game.width = self.width

        new_game.player_pos = self.player_pos
        new_game.boxes = self.boxes[:]
        new_game.goals = self.goals[:]
        new_game.portals = [p[:] for p in self.portals]

        return new_game

    def set_player_position(self, pos):
        self.player_pos = pos

    def set_box_positions(self, boxes):
        self.boxes = [box for box in boxes]

    def get_map_size(self):
        return [self.height, self.width]

    def get_box_locations(self):
        return [box for box in self.boxes]

    def get_goal_locations(self):
        return [goal for goal in self.goals]

    def get_portal_locations(self):
        return self.portals

    def get_player_position(self):
        return self.player_pos

    def is_wall(self, pos):
        return self.__is_pos_out_of_bounds(pos)
    #It's time-consuming
    def get_elements_in_position(self, pos):

        if self.__is_pos_out_of_bounds(pos):
            return ["W"]
        elements = []
        if self.game_map[pos[0]][pos[1]] != '.':
            elements.append(self.game_map[pos[0]][pos[1]])
        for i in range(len(self.boxes)):
            if self.boxes[i] == pos:
                elements.append(f'B{i + 1}')
        if self.player_pos == pos:
            elements.append('H')
        if len(elements) == 0:
            elements.append('.')
        return elements
    #It's time-consuming
    def get_map(self):

        game_map_copy = [[[cell] for cell in row] for row in self.game_map]
        for i in range(len(self.boxes)):
            box = self.boxes[i]
            game_map_copy[box[0]][box[1]].append(f'B{i + 1}')
        game_map_copy[self.player_pos[0]][self.player_pos[1]].append('H')

        result = []
        for i in range(len(game_map_copy)):
            row = []
            for j in range(len(game_map_copy[i])):
                cell = game_map_copy[i][j]
                if len(cell) > 1 and cell[0] == '.':
                    cell = cell[1:]
                row.append('/'.join(cell))
            result.append('\t'.join(row))
        return '\n'.join(result)

    def display_map(self):
        print(self.get_map())

    def apply_move(self, direction):
        direction_map = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
        dy, dx = direction_map[direction]
        human_new_pos = self.__calculate_new_pos(self.player_pos, (dy, dx))

        if self.__is_pos_out_of_bounds(human_new_pos):
            return False

        box_id = self.__get_element_id_in_cell(human_new_pos, 'B')
        if box_id is not None:
            box_new_pos = self.__calculate_new_pos(self.boxes[box_id - 1], (dy, dx))
            if not self.__validate_box_new_pos(box_new_pos):
                return False
            self.boxes[box_id - 1] = box_new_pos

        self.player_pos = human_new_pos
        return True

    def apply_moves(self, moves):
        for move in moves:
            try:
                self.apply_move(move)
            except ValueError:
                pass

    def is_game_won(self):
        for i in range(len(self.boxes)):
            if self.boxes[i] != self.goals[i]:
                return False
        return True

    def is_solution_valid(self, solution):
        self.apply_moves(solution)
        return self.is_game_won()

    def __calculate_new_pos(self, current_pos, direction):
        (dy, dx) = direction
        new_pos = (current_pos[0] + dy, current_pos[1] + dx)
        portal_id = self.__get_element_id_in_cell(new_pos, 'P')
        if portal_id is not None:
            portal_idx = portal_id - 1
            if len(self.portals[portal_idx]) == 2:
                if new_pos == self.portals[portal_idx][0]:
                    return (self.portals[portal_idx][1][0] + dy, self.portals[portal_idx][1][1] + dx)
                else:
                    return (self.portals[portal_idx][0][0] + dy, self.portals[portal_idx][0][1] + dx)
        return new_pos

    def __is_pos_out_of_bounds(self, pos):
        return (pos[0] < 0 or pos[0] >= self.height or
                pos[1] < 0 or pos[1] >= self.width or
                self.game_map[pos[0]][pos[1]][0] == 'W')

    def __validate_box_new_pos(self, pos):
        if self.__is_pos_out_of_bounds(pos):
            return False
        if self.__get_element_id_in_cell(pos, 'B') is not None:
            return False
        return True

    def __get_element_id_in_cell(self, pos, element):
        if pos[0] < 0 or pos[0] >= self.height or pos[1] < 0 or pos[1] >= self.width:
            return None
        if element == "B":
            for i in range(len(self.boxes)):
                if self.boxes[i] == pos:
                    return i + 1
        # If we're checking for a portal 'P' + number
        if len(self.game_map[pos[0]][pos[1]]) > 1 and self.game_map[pos[0]][pos[1]][0] == element:
            return int(self.game_map[pos[0]][pos[1]][1:])
        return None


    #  searching methods

    #1 uniformed bfs
    @staticmethod
    def bfs_solve(initial_game: "Game"):
        start_state = (
            initial_game.get_player_position(),
            tuple(sorted(initial_game.get_box_locations()))
        )

        if initial_game.is_game_won():
            return ""

        queue = deque([(start_state, "")])
        visited = set([start_state])

        while queue:
            (player_pos, boxes), path = queue.popleft()


            for move in ['U', 'D', 'L', 'R']:
                cloned = initial_game.clone()
                cloned.set_player_position(player_pos)
                cloned.set_box_positions(boxes)

                if cloned.apply_move(move):
                    new_state = (
                        cloned.get_player_position(),
                        tuple(sorted(cloned.get_box_locations()))
                    )
                    if new_state in visited:
                        continue

                    visited.add(new_state)
                    new_path = path + move

                    if cloned.is_game_won():
                        return new_path
                    queue.append((new_state, new_path))

        return None

    #2 uniformed dfs
    @staticmethod
    def dfs_solve(initial_game: "Game", max_depth=9999):
        start_state = (
            initial_game.get_player_position(),
            tuple(sorted(initial_game.get_box_locations()))
        )

        visited = set()
        return Game._dfs_recursive(initial_game, start_state, "", visited, 0, max_depth)

    @staticmethod
    def _dfs_recursive(game: "Game", state, path, visited, depth, max_depth):
        if depth > max_depth:
            return None

        (player_pos, boxes) = state


        cloned = game.clone()
        cloned.set_player_position(player_pos)
        cloned.set_box_positions(boxes)
        if cloned.is_game_won():
            return path

        visited.add(state)

        for move in ['U', 'D', 'L', 'R']:
            next_clone = cloned.clone()
            if next_clone.apply_move(move):
                new_state = (
                    next_clone.get_player_position(),
                    tuple(sorted(next_clone.get_box_locations()))
                )
                if new_state not in visited:
                    result = Game._dfs_recursive(game, new_state, path + move, visited, depth + 1, max_depth)
                    if result is not None:
                        return result

        return None

    #3 uniformed ids
    @staticmethod
    def ids_solve(initial_game: "Game", max_depth=50):
        for limit in range(max_depth + 1):
            visited = set()
            start_state = (
                initial_game.get_player_position(),
                tuple(sorted(initial_game.get_box_locations()))
            )
            result = Game._dls(initial_game, start_state, "", visited, 0, limit)
            if result is not None:
                return result
        return None

    @staticmethod
    def _dls(game: "Game", state, path, visited, depth, limit):
        if depth > limit:
            return None

        (player_pos, boxes) = state
        cloned = game.clone()
        cloned.set_player_position(player_pos)
        cloned.set_box_positions(boxes)

        if cloned.is_game_won():
            return path

        visited.add(state)

        for move in ['U', 'D', 'L', 'R']:
            next_clone = cloned.clone()
            if next_clone.apply_move(move):
                new_state = (
                    next_clone.get_player_position(),
                    tuple(sorted(next_clone.get_box_locations()))
                )
                if new_state not in visited:
                    result = Game._dls(game, new_state, path + move, visited, depth + 1, limit)
                    if result is not None:
                        return result
        return None

    @staticmethod
    # sum of Manhattan distances from each box to its goal
    def heuristic(box_positions, goal_positions):
        total = 0
        for b, g in zip(box_positions, goal_positions):
            br, bc = b
            gr, gc = g
            total += abs(br - gr) + abs(bc - gc)
        return total

    @staticmethod
    #4 a*
    def astar_solve(initial_game: "Game"):

        def manhattan_heuristic(boxes, goals):
            return Game.heuristic(sorted(boxes), sorted(goals))

        start_state = (
            initial_game.get_player_position(),
            tuple(sorted(initial_game.get_box_locations()))
        )

        if initial_game.is_game_won():
            return ""

        open_list = []
        visited = {}

        h0 = manhattan_heuristic(initial_game.get_box_locations(), initial_game.get_goal_locations())
        heapq.heappush(open_list, (h0, 0, start_state, ""))

        while open_list:
            f, g, (player_pos, boxes), path = heapq.heappop(open_list)

            if (player_pos, boxes) in visited and visited[(player_pos, boxes)] < g:
                continue

            current_clone = initial_game.clone()
            current_clone.set_player_position(player_pos)
            current_clone.set_box_positions(boxes)

            if current_clone.is_game_won():
                return path

            for move in ['U', 'D', 'L', 'R']:
                neighbor_clone = current_clone.clone()
                if neighbor_clone.apply_move(move):
                    new_state = (
                        neighbor_clone.get_player_position(),
                        tuple(sorted(neighbor_clone.get_box_locations()))
                    )
                    new_g = g + 1
                    if new_state not in visited or visited[new_state] > new_g:
                        visited[new_state] = new_g
                        h_val = manhattan_heuristic(neighbor_clone.get_box_locations(),
                                                    neighbor_clone.get_goal_locations())
                        new_f = new_g + h_val
                        heapq.heappush(open_list, (new_f, new_g, new_state, path + move))

        return None
