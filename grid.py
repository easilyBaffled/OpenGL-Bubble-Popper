from random import choice

from constants import *


class Grid():
    def __init__(self, col, row, next_bullet='0'):
        self.grid = []
        self.row = row
        self.col = col
        for current_row in range(self.row):
            if current_row < self.row / 2:
                grid_row = []
                for current_col in range(self.col):
                    grid_row.append(choice(color_dict.keys()))
                self.grid.append(grid_row)
            else:
                self.grid.append([None] * self.col)

    def __str__(self):
        output = ''
        for row in self.grid:
            for bubble in row:
                output += str(bubble) + ' '
            output += '\n'
        return output

    def get_col_size(self):
        return self.col - 1

    def get_row_size(self):
        return self.row - 1

    def set_grid(self, grid):
        self.grid = grid

    def update(self, row, col, new_object):
        self.grid[row][col] = new_object

    def get_cell(self, row, col):
        return self.grid[row][col]

    def get_legal_location(self, row, col):
        try:
            self.grid[row][col]
            return True
        except IndexError:
            return False

    def get_bubbles(self):
        bubble_grid = []
        for row_index, row in enumerate(self.grid):
            if row_index != len(self.grid) - 1:
                row = []
                for cell_index, cell, in enumerate(row):
                    row.append(cell)
                bubble_grid.append(row)
        return bubble_grid

    def get_neighbor(self, row, col):
        neighbor_list = []
        for direction in neighbor_dirs:
            temp_row = row - direction[ROW_INDEX]
            temp_col = col - direction[COL_INDEX]
            if 0 <= temp_row < (len(self.grid)) and 0 <= temp_col < (len(self.grid[0])):
                neighbor_list.append((temp_row, temp_col))
        return neighbor_list

    def last_row_with_bubbles(self):
        '''
        last_row_with_bubbles() -> None
        starting from the bottom row, iterate through the coloms in the row.
        Once you find a non-empty cell, move up a row
        If you make it through a whole row without hitting a character, return that row.
        If the row is the bottom row, return none to signify game over
        '''
        row_index = len(self.grid) - 2
        col_index = 0
        while col_index < (len(self.grid[0]) - 1) or row_index > 0:
            cell = self.grid[row_index][col_index]
            if cell == EMPTY and col_index < (len(self.grid[0]) - 1):
                col_index += 1
            else:
                col_index = 0
                row_index -= 1
        if row_index != len(self.grid) - 2:
            return row_index
        else:
            return None

    def add_new_row(self):
        '''
        new_grid = []
        new_row = []
        for cell in range(len(self.grid[0])):
            new_row.append(choice(color_dict.keys()))
        new_grid.append(new_row)
        for row_index, row in enumerate(self.grid):
            new_row = []
            for col_index, col in enumerate(row):
                new_row.append(col)
            new_grid.append(new_row)
        self.grid = new_grid
        '''

        new_row = []
        for cell in range(len(self.grid[0])):
            new_row.append(choice(color_dict.keys()))
        self.grid.insert(0, new_row)
        self.grid.pop()
