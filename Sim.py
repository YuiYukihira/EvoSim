#!/usr/bin/env python

from __future__ import annotations

from Graphics import Graphics
from typing import Tuple
from MapUtils import Vector, RadianAngle, PolarVector
from random import randint, uniform
from Creature import *
from math import pi, radians

class Simulation(Graphics):
    def __init__(self, field_space: Tuple[Vector, Vector], display_size: Vector):
        super().__init__(field_space, display_size)
        self.creatures = self._create_starting_creatures()
        self.food = generate_food_list(field_space, 50)
        
    def _create_starting_creatures(self):
        creatures = []
        for i in range(1):
            senseg = Gene(10, 0, (lambda x: x+randint(-1, 1)))
            speedg = Gene(PolarVector(BASE_TURN_SPEED, BASE_MOVE_SPEED), 10,
                          (lambda x: PolarVector((x.angle+radians(randint(-2,2)) % (2*pi)), x.magnitude+randint(-2,2))))
            sizeg  = Gene(1, 20, (lambda x: x+randint(-5, 5)))
            start_pos, start_heading = self._get_start_pos()
            creatures.append(Creature(start_pos, 10000,
                                      senseg, sizeg, speedg,
                                      start_heading))
        return creatures
            
    def tick_once(self) -> bool:
        for creature in self.creatures:
            creature.calculate_turn(self.food, self.field_space)
            # Remove any eaten field
            self.food = list(filter(lambda x: not x.eaten, self.food))
        super().draw(self.creatures, self.food)
        
    def run(self, trials: int):
        done_trials = 0
        while done_trials < trials:
            while not all(map(lambda c: c.task_finished or c.energy == 0, self.creatures)):
                self.tick_once()
            self.creatures = list(filter(lambda c: c.task_finished), self.creatures)
            new_creatures = []
            for creature in self.creatures:
                if creature.energy >= 150:
                    new_creatures.append(creature.reproduce())
            self.creatures += new_creatures
            self.food = generate_food_list(field_space, len(self.creatures))
            
            
    def _get_start_pos(self):
        wall = randint(1,4)
        if wall == 1:
            x1, x2 = self.field_space[0].x, self.field_space[1].x
            y = self.field_space[1].y
            return Vector(randint(x1, x2), y), RadianAngle(uniform(pi/2, pi*(3/2)))
        if wall == 2:
            y1, y2 = self.field_space[0].y, self.field_space[1].y
            x = self.field_space[1].x
            return Vector(x, randint(y1, y2)), RadianAngle(uniform(pi, pi*2))
        if wall == 3:
            x1, x2 = self.field_space[0].x, self.field_space[1].x
            y = self.field_space[0].y
            return Vector(randint(x1, x2), y), RadianAngle(uniform(pi*(3/2), pi/2) % 2*pi)
        if wall == 4:
            y1, y2 = self.field_space[0].y, self.field_space[1].y
            x = self.field_space[0].x
            return Vector(x, randint(y1, y2)), RadianAngle(uniform(0, pi))

def main():
    s = Simulation((Vector(0,0), Vector(200,200)), Vector(1920,1080))
    s.run(50)
    
if __name__ == '__main__':
    main()
