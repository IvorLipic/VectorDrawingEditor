from interfaces.interfaces import GraphicalObject
from geometry import GeometryUtil, Point 

class AbstractGraphicalObject(GraphicalObject):
    def __init__(self, hot_points: list[Point]):
        self._hot_points = list(hot_points)
        self._hot_point_selected = [False] * len(hot_points)
        self._selected = False
        self._listeners = []

    def isSelected(self):
        return self._selected

    def setSelected(self, selected):
        if self._selected != selected:
            self._selected = selected
            self.notifySelectionListeners()

    def getNumberOfHotPoints(self):
        return len(self._hot_points)

    def getHotPoint(self, index):
        if not (0 <= index < len(self._hot_points)):
            raise IndexError("Hot point index out of bounds")
        return self._hot_points[index]

    def setHotPoint(self, index, point):
        if not (0 <= index < len(self._hot_points)):
            raise IndexError("Hot point index out of bounds")
        if self._hot_points[index] != point:
            self._hot_points[index] = point
            self.notifyListeners()

    def isHotPointSelected(self, index):
        if not (0 <= index < len(self._hot_point_selected)):
            raise IndexError("Hot point index out of bounds")
        return self._hot_point_selected[index]

    def setHotPointSelected(self, index, selected):
        if not (0 <= index < len(self._hot_point_selected)):
            raise IndexError("Hot point index out of bounds")
        if self._hot_point_selected[index] != selected:
            self._hot_point_selected[index] = selected
            self.notifyListeners()

    def getHotPointDistance(self, index, mousePoint):
        if not (0 <= index < len(self._hot_points)):
            raise IndexError("Hot point index out of bounds")
        return GeometryUtil.distanceFromPoint(self._hot_points[index], mousePoint)

    def translate(self, delta):
        for i in range(len(self._hot_points)):
            self._hot_points[i] = self._hot_points[i].translate(delta)
        self.notifyListeners()

    def addGraphicalObjectListener(self, l):
        if l not in self._listeners:
            self._listeners.append(l)

    def removeGraphicalObjectListener(self, l):
        if l in self._listeners:
            self._listeners.remove(l)

    def notifyListeners(self):
        for l in self._listeners:
            l.graphicalObjectChanged(self)

    def notifySelectionListeners(self):
        for l in self._listeners:
            l.graphicalObjectSelectionChanged(self)

    # Abstract methods to be implemented by concrete classes
    def getBoundingBox(self):
        raise NotImplementedError

    def selectionDistance(self, mousePoint):
        raise NotImplementedError

    def getShapeName(self):
        raise NotImplementedError

    def duplicate(self):
        raise NotImplementedError
    
    def getShapeID(self) -> str:
        raise NotImplementedError
    
    def save(self, rows: list[str]):
        raise NotImplementedError
    
    def load(self, stack: list['GraphicalObject'], data: str):
        raise NotImplementedError