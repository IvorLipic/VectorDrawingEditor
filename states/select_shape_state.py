from interfaces.interfaces import State, GraphicalObject, Renderer
from geometry import Point
from document_model.document_model import DocumentModel
from renderers.tkinter_renderer_impl import TkinterRendererImpl
from shapes.composite_shape import CompositeShape

class SelectShapeState(State):
    def __init__(self, model: DocumentModel):
        self.model = model
        self._last_mouse_point: Point | None = None
        self._selected_hot_point_index: int | None = None
        self._object_being_modified: GraphicalObject | None = None
        print("Entering SelectShapeState.")

    def mouseDown(self, mousePoint: Point, shiftDown: bool, ctrlDown: bool):
        self._last_mouse_point = mousePoint # Store for potential drag

        # 1. Check for hot-point selection for modification (if one object selected)
        selected_objects = self.model.getSelectedObjects()
        if len(selected_objects) == 1:
            obj = selected_objects[0]
            hot_point_idx = self.model.findSelectedHotPoint(obj, mousePoint)

            if hot_point_idx != -1:
                self._selected_hot_point_index = hot_point_idx
                self._object_being_modified = obj
                obj.setHotPointSelected(hot_point_idx, True)
                self.model.notifyListeners()
                return

        # 2. If no hot-point selected, proceed with shape selection
        # Clear any previously selected hot-points from potentially modified object
        if self._object_being_modified:
            for i in range(self._object_being_modified.getNumberOfHotPoints()):
                self._object_being_modified.setHotPointSelected(i, False)
            self._object_being_modified = None
            self._selected_hot_point_index = None

        selected_obj_candidate = self.model.findSelectedGraphicalObject(mousePoint)

        if selected_obj_candidate:
            if ctrlDown: # Add/remove from selection
                selected_obj_candidate.setSelected(not selected_obj_candidate.isSelected())
            else: # Select single object
                if not selected_obj_candidate.isSelected() or len(selected_objects) > 1:
                     # Iterate through current selected objects and deselect them
                    for obj in selected_objects:
                        if obj is not selected_obj_candidate:
                            obj.setSelected(False)
                    selected_obj_candidate.setSelected(True)

        else: # Clicked on empty space
            # Iterate through current selected objects and deselect them
            for obj in selected_objects:
                obj.setSelected(False)

        self.model.notifyListeners()

    def mouseUp(self, mousePoint: Point, shiftDown: bool, ctrlDown: bool):
        # Reset hot-point modification state
        if self._object_being_modified:
            for i in range(self._object_being_modified.getNumberOfHotPoints()):
                self._object_being_modified.setHotPointSelected(i, False)
            self.model.notifyListeners()

        self._selected_hot_point_index = None
        self._object_being_modified = None
        self._last_mouse_point = None

    def mouseDragged(self, mousePoint: Point):
        if not self._last_mouse_point:
            return # Should not happen if mouseDown was called, but safety check

        delta_x = mousePoint.x - self._last_mouse_point.x
        delta_y = mousePoint.y - self._last_mouse_point.y
        delta_point = Point(delta_x, delta_y)

        if self._object_being_modified and self._selected_hot_point_index is not None:
            # Modify the hot-point of the single selected object
            current_hot_point = self._object_being_modified.getHotPoint(self._selected_hot_point_index)
            new_hot_point = Point(current_hot_point.x + delta_x, current_hot_point.y + delta_y)
            self._object_being_modified.setHotPoint(self._selected_hot_point_index, new_hot_point)
            # No need to notify here, setHotPoint should notify its listeners if it changes.
        else:
            # Move all selected objects
            for obj in self.model.getSelectedObjects():
                obj.translate(delta_point)
            # No need to notify here, translate should notify its listeners if it changes.
            
        self._last_mouse_point = mousePoint # Update for next drag segment

    def keyPressed(self, keyCode: str):
        selected_objects = self.model.getSelectedObjects()
        if not selected_objects:
            return 

        if keyCode == "Up":
            delta = Point(0, -1)
        elif keyCode == "Down":
            delta = Point(0, 1)
        elif keyCode == "Left":
            delta = Point(-1, 0)
        elif keyCode == "Right":
            delta = Point(1, 0)
        else:
            delta = None

        if delta:
            for obj in selected_objects:
                obj.translate(delta)

        # Z-order keys
        elif keyCode == "plus":
            for obj in selected_objects:
                self.model.increaseZ(obj)
        elif keyCode == "minus":
            for obj in selected_objects:
                self.model.decreaseZ(obj)        
        # The model's increaseZ/decreaseZ will call notifyListeners()

        # Group functionality
        elif keyCode == "g" or keyCode == "G": # Group selected objects
            if len(selected_objects) > 0: # Only group if there's something to group
                # Create a new CompositeShape with the selected objects as children
                new_composite = CompositeShape(selected_objects)
                
                # Remove all selected objects from the model
                for obj in list(selected_objects): # Iterate over a copy to allow modification
                    obj.setSelected(False) # Deselect them first
                    self.model.removeGraphicalObject(obj)
                
                # Add the new composite to the model
                self.model.addGraphicalObject(new_composite)
                new_composite.setSelected(True) # Select the new composite
                self.model.notifyListeners() # Trigger redraw

        # Ungroup functionality
        elif keyCode == "u" or keyCode == "U": # Ungroup a selected CompositeShape
            if len(selected_objects) == 1: # Only ungroup if exactly one object is selected
                selected_obj = selected_objects[0]
                if isinstance(selected_obj, CompositeShape): # And if it's a CompositeShape
                    children = selected_obj.getChildren() # Get its children
                    
                    # Remove the composite from the model
                    selected_obj.setSelected(False) # Deselect it
                    self.model.removeGraphicalObject(selected_obj)
                    
                    # Add its children back to the model and select them
                    for child in children:
                        self.model.addGraphicalObject(child)
                        child.setSelected(True) # Select the children
                    
                    self.model.notifyListeners() # Trigger redraw


    def afterDraw(self, r: TkinterRendererImpl, go: GraphicalObject):
        # This method is called for EACH graphical object by the DrawingCanvas.
        # It's responsible for drawing selection decorations *if* the object is selected.

        if go.isSelected():
            r.draw_bounding_box(go.getBoundingBox())
            
            # If only one object is selected, draw its hot-points
            if len(self.model.getSelectedObjects()) == 1 and self.model.getSelectedObjects()[0] is go and \
               not isinstance(go, CompositeShape):
                for i in range(go.getNumberOfHotPoints()):
                    hot_point = go.getHotPoint(i)
                    # go.isHotPointSelected(i) to determine hot-point color
                    color = "blue" if go.isHotPointSelected(i) else "black"
                    r.draw_hot_point(hot_point, color=color)

    def afterDrawAll(self, r: Renderer):
        pass

    def onLeaving(self):
        print("Leaving SelectShapeState.")
        for obj in list(self.model.getSelectedObjects()):
            obj.setSelected(False)
            for i in range(obj.getNumberOfHotPoints()):
                obj.setHotPointSelected(i, False)