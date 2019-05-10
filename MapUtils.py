#!/usr/bin/env python

from __future__ import annotations
import math
from typing import Union, Tuple

NumericType = Union[float, int]
AngleType   = Union[float, int, 'RadianAngle']
VectorType  = Union['Vector', 'PolarVector']

class Vector(tuple):
    def __new__(cls, x: float, y: float):
        if type(x) == int:
             x = float(x)
        if type(x) in (float, property):
             if type(y) == int:
                 y = float(y)
             if type(y) in (float, property):
                 return tuple.__new__(cls, (x, y))
             raise TypeError(f"y has incorrect type of: {type(y)}")
        raise TypeError(f"x has incorrect type of {type(x)}")
        
    
    @property
    def x(self):
        return tuple.__getitem__(self, 0)
    
    @property
    def y(self):
        return tuple.__getitem__(self, 1)
    
    def __getitem__(self, item):
        raise TypeError
        
    def __add__(self, other: Union[NumericType, VectorType]) -> Vector:
        if type(other) in [int, float]:
            return Vector(self.x + other, self.y + other)
        elif isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
            
    def __radd__(self, other: Union[NumericType, VectorType]) -> Vector:
        if type(other) in [int, float]:
            return Vector(self.x + other, self.y + other)
        elif isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        
        
    def __sub__(self, other: Union[NumericType, VectorType]) -> Vector:
        if type(other) in [int, float]:
            return Vector(self.x - other, self.y - other)
        elif isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
            
    def __rsub__(self, other: Union[NumericType, VectorType]) -> Vector:
        if type(other) in [int, float]:
            return Vector(self.x - other, self.y - other)
        elif isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        
    def __truediv__(self, other: Numeric) -> Vector:
        if type(other) in [int, float]:
            return Vector(self.x/other, self.y/other)
        raise TypeError(f"unsupported operand types(s) for /: 'Vector' and '{type(other)}'")
    
    def __rtruediv__(self, other: Numeric) -> Vector:
        raise TypeError(f"unsupported operand types(s) for /: '{type(other)}' and 'Vector'")
    
    @classmethod
    def fromPolar(cls, vector):
        return Vector(vector.x, vector.y)
        
class RadianAngle(float):
    def __new__(cls, v0: NumericType) -> RadianAngle:
        if type(v0) is RadianAngle:
            return v0
        if type(v0) is int:
            v0 = float(v0)
        if not type(v0) is float:
            raise TypeError(f"Unexpected type for angle: {type(v0)}")
        return float.__new__(cls, v0)
        
    def __add__(self, other: AngleType) -> RadianAngle:
        return RadianAngle(self.real + other)
    
    def __radd__(self, other: AngleType) -> RadianAngle:
        return RadianAngle(self.real + other)
    
    def __mul__(self, other: AngleType) -> RadianAngle:
        return RadianAngle(self.real * other)

    def __rmul__(self, other: AngleType) -> RadianAngle:
        return RadianAngle(self.real * other)
    
    def __repr__(self) -> str:
        return str(self.real)
    
    def __lt__(self, other: AngleType) -> bool:
        return self.real < other
    
    def __rlt__(self, other: AngleType) -> bool:
        return other < self.real
    
    def __gt__(self, other: AngleType) -> bool:
        return self.real > other
    
    def __rgt__(self, other: AngleType) -> bool:
        return other > self.real
    
    @classmethod
    def from_degrees(cls, value: Union[int, float]) -> RadianAngle:
        return RadianAngle(math.radians(value))
    
class PolarVector(Vector):
    def __new__(cls, angle: AngleType, magnitude: int) -> PolarVector:
        if not type(angle) in [int, float, RadianAngle]:
            raise TypeError(f"Unexpected type for polar vector: {type(angle)}")
        elif type(angle) in [float, int]:
            angle = RadianAngle(angle % 2*math.pi)
        if magnitude < 0:
            raise ValueError(f"Passed value {magnitude} is not 0 or greater.")
        
        return Vector.__new__(cls,
            magnitude*math.cos(angle),
            magnitude*math.sin(angle))
        
    @property
    def angle(self) -> RadianAngle:
        return RadianAngle(math.atan2(self.y, self.x))
        
    @property
    def magnitude(self) -> float:
        return math.hypot(self.x, self.y)

    def __repr__(self) -> str:
        return f"Angle: {self.angle}, Magnitude: {self.magnitude}"
    
    @classmethod
    def fromVector(cls, vector: Vector) -> PolarVector:
        return PolarVector(RadianAngle(math.atan2(vector.y, vector.x)), math.hypot(vector.x, vector.y))

    
def dist(x: VectorType, y: VectorType) -> float:
    return math.hypot(x.x - y.x, x.y - y.y)

def intersectionq(line1: Tuple[VectorType, VectorType], line2: Tuple[VectorType, VectorType]) -> Vector:
    X1, X2 = line1[0].x, line1[1].x
    X3, X4 = line2[0].x, line2[1].x
    Y1, Y2 = line1[0].y, line1[1].y
    Y3, Y4 = line2[1].y, line2[1].y
    print(X1, X2, X3, X4)
    print(Y1, Y2, Y3, Y4)
    if max(X1, X2) < min(X3, X4):
        return 'a'
    A1 = (Y1-Y2)/(0.01 if (X1-X2) == 0 else (X1-X2))
    A2 = (Y3-Y4)/(0.01 if (X3-X4) == 0 else (X1-X2))
    b1 = Y1-A1*X1
    b2 = Y3-A2*X3
    
    if A1 == A2:
        return 'b'
    
    Xa = (b2 - b1) / (A1 - A2)
    Ya = A1 * Xa + b1
    if (Xa < max(min(X1,X2),min(X3,X4))) or (Xa > min(max(X1,X2),max(X3,X4))):
        return 'c'
    return Vector(Xa, Ya)
