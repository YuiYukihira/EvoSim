#!/usr/bin/env python

from __future__ import annotations
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from MapUtils import Vector, RadianAngle
from typing import Tuple, List
from math import degrees as to_degrees
from math import cos, sin, pi
from random import randint
from Creature import Food
import numpy as np

class Graphics:
    def __init__(self, field_space: Tuple[Vector, Vector], display_size: Vector):
        self.SCALING = Vector(10/abs(field_space[1].x - field_space[0].x),
                              10/abs(field_space[1].y - field_space[0].y))
        self.field_space = field_space
        
        self.c_velocity = RadianAngle(0)
        self.c_pos = 0
        
        pygame.init()
        pygame.display.set_mode(
            (int(display_size.x), int(display_size.y)),
            DOUBLEBUF|OPENGL)
        gluPerspective(45, (display_size.x/display_size.y), 0.1, 50.0)
        glTranslatef(0.0,0.0,-15)
        glRotatef(25, 2, 1, 0)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        
        
    def scale_vector(self, vector: Vector) -> Vector:
        new_x = -5 + (((vector.x-self.field_space[0].x)
                       /(self.field_space[1].x-self.field_space[0].x)*10))
        new_y = -5 + (((vector.y-self.field_space[0].y)
                       /(self.field_space[1].y-self.field_space[0].y)*10))
        return Vector(new_x, new_y)
    
    def draw_food(self, food: Food):
        glPushMatrix()
        
        pos = self.scale_vector(food.position)
        # Angle for food is random
        angle = food.angle + self.c_pos
        
        rotate_matrix = np.array([
            [cos(angle), 0, -sin(angle), 0],
            [         0, 1,           0, 0],
            [sin(angle), 0,  cos(angle), 0],
            [         0, 0,           0, 1]
        ])
        translate_matrix = np.array([
            [1, 0, 0, pos.x],
            [0, 1, 0,     0],
            [0, 0, 1, pos.y],
            [0, 0, 0,     1]
        ])
        
        tm = np.dot(
            rotate_matrix,
            translate_matrix)
        
        # Get position and draw the food
        glBegin(GL_QUADS)
        pos = self.scale_vector(food.position)
        #vertices = (
        #    (-0.1 + pos.x, .2  -0.1 + pos.y),
        #    ( 0.1 + pos.x, .2, -0.1 + pos.y),
        #    ( 0.1 + pos.x, .2,  0.1 + pos.y),
        #    (-0.1 + pos.x, .2,  0.1 + pos.y),

        #    (-0.1 + pos.x,  0, -0.1 + pos.y),
        #    ( 0.1 + pos.x,  0, -0.1 + pos.y),
        #    ( 0.1 + pos.x,  0,  0.1 + pos.y),
        #    (-0.1 + pos.x,  0,  0.1 + pos.y),
        #)
        vertices = (
            tuple(np.dot(tm, np.array([-0.1, .2, -0.1, 1]))[:3]),
            tuple(np.dot(tm, np.array([ 0.1, .2, -0.1, 1]))[:3]),
            tuple(np.dot(tm, np.array([ 0.1, .2,  0.1, 1]))[:3]),
            tuple(np.dot(tm, np.array([-0.1, .2,  0.1, 1]))[:3]),

            tuple(np.dot(tm, np.array([-0.1, 0, -0.1, 1]))[:3]),
            tuple(np.dot(tm, np.array([ 0.1, 0, -0.1, 1]))[:3]),
            tuple(np.dot(tm, np.array([ 0.1, 0,  0.1, 1]))[:3]),
            tuple(np.dot(tm, np.array([-0.1, 0,  0.1, 1]))[:3]),
        )
        #vertices = (
        #    (-0.1 , .2, -0.1 ),
        #    ( 0.1 , .2, -0.1 ),
        #    ( 0.1 , .2,  0.1 ),
        #    (-0.1 , .2,  0.1 ),

        #    (-0.1 ,  0, -0.1 ),
        #    ( 0.1 ,  0, -0.1 ),
        #    ( 0.1 ,  0,  0.1 ),
        #    (-0.1 ,  0,  0.1 ),
        #)
        surfaces = (
            (0,1,2,3),
            (0,1,5,4),
            (3,0,4,7),
            (2,3,7,6),
            (1,2,6,5)
        )
        colors = (
            (1,0,0),
            (1,0,0),
            (1,0,0),
            (1,0,0),
            (1,0,0),
            (1,0,0),
            (1,0,0),
            (1,0,0),
        )
        for surface in surfaces:
            for vertex in surface:
                glColor3fv(colors[vertex])
                glVertex3fv(vertices[vertex])
        glEnd()
        glPopMatrix()
    def draw_creature(self, creature: Creature):
        pos = self.scale_vector(creature.position)
        glPushMatrix()
        
        # Get rotation of the creature
        cangle = creature.heading #+ self.c_pos
        rotate_matrix_c = np.array([
            [cos(cangle), 0, -sin(cangle), 0],
            [         0, 1,           0, 0],
            [sin(cangle), 0,  cos(cangle), 0],
            [         0, 0,           0, 1]
        ])
        wangle = self.c_pos
        rotate_matrix_f = np.array([
            [cos(wangle), 0, -sin(wangle), 0],
            [         0, 1,           0, 0],
            [sin(wangle), 0,  cos(wangle), 0],
            [         0, 0,           0, 1]
        ])
        translate_matrix = np.array([
            [1, 0, 0, pos.x],
            [0, 1, 0,     0],
            [0, 0, 1, pos.y],
            [0, 0, 0,     1]
        ])
        
        tm = np.dot(np.dot(
            rotate_matrix_f,
            translate_matrix),
            rotate_matrix_c)
        
        # Get position and draw the cube
        glBegin(GL_QUADS)
        vertices = (
            (-0.2, .4, -0.2, 1),
            ( 0.2, .4, -0.2, 1),
            ( 0.2, .4,  0.2, 1),
            (-0.2, .4,  0.2, 1),

            (-0.2,  0, -0.2, 1),
            ( 0.2,  0, -0.2, 1),
            ( 0.2,  0,  0.2, 1),
            (-0.2,  0,  0.2, 1),
        )
        vertices = tuple(tuple(np.dot(tm, np.array(i))[:3]) for i in vertices)
        surfaces = (
            (0,1,2,3),
            (0,1,5,4),
            (3,0,4,7),
            (2,3,7,6),
            (1,2,6,5)
        )
        colors = (
            (0,1,0),
            (0,1,0),
            (0,1,0),
            (0,1,0),
            (0,1,0),
            (0,1,0),
            (0,1,0),
            (0,1,0),
        )
        for surface in surfaces:
            for vertex in surface:
                glColor3fv(colors[vertex])
                glVertex3fv(vertices[vertex])
        glEnd()
        glPopMatrix()
        
    def draw_field(self):
        glPushMatrix()
        
        tm = np.array([
            [cos(self.c_pos), 0, -sin(self.c_pos), 0],
            [              0, 1,                0, 0],
            [sin(self.c_pos), 0,  cos(self.c_pos), 0],
            [              0, 0,                0, 1]
        ])
        glBegin(GL_QUADS)
        vertices = (
            tuple(np.dot(tm, np.array((-5,0,-5, 1)))[:3]),
            tuple(np.dot(tm, np.array(( 5,0,-5, 1)))[:3]),
            tuple(np.dot(tm, np.array(( 5,0, 5, 1)))[:3]),
            tuple(np.dot(tm, np.array((-5,0, 5, 1)))[:3]),
            
            tuple(np.dot(tm, np.array((-5,-5,-5, 1)))[:3]),
            tuple(np.dot(tm, np.array(( 5,-5,-5, 1)))[:3]),
            tuple(np.dot(tm, np.array(( 5,-5, 5, 1)))[:3]),
            tuple(np.dot(tm, np.array((-5,-5, 5, 1)))[:3])
        )
        surfaces = (
            (0,1,2,3),
            (0,1,5,4),
            (3,0,4,7),
            (2,3,7,6),
            (1,2,6,5)
        )
        colors = (
            (1,1,1),
            (1,1,1),
            (1,1,1),
            (1,1,1),
            
            (0,0,0),
            (0,0,0),
            (0,0,0),
            (0,0,0),
        )
        for surface in surfaces:
            for vertex in surface:
                glColor3fv(colors[vertex])
                glVertex3fv(vertices[vertex])
        glEnd()
        glPopMatrix()
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.c_velocity = 0.025
                elif event.key == pygame.K_RIGHT:
                    self.c_velocity = -0.025
                
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.c_velocity = 0
                elif event.key == pygame.K_RIGHT:
                    self.c_velocity = 0

        
    def draw(self, creatures: List[Creature], foods: List[Food]):
        self.handle_events()
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        self.c_pos = (self.c_pos + self.c_velocity) % (2*pi)
        for creature in creatures:
            self.draw_creature(creature)
        for food in foods:
            self.draw_food(food)
        self.draw_field()
        pygame.display.flip()
        pygame.time.wait(10)
        
class DummyCreature:
    def __init__(self, pos: Vector, heading: RadianAngle):
        self.position = pos
        self.heading = heading

if __name__ == '__main__':
    g = Graphics((Vector(-200,-200), Vector(200,200)), Vector(1920,1080))
    food = [Food(i, RadianAngle(0)) for i in [Vector(-200,-200), Vector(-200,200), Vector(200,-200), Vector(200,200)]]
    bounce = True
    creature = DummyCreature(Vector(0,0), RadianAngle(0))
    spin = RadianAngle(0)
    while True:
        print(f'Pos:    {creature.position}')
        print(f'Bounce: {bounce}')
        print(f'Spin:   {spin}')
        
        spin = (spin + RadianAngle(0.01)) % (2*pi)
        creature.heading = spin
        if creature.position.x >= 100:
            bounce = False
            creature.position = Vector(99,0)
        elif creature.position.x <= -100:
            bounce = True
            creature.position = Vector(-99,0)
            
        if bounce:
            creature.position = creature.position + Vector(5,0)
        else:
            creature.position = creature.position - Vector(5,0)
        g.draw([creature], food)
