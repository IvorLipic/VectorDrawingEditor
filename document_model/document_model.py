from geometry import Point, Rectangle, GeometryUtil
from interfaces.interfaces import GraphicalObject, GraphicalObjectListener
from document_model.document_model_listener import DocumentModelListener
from typing import Union, List


class DocumentModel:
    SELECTION_PROXIMITY = 10.0

    def __init__(self):
        self._objects: list[GraphicalObject] = []
        self._listeners: list[DocumentModelListener] = []
        self._selected_objects: list[GraphicalObject] = []

        # Observer to be registered on all graphical objects
        self._go_listener = self._GraphicalObjectInternalListener(self)

    # Inner class/closure for GraphicalObjectListener to avoid strong reference cycle issues
    class _GraphicalObjectInternalListener(GraphicalObjectListener):
        class DocumentModel:
            pass
        def __init__(self, model_instance: DocumentModel):
            self._model = model_instance

        def graphicalObjectChanged(self, go: GraphicalObject):
            self._model.notifyListeners()

        def graphicalObjectSelectionChanged(self, go: GraphicalObject):
            if go.isSelected() and go not in self._model._selected_objects:
                self._model._selected_objects.append(go)
            elif not go.isSelected() and go in self._model._selected_objects:
                self._model._selected_objects.remove(go)
            self._model.notifyListeners()

    def clear(self):
        """
        Clears all objects from the model.
        Ensures all necessary deregistration and notifies document model listeners.
        """
        for obj in list(self._objects):
            self.removeGraphicalObject(obj)
        self._objects.clear()
        self._selected_objects.clear()
        self.notifyListeners()

    def addGraphicalObject(self, obj: GraphicalObject):
        """
        Adds an object to the document.
        Registers the model as an observer to the graphical object.
        """
        if obj not in self._objects:
            self._objects.append(obj)
            obj.addGraphicalObjectListener(self._go_listener)
            # If the object is already selected when added, add it to selected_objects
            if obj.isSelected() and obj not in self._selected_objects:
                self._selected_objects.append(obj)
            self.notifyListeners()

    def removeGraphicalObject(self, obj: GraphicalObject):
        """
        Removes an object from the document.
        Deregisters the model as an observer from the graphical object.
        """
        if obj in self._objects:
            self._objects.remove(obj)
            obj.removeGraphicalObjectListener(self._go_listener)
            # If the object was selected, remove it from selected_objects as well
            if obj in self._selected_objects:
                self._selected_objects.remove(obj)
            self.notifyListeners()

    def list(self) -> list[GraphicalObject]:
        """
        Returns an unmodifiable list of existing objects.
        Changes should only occur through model methods.
        Returns a shallow copy to prevent external modification of the internal list.
        """
        return list(self._objects) # Return a shallow copy

    def addDocumentModelListener(self, l: DocumentModelListener):
        """Registers a listener for document model changes."""
        if l not in self._listeners:
            self._listeners.append(l)

    def removeDocumentModelListener(self, l: DocumentModelListener):
        """Deregisters a listener for document model changes."""
        if l in self._listeners:
            self._listeners.remove(l)

    def notifyListeners(self):
        """Notifies all registered document model listeners of a change."""
        for l in self._listeners:
            l.documentChange()

    def getSelectedObjects(self) -> List[GraphicalObject]:
        """
        Returns a shallow copy to prevent external modification.
        """
        return list(self._selected_objects)

    def increaseZ(self, go: GraphicalObject):
        """
        Moves the given object one position later in the objects list.
        This means it will be rendered later (potentially more visible).
        """
        if go in self._objects:
            current_index = self._objects.index(go)
            if current_index < len(self._objects) - 1:
                self._objects.insert(current_index + 1, self._objects.pop(current_index))
                self.notifyListeners()

    def decreaseZ(self, go: GraphicalObject):
        """
        Moves the given object one position earlier in the objects list.
        """
        if go in self._objects:
            current_index = self._objects.index(go)
            if current_index > 0:
                self._objects.insert(current_index - 1, self._objects.pop(current_index))
                self.notifyListeners()

    def findSelectedGraphicalObject(self, mousePoint: Point) -> Union[GraphicalObject, None]:
        """
        Finds if any object in the model is selected by a click at the given mousePoint.
        Returns the closest object if its distance is within SELECTION_PROXIMITY, otherwise None.
        This method DOES NOT change the selection status of the object.
        """
        min_distance = float('inf')
        selected_object = None

        # Iterate in reverse order to prioritize objects drawn on top (later in the list)
        for obj in reversed(self._objects):
            distance = obj.selectionDistance(mousePoint)
            if distance <= self.SELECTION_PROXIMITY and distance < min_distance:
                min_distance = distance
                selected_object = obj
        return selected_object

    def findSelectedHotPoint(self, obj: GraphicalObject, mousePoint: Point) -> int:
        """
        Finds if the given mousePoint selects any hot-point of the given object.
        Returns the index of the hot-point if its distance is within SELECTION_PROXIMITY,
        otherwise -1. This method DOES NOT change the selection status of the hot-point.
        """
        min_distance = float('inf')
        selected_hot_point_index = -1

        for i in range(obj.getNumberOfHotPoints()):
            hot_point = obj.getHotPoint(i)
            distance = GeometryUtil.distanceFromPoint(hot_point, mousePoint)
            if distance <= self.SELECTION_PROXIMITY and distance < min_distance:
                min_distance = distance
                selected_hot_point_index = i
        return selected_hot_point_index