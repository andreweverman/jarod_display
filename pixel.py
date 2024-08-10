import math


class Point:

    def __init__(self, x, y):
        self._x = x
        self._y = y

    def __str__(self):
        return f'({self._x}, {self._y})'

    def __repr__(self):
        return f'Point({self._x}, {self._y})'


class AnimationPixel(Point):

    def __init__(self, x, y,  dest: 'Point', acceleration=1):
        super().__init__(x, y)
        self.initial_position = Point(x, y)
        self.current_position = Point(x, y)
        self._velocity = 0
        self._acceleration = acceleration
        self._slope = 0
        self._destination = dest
        self._distance_to = self.calculate_distance(self.current_position, self._destination)
        self._slope = (dest._y - self._y)/(dest._x - self._x)
        self.t = 0

    def __str__(self):
        return f'Current Position: {self.current_position}'
    
    def __repr__(self):
        return f'AnimationPixel({self.current_position._x}, {self.current_position._y}, {self._destination})'

    def at_destination(self):
        return self.current_position == self._destination

    @staticmethod
    def calculate_distance( frm: 'Point', to: 'Point'):
        return abs(((frm._x - to._x)**2 + (frm._y - to._y)**2)**0.5)

    def calculate_distance_remaining(self):
        return self.calculate_distance(self.current_position, self._destination)

    def get_next_position(self):
        '''
        Calculate the next position of the pixel based on the velocity, acceleration and slope
        '''
        self.t += 1
        displacement = self._velocity * self.t + 0.5 * self._acceleration * self.t**2
        angle = math.atan(self._slope)

        direction_x = 1 if self._destination._x > self.initial_position._x else -1
        direction_y = 1 if self._destination._y > self.initial_position._y else -1

        self.current_position._x = self.initial_position._x + direction_x * displacement * math.cos(angle)
        self.current_position._y = self.initial_position._y + direction_y * displacement * math.sin(angle)
        # self.current_position._x = self.initial_position._x + \
        #     displacement * math.cos(angle)
        # self.current_position._y = self.initial_position._y + \
        #     displacement * math.sin(angle)
        
        self._distance_traveled_total = self.calculate_distance(self.initial_position, self.current_position)
        if self._distance_traveled_total >= self._distance_to:
            self.current_position = self._destination
            self._distance_remaining = 0
        else:
            self._distance_remaining = self.calculate_distance(self.current_position, self._destination)

        return self.current_position


