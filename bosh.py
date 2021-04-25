from hxlr import *

class Rider(hxlr_rider_RiderBase):
    def __init__(self, _struct, _start, _name):
        super().__init__(_struct, _start, _name)
    
    def step(self):
        self.iterate()
        for i in range(6):
            self.constrain()
            self.collide()
        
        self.checkLimits()
    
    def checkLimits(self):
        for _def in self.limits:
            x_distA = self.contactPoints[_def.point_a].pos.x - self.contactPoints[_def.point_b].pos.x
            y_distA = self.contactPoints[_def.point_a].pos.y - self.contactPoints[_def.point_b].pos.y
            x_distB = self.contactPoints[_def.point_c].pos.x - self.contactPoints[_def.point_d].pos.x
            y_distB = self.contactPoints[_def.point_c].pos.y - self.contactPoints[_def.point_d].pos.y
            
            if _def.lessThan:
                if (x_distA * y_distB - y_distA * x_distB < _def.threshold): self.crashed = True
            else:
                if (x_distA * y_distB - y_distA * x_distB > _def.threshold): self.crashed = True
    
    def iterate(self):
        for point in self.contactPoints:
            point.iterate(self.gravity)
        
        for point in self.airPoints:
            point.iterate(self.gravity)
    
    def constrain(self):
        for edge in self.constraints:
            edge.satisfy(self.crashed)
    
    def reset(self):
        self.init()