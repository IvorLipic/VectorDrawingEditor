from interfaces.interfaces import State, GraphicalObject, Renderer
from geometry import Point
from document_model.document_model import DocumentModel

class AddShapeState(State):
    def __init__(self, model: DocumentModel, prototype: GraphicalObject):
        self.model = model
        self.prototype = prototype
        print(f"Entering AddShapeState for: {prototype.getShapeName()}")

    @property
    def get_model(self):
        return self.model

    @property
    def get_prototype(self):
        return self.prototype

    def mouseDown(self, mousePoint: Point, shiftDown: bool, ctrlDown: bool):
        new_object = self.prototype.duplicate()
        new_object.translate(mousePoint)

        self.model.addGraphicalObject(new_object)

        print(f"Added {new_object.getShapeName()} at {mousePoint}")

    def mouseUp(self, mousePoint: Point, shiftDown: bool, ctrlDown: bool):
        pass

    def mouseDragged(self, mousePoint: Point):
        pass

    def keyPressed(self, keyCode: int):
        pass

    def afterDraw(self, r: Renderer, go: GraphicalObject):
        pass

    def afterDrawAll(self, r: Renderer):
        pass

    def onLeaving(self):
        print(f"Leaving AddShapeState for: {self.prototype.getShapeName()}")
        pass