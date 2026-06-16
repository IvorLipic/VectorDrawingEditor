from shapes.abstract_graphical_object import AbstractGraphicalObject
from geometry import Point, Rectangle, GeometryUtil
from interfaces.interfaces import Renderer, GraphicalObject
import math

class Oval(AbstractGraphicalObject):
    def __init__(self, p_right=None, p_bottom=None):
        if p_right is None:
            p_right = Point(20, 5)
        if p_bottom is None:
            p_bottom = Point(10, 10)
        super().__init__([p_right, p_bottom])

    def getBoundingBox(self):
        p_right = self.getHotPoint(0)
        p_bottom = self.getHotPoint(1)

        center_x = p_bottom.x
        center_y = p_right.y

        radius_x = abs(p_right.x - center_x)
        radius_y = abs(p_bottom.y - center_y)

        min_x = center_x - radius_x
        min_y = center_y - radius_y
        max_x = center_x + radius_x
        max_y = center_y + radius_y

        width = max(1, max_x - min_x)
        height = max(1, max_y - min_y)

        return Rectangle(min_x, min_y, width, height)

    def selectionDistance(self, mousePoint):
        bbox = self.getBoundingBox()

        # Check if point is inside the bounding box
        if bbox.x <= mousePoint.x <= (bbox.x + bbox.width) and \
           bbox.y <= mousePoint.y <= (bbox.y + bbox.height):
            return 0.0
        
        # If not inside, calculate distance to the bounding box edges
        closest_x = max(bbox.x, min(mousePoint.x, bbox.x + bbox.width))
        closest_y = max(bbox.y, min(mousePoint.y, bbox.y + bbox.height))
        
        return GeometryUtil.distanceFromPoint(mousePoint, Point(closest_x, closest_y))

    def getShapeName(self):
        return "Oval"

    def duplicate(self):
        p_right = self.getHotPoint(0)
        p_bottom = self.getHotPoint(1)
        new_oval = Oval(p_right.translate(Point(0,0)), p_bottom.translate(Point(0,0)))
        return new_oval
    
    def render(self, r: Renderer):
        bbox = self.getBoundingBox()
        center_x = bbox.x + bbox.width / 2
        center_y = bbox.y + bbox.height / 2
        
        radius_x = bbox.width / 2
        radius_y = bbox.height / 2

        num_segments = 60 # Number of line segments to approximate the ellipse
        points = []
        for i in range(num_segments):
            angle = 2 * math.pi * i / num_segments
            x = center_x + radius_x * math.cos(angle)
            y = center_y + radius_y * math.sin(angle)
            points.append(Point(round(x), round(y)))

        r.fillPolygon(points)

    def getShapeID(self) -> str:
        return "@OVAL"

    def save(self, rows: list[str]):
        p_right = self.getHotPoint(0)
        p_bottom = self.getHotPoint(1)
        rows.append(f"{self.getShapeID()} {p_right.x} {p_right.y} {p_bottom.x} {p_bottom.y}")
    
    def load(self, stack: list[GraphicalObject], data: str):
        parts = data.split()
        if len(parts) == 4:
            try:
                x_right, y_right, x_bottom, y_bottom = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
                new_oval = Oval(Point(x_right, y_right), Point(x_bottom, y_bottom))
                stack.append(new_oval)
            except ValueError:
                print(f"Error parsing Oval data: {data}")
        else:
            print(f"Invalid Oval data format: {data}")