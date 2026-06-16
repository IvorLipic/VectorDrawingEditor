from shapes.abstract_graphical_object import AbstractGraphicalObject
from geometry import Point, Rectangle, GeometryUtil
from interfaces.interfaces import Renderer, GraphicalObject

class LineSegment(AbstractGraphicalObject):
    def __init__(self, p1=None, p2=None):
        if p1 is None:
            p1 = Point(0, 0)
        if p2 is None:
            p2 = Point(10, 0)
        super().__init__([p1, p2])

    def getBoundingBox(self):
        p1 = self.getHotPoint(0)
        p2 = self.getHotPoint(1)
        min_x = min(p1.x, p2.x)
        max_x = max(p1.x, p2.x)
        min_y = min(p1.y, p2.y)
        max_y = max(p1.y, p2.y)
        return Rectangle(min_x, min_y, max_x - min_x, max_y - min_y)

    def selectionDistance(self, mousePoint):
        p1 = self.getHotPoint(0)
        p2 = self.getHotPoint(1)
        return GeometryUtil.distanceFromLineSegment(p1, p2, mousePoint)

    def getShapeName(self):
        return "Linija"

    def duplicate(self):
        p1 = self.getHotPoint(0)
        p2 = self.getHotPoint(1)
        new_segment = LineSegment(p1, p2)
        return new_segment
    
    def render(self, r: Renderer):
        p1 = self.getHotPoint(0)
        p2 = self.getHotPoint(1)
        r.drawLine(p1, p2)
    
    def getSegment(self) -> tuple[Point, Point]:
        return self.getHotPoint(0), self.getHotPoint(1)
    
    def getShapeID(self) -> str:
        return "@LINE"

    def save(self, rows: list[str]):
        p1 = self.getHotPoint(0)
        p2 = self.getHotPoint(1)
        rows.append(f"{self.getShapeID()} {p1.x} {p1.y} {p2.x} {p2.y}")

    def load(self, stack: list[GraphicalObject], data: str):
        parts = data.split()
        if len(parts) == 4:
            try:
                x1, y1, x2, y2 = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
                new_line = LineSegment(Point(x1, y1), Point(x2, y2))
                stack.append(new_line)
            except ValueError:
                print(f"Error parsing LineSegment data: {data}")
        else:
            print(f"Invalid LineSegment data format: {data}")