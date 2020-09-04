
import cv2
import random
import time
import numpy as np

TILE_SIZE = 32
OFS = 50


MARKET = """
##################
##..............##
##..pq..aw..db..##
##..pq..aw..db..##
##..pq..aw..db..##
##..pq..aw..db..##
##..pq..aw..db..##
##...............#
##..xy..zx..xm...#
##..yx..xz..mx...#
##............s.s#
##################
""".strip()


class TiledMap:

    def __init__(self, layout, tiles):
        self.tiles = tiles
        self.contents = [list(row) for row in layout.split('\n')]
        self.xsize = len(self.contents[0])
        self.ysize = len(self.contents)
        self.image = np.zeros((self.ysize * TILE_SIZE, self.xsize * TILE_SIZE, 3), dtype=np.uint8)
        self.prepare_map()

    def get_tile_bitmap(self, char):
        if char == '#':
            return self.tiles[0:32, 0:32, :]
        elif char == 'b':
            return self.tiles[0:32, 128:160, :]
        elif char == 'd':
            return self.tiles[64:96, 128:160, :]
        elif char == 'w':
            return self.tiles[96:128, 128:160, :]
        elif char == 'a':
            return self.tiles[96:128, 160:192, :]
        elif char == 'q':
            return self.tiles[32:64, 128:160, :]
        elif char == 'p':
            return self.tiles[64:96, 192:224, :]
        elif char == 'x':
            return self.tiles[128:160, 128:160, :]
        elif char == 'y':
            return self.tiles[192:224, 96:128, :]
        elif char == 'z':
            return self.tiles[160:192, 96:128, :]
        elif char == 'm':
            return self.tiles[96:128, 224:256, :]
        elif char == 's':
            return self.tiles[32:64, 0:32, :]
        else:
            return self.tiles[32:64, 64:96, :]

    def prepare_map(self):
        for y, row in enumerate(self.contents):
            for x, tile in enumerate(row):
                bm = self.get_tile_bitmap(tile)
                self.image[y * TILE_SIZE:(y+1)*TILE_SIZE, x * TILE_SIZE:(x+1)*TILE_SIZE] = bm

    def draw(self, frame):
        frame[OFS:OFS+self.image.shape[0], OFS:OFS+self.image.shape[1]] = self.image


class Customer:
    """
    Customer class that models the customer behavior in a supermarket.
    """

    def __init__(self, tmap, image, x, y, current_location):
        self.tmap = tmap
        self.image = image
        self.x = x
        self.y = y
        self.current_location = current_location
        self.possible_locations = ['dairy', 'drinks', 'fruits', 'spices']
        self.transition_probabilities = {
            'dairy': [0.837575, 0.006778, 0.078079, 0.077567],
            'drinks': [0.121551, 0.677844, 0.081383, 0.119222],
            'fruits': [0.089918, 0.086386, 0.765668, 0.058028],
            'spices': [0.185688, 0.171498, 0.130955, 0.511859]}

    def change_location(self):
        """
        Choses a new location among the provided locations.

        Parameters
        ----------
        possible_locations : The locations the customer might transition to.
        """
        newx = self.x
        newy = self.y
        new_location = random.choices(self.possible_locations, self.transition_probabilities[self.current_location])[0]

        self.current_location = new_location
        if self.current_location == 'spices':
            newx = OFS + TILE_SIZE * np.random.randint(11, 12)
            newy = OFS + TILE_SIZE * np.random.randint(1, 10)
        elif self.current_location == 'fruits':
            newx = OFS + TILE_SIZE * np.random.randint(14, 15)
            newy = OFS + TILE_SIZE * np.random.randint(1, 10)
        elif self.current_location == 'drinks':
            newx = OFS + TILE_SIZE * np.random.randint(3, 4)
            newy = OFS + TILE_SIZE * np.random.randint(1, 10)
        elif self.current_location == 'dairy':
            newx = OFS + TILE_SIZE * np.random.randint(6, 7)
            newy = OFS + TILE_SIZE * np.random.randint(1, 10)
        frame[newy:newy+TILE_SIZE, newx:newx+TILE_SIZE] = self.image

    def __repr__(self):
        return f'''is in location {self.current_location}'''


class Ghost:

    def __init__(self, tmap, image, x, y):
        self.tmap = tmap
        self.image = image
        self.x = x
        self.y = y

    def draw(self, frame):              # puts the ghost-object onto the map
        xpos = OFS + self.x * TILE_SIZE
        ypos = OFS + self.y * TILE_SIZE
        frame[ypos:ypos+TILE_SIZE, xpos:xpos+TILE_SIZE] = self.image

    def move(self):
        newx = self.x
        newy = self.y
        newy += random.randint(-1, 1)
        newx += random.randint(-1, 1)
        if self.tmap.contents[newy][newx] != '#':
            self.x = newx
            self.y = newy


background = np.zeros((700, 1000, 3), np.uint8)
tiles = cv2.imread('tiles2.png')

customer_1 = tiles[1*TILE_SIZE:2*TILE_SIZE, -2*TILE_SIZE:-1*TILE_SIZE, :]
customer_2 = tiles[2*TILE_SIZE:3*TILE_SIZE, -1*TILE_SIZE:, :]
customer_3 = tiles[:1*TILE_SIZE, -1*TILE_SIZE:, :]
customers = [customer_1, customer_2, customer_3]
customer = random.choice(customers)

ghost_trump = tiles[2*TILE_SIZE:3*TILE_SIZE, -3*TILE_SIZE:-2*TILE_SIZE, :]

possible_locations = ['dairy', 'drinks', 'fruits', 'spices']

tmap = TiledMap(MARKET, tiles)

c = Customer(tmap, customer, 15, 10, 'spices')
g = Ghost(tmap, ghost_trump, 12, 9)


# infinite loop to refresh the frame with supermarket and customers on
while True:
    frame = background.copy()
    tmap.draw(frame)

    c.change_location()

    g.move(frame)
    g.draw(frame)

    cv2.imshow('frame', frame)

    key = chr(cv2.waitKey(1) & 0xFF)
    time.sleep(0.5)

    if key == 'q':
        break

cv2.destroyAllWindows()
