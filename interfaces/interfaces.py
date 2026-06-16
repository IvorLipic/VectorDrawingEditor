from geometry import Point

class GraphicalObject:
    def isSelected(self):
        raise NotImplementedError

    def setSelected(self, selected):
        raise NotImplementedError

    def getNumberOfHotPoints(self):
        raise NotImplementedError

    def getHotPoint(self, index):
        raise NotImplementedError

    def setHotPoint(self, index, point):
        raise NotImplementedError

    def isHotPointSelected(self, index):
        raise NotImplementedError

    def setHotPointSelected(self, index, selected):
        raise NotImplementedError

    def getHotPointDistance(self, index, mousePoint):
        raise NotImplementedError

    def translate(self, delta):
        raise NotImplementedError

    def getBoundingBox(self):
        raise NotImplementedError

    def selectionDistance(self, mousePoint):
        raise NotImplementedError

    def addGraphicalObjectListener(self, l):
        raise NotImplementedError

    def removeGraphicalObjectListener(self, l):
        raise NotImplementedError

    def getShapeName(self):
        raise NotImplementedError

    def duplicate(self):
        raise NotImplementedError
    
    def render(self, r):
        raise NotImplementedError
    
    def getShapeID(self) -> str: 
        raise NotImplementedError

    def save(self, rows: list[str]):
        raise NotImplementedError
    
    def load(self, stack: list['GraphicalObject'], data: str): 
        raise NotImplementedError


class GraphicalObjectListener:
    def graphicalObjectChanged(self, go):
        raise NotImplementedError

    def graphicalObjectSelectionChanged(self, go):
        raise NotImplementedError


class Renderer:
    def drawLine(self, s, e):
        raise NotImplementedError

    def fillPolygon(self, points):
        raise NotImplementedError
    
class State:
    def mouseDown(self, mousePoint: Point, shiftDown: bool, ctrlDown: bool):
        raise NotImplementedError

    def mouseUp(self, mousePoint: Point, shiftDown: bool, ctrlDown: bool):
        raise NotImplementedError

    def mouseDragged(self, mousePoint: Point):
        raise NotImplementedError

    def keyPressed(self, keyCode: int):
        raise NotImplementedError

    def afterDraw(self, r: Renderer, go: GraphicalObject):
        raise NotImplementedError

    def afterDrawAll(self, r: Renderer): # Renamed to avoid confusion with go argument
        raise NotImplementedError

    def onLeaving(self):
        raise NotImplementedError