from copy import deepcopy

from constants import *


class Controller():
    def __init__(self, grid, output_handler, game_over_handler):
        self.game_over_handler = game_over_handler
        self.output_handler = output_handler
#        self.shooting_handler = self.ui.shooting_handler
        self.grid = grid
        self.update_grid = self.grid.update
        self.cannon_col_location = 1
        self.next_row_countdown = 7
        self.game_over = False
        ###Begin Game###
#        self.output_handler(self.grid)

    def shoot(self, row, col, color):
        changed_bubbles, old_grid = self.collision(color, row, col)
        if self.next_row_countdown == 0:
            self.move_rows_down()
        self.output_handler(changed_bubbles, old_grid)

    def move_rows_down(self):
        bottom_row = self.grid.last_row_with_bubbles()
        if bottom_row:
            self.grid.add_new_row()
        else:
            self.game_over_handler()

    def collision(self, current_bullet, row, col):
        self.grid.update(row, col, current_bullet)
        locations_to_visit = [(row, col)]
        visited = [(row, col)]
        locations_to_pop = [(row, col)]
        old_grid = []
        while locations_to_visit:
            row, col = locations_to_visit.pop()
            for neighbor in self.grid.get_neighbor(row, col):
                if neighbor not in visited and neighbor not in locations_to_visit:
                    visited.append((neighbor[0], neighbor[1]))
                    cell = self.grid.get_cell(neighbor[0], neighbor[1])
                    if cell == current_bullet:
                        locations_to_visit.append((neighbor[0], neighbor[1]))
                        locations_to_pop.append((neighbor[0], neighbor[1]))

        if len(locations_to_pop) > 2:
            loose_bubbles, old_grid = self.resolve_pops(locations_to_pop)
            locations_to_pop.extend(loose_bubbles)
        else:
            self.next_row_countdown -= 1
        return locations_to_pop, old_grid

    def resolve_pops(self, locations_to_pop):
        old_grid = deepcopy(self.grid.grid)
        self.next_row_countdown = 7
        for location in locations_to_pop:
            self.grid.update(location[ROW_INDEX], location[COL_INDEX], EMPTY)
        ###Create a new empty grid
        new_grid = []
        for row in range(self.grid.get_row_size() + 2):
            new_row = []
            for col in range(self.grid.get_col_size() + 2):
                new_row.append(None)
            new_grid.append(new_row)
        to_visit = [(0, 0)]
        visited = []
        while to_visit:
            row, col = to_visit.pop()
            for neighbor in self.grid.get_neighbor(row, col):
                if neighbor not in to_visit and neighbor not in visited:
                    cell = self.grid.get_cell(neighbor[0], neighbor[1])
                    if cell:
                        to_visit.append((neighbor[0], neighbor[1]))
            visited.append((row, col))
            new_grid[row][col] = str(self.grid.get_cell(row, col))
        changed_bubbles = []
        for i, row in enumerate(self.grid.grid):
            for j, x in enumerate(row):
                if new_grid[i][j] != x:
                    changed_bubbles.append((i, j))
        self.grid.set_grid(new_grid)
        return changed_bubbles, old_grid