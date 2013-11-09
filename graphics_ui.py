from random import choice, randrange, random
from math import acos, pi, floor

from OpenGL.GL import *
from OpenGL.GLUT import *

from constants import *
from grid import Grid
from controller import Controller


class Visualizer():
    '''
    0, 540              540, 540

            275, 275

    0,0                 540, 0
    '''
    def __init__(self, height=STANDARD_HEIGHT, width=STANDARD_WIDTH):
        ###Window Information
        self.rad = RADIUS
        self.height = height
        self.width = width
        self.controller = None
        self.grid = None
        ###Cannon and Bullet
        self.cannon_to_mouse = 0                        #Vector from cannon to mouse
        self.unit_vector = 0                            #Vector from cannon to mouse in Unit form
        self.mouse_location = [self.width/2, 30]        #Location of Mouse, starts at cannon
        self.bullet_location = [self.width/2, 30]       #Location of Bullet, starts at cannon
        self.bullet_color = choice(color_dict.keys())
        self.shooting = False
        self.falling_list = []
        self.game_over = False
        ###OpenGL Setup
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Initialize modes
        glutInitWindowSize(height, width)
        glutCreateWindow("Bubbly")
        glutReshapeFunc(self.reshape)
        glutDisplayFunc(self.display)
        glutMouseFunc(self.on_click)
        glutKeyboardUpFunc(self.on_keyboard_up)
        glutPassiveMotionFunc(self.mouse_tracker)
        self.set_up()
        glutMainLoop()

    ###Window and Display
    def set_up(self):                                             # Initialization routine
        glClearColor(1.0, 1.0, 1.0, 0.0)
        glColor3f(0.0, 0.0, 0.0)
        glPointSize(POINT_SIZE)

    def reshape(self, height, width):
        if height >= 90 and width >= 90 or (self.height != height and self.width != width):
            if height > width:
                self.height = height
                self.width = height
            else:
                self.height = width
                self.width = width
#            self.height = height
#            self.width = width
            grid_height = self.point_to_index(self.height)
            grid_width = self.point_to_index(self.width)
            self.grid = Grid(grid_width, grid_height)
            self.controller = Controller(self.grid, self.initial_falling, self.flip_game_over)
            glViewport(0, 0, self.height, self.width)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glOrtho(0.0, self.width, 0.0, self.height, -100.0, 100.0)
            glEnable(GL_DEPTH_TEST)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear Color and Depth
        if self.game_over:
            game_over_text = "Game Over. Press 'r' to Restart."
            glRasterPos(150, 250, 0)
            for letter_index, letter in enumerate(game_over_text):
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(letter))
        else:
            for row_index, row in enumerate(self.grid.grid):
                for col_index, color_key in enumerate(row):
                    if color_key:
                        x_point = self.index_to_point(col_index)
                        y_point = self.height - self.index_to_point(row_index)
                        self.draw_bubble_at_location(x_point, y_point, color_key)
            self.draw_cannon()
            if self.shooting:
                self.draw_shot_bullet()
            self.draw_falling()
        glFlush()
        glutSwapBuffers()
        glutPostRedisplay()

    def flip_game_over(self):
        self.game_over = True

    ###Drawing
    def draw_bubble_at_location(self, x, y, color_key, radius=RADIUS, z=0.0):
        glPushMatrix()
        glTranslatef(x, y, z)    # Move reference point
        color = color_dict[color_key]
        glColor3f(color[0], color[1], color[2])        # Set the color
        glutSolidSphere(radius, 50, 2)  # Draw sphere
        glPopMatrix()                    # Return to first reference

    def draw_cannon(self):
        glPushMatrix()
        glTranslatef(self.width / 2, 0, 1.0)
        rotation_angle = self.cannon_rotation()
        glRotatef(rotation_angle, 0, 0, 1)
        glutSolidSphere(10, 50, 2)
        glTranslatef(0, 30, 1.0)
        self.draw_loaded_bullet()
#        self.bullet_location = [self.width/2 + 30 * cos(rotation_angle), 30 * sin(rotation_angle)]
        glRotatef(90.0, 1, 0, 0)
        glColor3f(0.0, 0.0, 0.0)
        glutSolidCone(10, 30, 10, 10)
        glPopMatrix()

    def draw_loaded_bullet(self):
        if not self.shooting:
            glPushMatrix()
            color = color_dict[self.bullet_color]
            glColor3f(color[0], color[1], color[2])
            glutSolidSphere(10, 50, 2)
            glPopMatrix()

    def draw_shot_bullet(self):
        if int(self.bullet_location[1]) >= self.height - 10:
            self.shooting = False
            self.bullet_location = [self.width/2, 30]
        else:
            ###Move bullet
            if self.bullet_location[0] >= self.width - 10 or self.bullet_location[0] <= 10:
                self.unit_vector[0] *= -1
            next_x = self.bullet_location[ROW_INDEX] + self.unit_vector[ROW_INDEX] * MOVEMENT_SPEED
            next_y = self.bullet_location[COL_INDEX] + self.unit_vector[COL_INDEX] * MOVEMENT_SPEED
            if self.collision(next_x, next_y):
                if next_y < 40:
                    self.flip_game_over()
                x_index = self.point_to_index(self.bullet_location[ROW_INDEX])
                y_index = self.point_to_index(self.bullet_location[COL_INDEX])
                self.bullet_location[ROW_INDEX] = self.index_to_point(x_index)
                self.bullet_location[COL_INDEX] = self.index_to_point(y_index)
                self.shooting = False
                self.bullet_location = [self.width / 2, 30]
                self.bullet_color = choice(color_dict.keys())

            else:
                self.bullet_location[ROW_INDEX] += self.unit_vector[ROW_INDEX] * MOVEMENT_SPEED
                self.bullet_location[COL_INDEX] += self.unit_vector[COL_INDEX] * MOVEMENT_SPEED
            self.draw_bubble_at_location(self.bullet_location[ROW_INDEX], self.bullet_location[COL_INDEX], self.bullet_color)

    def draw_falling(self):
        if self.falling_list:
            DIRECTION = 0
            LOC = 1
            COLOR = 2
            UP_RATE = 3
            Z_MOTION = 3
            prev_bubble_col = 0
            prev_bubble_row = 0
            new_falling = list(self.falling_list)
            for bubble in self.falling_list:
                if bubble[LOC][COL_INDEX] > -45.0:
                    bubble[LOC][ROW_INDEX] += bubble[DIRECTION] * MOVEMENT_SPEED
                    prev_bubble_row = bubble[LOC][ROW_INDEX]
                    if bubble[UP_RATE] > 0:
                        bubble[UP_RATE] -= 1
                        bubble[LOC][COL_INDEX] += self.unit_vector[COL_INDEX] * MOVEMENT_SPEED * (bubble[UP_RATE]/17)
                    else:
                        bubble[LOC][COL_INDEX] -= self.unit_vector[COL_INDEX] * MOVEMENT_SPEED
                        prev_bubble_col = bubble[LOC][COL_INDEX]
                        for tail in range(25):
                            prev_bubble_col += self.unit_vector[COL_INDEX] * MOVEMENT_SPEED * 1.5
                            prev_bubble_row -= bubble[DIRECTION] * MOVEMENT_SPEED * 1.5
                            self.draw_bubble_at_location(prev_bubble_row,
                                                         prev_bubble_col, bubble[COLOR], self.rad-tail)
                    if self.rad < 30:
                        self.rad += .03
                    self.draw_bubble_at_location(bubble[LOC][ROW_INDEX],
                                                 bubble[LOC][COL_INDEX], bubble[COLOR], self.rad, 50)
                else:
                    self.falling_list.remove(bubble)
                    self.rad = RADIUS

    ####Colision Detection
    def initial_falling(self, falling, old_grid):
        if old_grid:
            self.falling_list = []
            for bubble in falling:
                color = old_grid[bubble[ROW_INDEX]][bubble[COL_INDEX]]
                y = self.height - self.index_to_point(bubble[ROW_INDEX])
                x = self.index_to_point(bubble[COL_INDEX])
                self.falling_list.append([random() * randrange(-2, 2), [x, y], color, MOVEMENT_UP, randrange(0, 2)])

    def collision(self, next_x, next_y):
        x_index = self.point_to_index(next_x)
        y_index = self.point_to_index(next_y)
        y_index = self.grid.get_col_size() - y_index
        cell = self.grid.get_cell(y_index, x_index)
        if cell:
            next_x -= self.unit_vector[ROW_INDEX] * MOVEMENT_SPEED
            next_y -= self.unit_vector[COL_INDEX] * MOVEMENT_SPEED
            x_index = self.point_to_index(next_x)
            y_index = self.point_to_index(next_y)
            y_index = self.grid.get_col_size() - y_index
            self.controller.shoot(y_index, x_index, self.bullet_color)
        return cell

    ###Input
    def on_keyboard_up(self, key, x, y):
        if key == 'r':
            self.game_over = False
            self.reshape(self.height, self.width)

    def mouse_tracker(self, x, y):
        self.mouse_location = x, self.height-y
        self.cannon_to_mouse = self.points_to_vector((self.width / 2, 0), self.mouse_location)

    def on_click(self, button, state, x, y):
        if (not self.shooting) and button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            self.shooting = True
            length = self.length(self.cannon_to_mouse)
            self.unit_vector = [self.cannon_to_mouse[0] / length, self.cannon_to_mouse[1] / length]

    ###Location Information
    def point_to_index(self, point):
        return int(floor(point/(RADIUS*2)))

    def index_to_point(self, index):
        return int((RADIUS * 2) * (index + .5))

    ###Angle
    def cannon_rotation(self):
        base_vector = (0, 1)
        self.cannon_to_mouse = self.points_to_vector((self.width / 2, 0), self.mouse_location)
        a = self.angle(self.cannon_to_mouse, base_vector)
        return a

    def points_to_vector(self, point1, point2):
        return point2[0] - point1[0], point2[1] - point1[1]

    #http://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python
    def dot_product(self, vector1, vector2):
        return vector1[0] * vector2[0] + vector1[1] * vector2[1]

    def length(self, vector):
        return (self.dot_product(vector, vector)) ** .5

    def angle(self, vector1, vector2):
        dot_a_b = self.dot_product(vector1, vector2)
        len_a_b = (self.length(vector1)) * (self.length(vector2))
        angle = acos(dot_a_b / len_a_b) * 180 / pi
        if self.mouse_location[0] > self.width / 2:
            angle *= -1
        return angle

Visualizer()