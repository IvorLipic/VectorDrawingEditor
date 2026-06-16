from shapes.abstract_graphical_object import AbstractGraphicalObject
from geometry import Point, Rectangle
from interfaces.interfaces import GraphicalObject, Renderer, GraphicalObjectListener

class CompositeShape(AbstractGraphicalObject):
    class _ChildGraphicalObjectListener(GraphicalObjectListener):
        def __init__(self, composite_instance):
            self._composite = composite_instance
        def graphicalObjectChanged(self, go: GraphicalObject):
            self._composite.notifyListeners()
        def graphicalObjectSelectionChanged(self, go: GraphicalObject):
            self._composite.notifyListeners()
    
    def __init__(self, children: list[GraphicalObject] = None):
        super().__init__([])
        if children:
            self._children = children
            self._child_listener = self._ChildGraphicalObjectListener(self)
            for child in self._children:
                child.addGraphicalObjectListener(self._child_listener)

    def getBoundingBox(self) -> Rectangle:
        if not self._children:
            return Rectangle(0, 0, 0, 0)

        first_bbox = self._children[0].getBoundingBox()
        min_x = first_bbox.x
        min_y = first_bbox.y
        max_x = first_bbox.x + first_bbox.width
        max_y = first_bbox.y + first_bbox.height

        for i in range(1, len(self._children)):
            child_bbox = self._children[i].getBoundingBox()
            min_x = min(min_x, child_bbox.x)
            min_y = min(min_y, child_bbox.y)
            max_x = max(max_x, child_bbox.x + child_bbox.width)
            max_y = max(max_y, child_bbox.y + child_bbox.height)

        return Rectangle(min_x, min_y, max_x - min_x, max_y - min_y)

    def selectionDistance(self, mousePoint: Point) -> float:
        min_dist = float('inf')
        for child in self._children:
            dist = child.selectionDistance(mousePoint)
            if dist < min_dist:
                min_dist = dist
        return min_dist

    def translate(self, delta: Point):
        for child in self._children:
            child.translate(delta)

    def render(self, r: Renderer):
        for child in self._children:
            child.render(r)

    def getShapeName(self) -> str:
        return "Group"

    def duplicate(self) -> 'GraphicalObject':
        duplicated_children = [child.duplicate() for child in self._children]
        return CompositeShape(duplicated_children)
    
    def save(self, rows: list[str]):
        rows.append(f"{self.getShapeID()} {len(self._children)}")
    
    def getChildren(self) -> list[GraphicalObject]:
        return self._children

    def getShapeID(self) -> str:
        return "@COMP"

    def save(self, rows: list[str]):
        for child in self._children:
            child.save(rows)
        rows.append(f"{self.getShapeID()} {len(self._children)}")
    
    def load(self, stack: list[GraphicalObject], data: str):
        try:
            num_children = int(data.strip())
            popped_children = []
            for _ in range(num_children):
                if stack:
                    popped_children.append(stack.pop())
                else:
                    print(f"Error: Not enough objects on stack to form composite. Expected {num_children}, but stack is empty.")
                    return
            popped_children.reverse() 
            
            new_composite = CompositeShape(popped_children)
            stack.append(new_composite)

        except ValueError:
            print(f"Error parsing CompositeShape data (expected integer for child count): {data}")
        except Exception as e:
            print(f"An unexpected error occurred during CompositeShape loading: {e}")