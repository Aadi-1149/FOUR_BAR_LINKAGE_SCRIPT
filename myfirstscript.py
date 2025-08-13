import FreeCAD as App, Part
import math






import sys
import FreeCAD as App, Part
import math

if len(sys.argv) != 6:
    print("Usage: myfirstscript.py a b c d output_path")
    sys.exit(1)

# Parse command-line args
linkList = [float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])]
output_path = sys.argv[5]



#linkList = [600,200,700,900]

for i in range(4):
    if linkList[i]<=linkList[0]:
        minindex = i

newlinkList = []
for i in range(4):
    newlinkList.append(linkList[(minindex + i)%4])
        

#print(newlinkList)
a = newlinkList[0]
b = newlinkList[1]
c = newlinkList[2]
d = newlinkList[3]

alpha  = math.acos(((a+b)**2 + c**2 - d**2)/(2*(a+b)*c))
#print(alpha)

beta = math.asin(c*math.sin(alpha)/d)
#print(beta)

thickness = a/8
hole_size = a/32
height = a/16


class SlotLink:
    def __init__(self, p1, p2, thickness, arc_radius):
        
       
        self.p1 = App.Vector(p1) if not isinstance(p1, App.Vector) else p1
        self.p2 = App.Vector(p2) if not isinstance(p2, App.Vector) else p2
        self.thickness = thickness
        self.arc_radius = arc_radius
        self.slot_shape = None
        self.slot_extrusion = None
        self.holes = [(self.p1, hole_size), (self.p2, hole_size)]
        self._make_slot()

    def _make_slot(self):
        
        direction = self.p2.sub(self.p1)
        length = direction.Length
        dir_unit = direction.normalize()

        # Perpendicular vector for thickness
        perp = App.Vector(-dir_unit.y, dir_unit.x, 0) * (self.thickness / 2)

        # Four corner points
        p1_left = self.p1 + perp
        p1_right = self.p1 - perp
        p2_left = self.p2 + perp
        p2_right = self.p2 - perp

        # Lines and arcs
        line1 = Part.LineSegment(p1_left, p2_left).toShape()
        line2 = Part.LineSegment(p2_right, p1_right).toShape()

        arc1 = Part.Arc(p2_left, self.p2 + dir_unit * self.arc_radius, p2_right).toShape()
        arc2 = Part.Arc(p1_right, self.p1 - dir_unit * self.arc_radius, p1_left).toShape()
        
        outer_wire = Part.Wire([line1, arc1, line2, arc2])

 
        
        hole_wires = []
        for hole_center, hole_radius in self.holes:  
            circ_edge = Part.Circle(hole_center, App.Vector(0, 0, 1), hole_radius).toShape()
            hole_wire = Part.Wire([circ_edge])
            hole_wires.append(hole_wire)
            
         # Combine into wire
     
        
        self.slot_shape = Part.Face([outer_wire] + hole_wires)
      
        

    def extrude(self, height,offset_z):
        """Extrude the slot to a solid link"""
        
        
        if self.slot_shape:
            offset_shape = self.slot_shape.translate(App.Vector(0, 0, offset_z))
            
            self.slot_extrusion = self.slot_shape.extrude(App.Vector(0, 0, height))
            extrusion_obj = App.ActiveDocument.addObject("Part::Feature", "SlotLink_Extrude")
            extrusion_obj.Shape = self.slot_extrusion
            #return extrusion_obj
        return None
        
            

        
pinlength = [4,2,2,2]
pinoffset = [0,0,1,2]
def create_joints(doc, holes):
    i = 0
    for center in holes:
        
        joint = doc.addObject("Part::Cylinder", "Joint")
        joint.Radius = hole_size
        joint.Height = height*pinlength[i]  # extend through thickness
        joint.Placement.Base = App.Vector(center.x, center.y, height*(pinoffset[i]))  # centered through part
        i = i+1
        
doc = App.newDocument()

#App.Gui.runCommand('Std_DrawStyle',6)  #shaded wireframe



#Define Points
point1 = App.Vector(0,0,0)
point2 = App.Vector(a,0,0)
point3 = App.Vector(a+b,0,0)

#defining Point 4
dx = c * math.cos(alpha)
dy = c * math.sin(alpha)
point4 = App.Vector(point3.x - dx, point3.y + dy, point3.z)


holes = [point1,point2,point3,point4]


slot1 = SlotLink(point1, point2, thickness, thickness/2)
slot1._make_slot()
slot1obj = slot1.extrude(height, 0)


slot2 = SlotLink(point2, point3, thickness, thickness/2)
slot2._make_slot()
slot2obj = slot2.extrude(height, height)

slot3 = SlotLink(point3, point4, thickness, thickness/2)
slot3._make_slot()
slot3obj = slot3.extrude(height, height*2)

slot4 = SlotLink(point4, point1, thickness, thickness/2)
slot4._make_slot()
slot4obj = slot4.extrude(height, height*3)


create_joints(doc,holes)



doc.recompute()


#App.Gui.SendMsgToActiveView("ViewFit")

part_objs = [obj for obj in doc.Objects if obj.TypeId.startswith("Part::")]
Part.export(part_objs, output_path)
print(f"CAD file generated: {output_path}")
