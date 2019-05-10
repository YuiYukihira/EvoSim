#!/usr/bin/env python
from __future__ import annotations

from MapUtils import Vector, PolarVector, dist
from abc import ABC, abstractmethod
from typing import Callable, List, Any, Tuple
from random import randint, uniform
import math

BASE_TURN_SPEED = math.radians(20)
BASE_MOVE_SPEED = 1
BASE_TURN_ENRGY = 1
BASE_MOVE_ENRGY = 1

class Gene(object):
    __slots__ = ["val", "mutation_chance", "mutation_change"]
    def __init__(self, val: Any, mutation_chance: int, mutation_change: Callable[[Any], Any]):
        self.val = val
        self.mutation_chance = mutation_chance
        self.mutation_change = mutation_change
        
        def _mutate(self) -> Gene:
            return Gene(self.mutation_change(self.val), self.mutation_chance, mutation_change)
        
        def reproduce(self) -> Gene:
            if randint(0, 100) < self.mutation_chance:
                return self._mutate()
            return copy(self)
        
    def __copy__(self):
        return type(self)(copy(self.val), self.mutation_chance, self.mutation_change)
        
class Creature(object):
    def __init__(self, start_position: Position, start_energy: int, 
               sense_gene: Gene, size_gene: Gene, speed_gene: Gene,
               start_heading: RadianAngle):
        self.position = start_position
        self.heading  = start_heading
        self.energy   = start_energy
        self.senseg   = sense_gene
        self.sizeg    = size_gene
        self.speedg   = speed_gene
        
        self.task_finished = False
        self.got_food = False
        
    def reproduce(self) -> Creature:
        self.energy -= 50
        return Creature(self.position, 100,
                   self.senseg.reproduce(),
                   self.sizeg.reproduce(),
                   self.speedg.reproduce())
    
    def move(self, target: Vector) -> Tuple[Vector, PolarVector]:
        # Find change in heading
        new_course = PolarVector.fromVector(self.position - target)
        course_correction = new_course.angle - self.heading
       # print(f"Angle change: {course_correction}")
        muli = -1 if course_correction > math.pi else 1
        if (2*math.pi) - course_correction < self.speedg.val.angle:
            correction_to_make = muli*(2*math.pi - course_correction)
        else:
            correction_to_make = muli*self.speedg.val.angle
        
        # Now change the heading
        self.heading = (self.heading + correction_to_make) % 2*math.pi
        self.energy -= BASE_TURN_ENRGY*(correction_to_make/BASE_TURN_SPEED)
        
        # Find the change in position
        move_speed = new_course.magnitude if new_course.magnitude < self.speedg.val.magnitude else self.speedg.val.magnitude
        pos_diff = Vector.fromPolar(PolarVector(self.heading, move_speed))
        
        # Now change tho position
        self.position += pos_diff
        self.energy -= BASE_MOVE_ENRGY*(move_speed/BASE_MOVE_SPEED)
        
        return self.position, PolarVector(self.heading, move_speed)
    
    def eat(self, target: Food):
        target.eaten = True
        self.energy += target.energy
    
    def calculate_turn(self, food_options: List[Food], field_space: Tuple[Vector, Vector]):
        #print("Job: ", end='')
        if (not self.task_finished) and self.energy > 0:
            # Need to get food and go home
            if not self.got_food:
         #       print('Getting Food')
        #        print(f'Energy: {self.energy}')
                # Need to get food
                # Find closest food
                closest = food_options[0]
                cdist = dist(self.position, closest.position)
                for food in food_options[1:]:
                    new_dist = dist(self.position, food.position)
                    if new_dist < cdist:
                        closest = food
                        cdist = new_dist
                # Go get food
       #         print(f'Closest: {closest.position}, Dist: {cdist}')
      #          print(f'X: {self.position.x}\nY: {self.position.y}')
                self.move(closest.position)
     #           print(f'nX: {self.position.x}\nnY: {self.position.y}')
                # Eat that food
                if dist(self.position, food.position) < self.sizeg.val*2:
                    self.eat(closest)
            else:
    #            print('Going Home')
                # Need to get to the wall
                
                # find the closest wall
                wall_dists = {
                    1: abs(field_space[1].y - self.position.y),
                    2: abs(field_space[1].x - self.position.x),
                    3: abs(self.position.y - field_space[0].y),
                    4: abs(self.position.x - field_space[0].x)
                }
                closest_wall = min(wall_dists, key=lambda x: wall_dists[x])
                
                # Move to wall
                if closest_wall == 1:
                    self.move(Vector(self.position.x, field_space[1].y))
                elif closest_wall == 2:
                    self.move(Vector(field_space[1].x, self.position.y))
                elif closest_wall == 3:
                    self.move(Vector(self.position.x, field_space[0].y))
                elif closest_wall == 4:
                    self.move(Vector(field_space[0].x, self.position.y))

                wall_dists = [
                    abs(field_space[1].y - self.position.y),
                    abs(field_space[1].x - self.position.x),
                    abs(self.position.y - field_space[0].y),
                    abs(self.position.x - field_space[0].x)
                ]
                if any(map(lambda x: x < self.sizeg.val)):
                    self.finished_task = True
       # else:
   #         print('None')
        if self.position.x < field_space[0].x:
            self.position = Vector(field_space[0].x, self.position.y)
        if self.position.x > field_space[1].x:
            self.position = Vector(field_space[1].x, self.position.y)
        if self.position.y < field_space[0].y:
            self.position = Vector(self.position.x, field_space[0].y)
        if self.position.y > field_space[1].y:
            self.position = Vector(self.position.x, field_space[1].y)

                    
class Food:
    def __init__(self, position: Vector, angle: RadianAngle):
        self.eaten = False
        self.energy = 100
        self.position = position
        self.angle = angle
        

def randvector(start, end):
    X = uniform(start.x, end.x)
    Y = uniform(start.y, end.y)
    return Vector(X, Y)

def generate_food_list(field_space, food_amount):
    x_space = abs(field_space[1].x - field_space[0].x)
    y_space = abs(field_space[1].y - field_space[0].y)
    
    spawn_space = [Vector(field_space[0].x + 0.1*x_space, field_space[0].y + 0.1*y_space),
                   Vector(field_space[1].x - 0.1*x_space, field_space[1].y - 0.1*y_space)]
    
    foods = [Food(randvector(spawn_space[0], spawn_space[1]), uniform(0, 2*math.pi)) for i in range(food_amount)]
    return foods
    
def main():
    field_space = [Vector(0,0), Vector(200, 200)]
