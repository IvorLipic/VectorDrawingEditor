from geometry import Point
from interfaces.interfaces import GraphicalObject, Renderer, State

class IdleState(State):
    """
    IdleState: All methods are empty.
    """
    def __init__(self):
        print("Entering IdleState.")

    def mouseDown(self, mousePoint: Point, shiftDown: bool, ctrlDown: bool):
        pass

    def mouseUp(self, mousePoint: Point, shiftDown: bool, ctrlDown: bool):
        pass

    def mouseDragged(self, mousePoint: Point):
        pass

    def keyPressed(self, keyCode: int):
        print("Key pressed")
        pass

    def afterDraw(self, r: Renderer, go: GraphicalObject):
        pass

    def afterDrawAll(self, r: Renderer):
        pass

    def onLeaving(self):
        print("Leaving IdleState.")
        pass