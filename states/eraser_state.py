from interfaces.interfaces import State, GraphicalObject
from geometry import Point, GeometryUtil
from document_model.document_model import DocumentModel
from renderers.tkinter_renderer_impl import TkinterRendererImpl
from shapes.line_segment import LineSegment

class EraserState(State):
    def __init__(self, model: DocumentModel):
        self.model = model
        self._eraser_points: list[Point] = []
        self._is_dragging: bool = False
        self._highlight_states: dict[GraphicalObject, dict] = {}
        print("Entering EraserState.")

    def mouseDown(self, mousePoint: Point, shiftDown: bool, ctrlDown: bool):
        self._eraser_points = [mousePoint]
        self._is_dragging = True
        self._update_highlight_states()
        self.model.notifyListeners()

    def mouseUp(self, mousePoint: Point, shiftDown: bool, ctrlDown: bool):
        if not self._is_dragging:
            return

        self._eraser_points.append(mousePoint)
        self._is_dragging = False

        objects_to_delete = []
        current_objects = list(self.model.list())
        
        if len(self._eraser_points) >= 2:
            for obj in current_objects:
                crossed_bbox_segments_indices = set()

                # Special handling for LineSegment: use segment-segment intersection
                if isinstance(obj, LineSegment):
                    line_p1, line_p2 = obj.getSegment()
                    for i in range(len(self._eraser_points) - 1):
                        eraser_p1 = self._eraser_points[i]
                        eraser_p2 = self._eraser_points[i+1]
                        if GeometryUtil.doSegmentsIntersect(eraser_p1, eraser_p2, line_p1, line_p2):
                            objects_to_delete.append(obj)
                            break
                else:
                    # For Oval and CompositeShape: bbox intersection
                    bbox = obj.getBoundingBox()
                    bbox_segments = [
                        (Point(bbox.x, bbox.y), Point(bbox.x + bbox.width, bbox.y)),
                        (Point(bbox.x + bbox.width, bbox.y), Point(bbox.x + bbox.width, bbox.y + bbox.height)),
                        (Point(bbox.x + bbox.width, bbox.y + bbox.height), Point(bbox.x, bbox.y + bbox.height)),
                        (Point(bbox.x, bbox.y + bbox.height), Point(bbox.x, bbox.y))
                    ]

                    for i in range(len(self._eraser_points) - 1):
                        eraser_p1 = self._eraser_points[i]
                        eraser_p2 = self._eraser_points[i+1]

                        for idx, (rect_p1, rect_p2) in enumerate(bbox_segments):
                            if GeometryUtil.doSegmentsIntersect(eraser_p1, eraser_p2, rect_p1, rect_p2):
                                crossed_bbox_segments_indices.add(idx)

                    if len(crossed_bbox_segments_indices) >= 2:
                        objects_to_delete.append(obj)   

        for obj in objects_to_delete:
            if obj in self.model.list():
                self.model.removeGraphicalObject(obj)
        
        self._eraser_points = []
        self._highlight_states = {}
        self.model.notifyListeners()

    def mouseDragged(self, mousePoint: Point):
        if self._is_dragging:
            self._eraser_points.append(mousePoint)
            self._update_highlight_states()
            self.model.notifyListeners()

    def _update_highlight_states(self):
        objects_in_model = set(self.model.list())
        for obj_to_remove in list(self._highlight_states.keys()):
            if obj_to_remove not in objects_in_model:
                del self._highlight_states[obj_to_remove]

        if len(self._eraser_points) < 2:
            for obj_state in self._highlight_states.values():
                obj_state['crossed_count'] = 0
                obj_state['current_color'] = None
                obj_state['highlight_type'] = 'bbox'
            return

        for obj in self.model.list():
            num_crossed_segments = 0
            highlight_type = 'bbox' # Default highlight type

            if isinstance(obj, LineSegment):
                line_p1, line_p2 = obj.getSegment()
                distinct_eraser_segment_hits = 0
                for i in range(len(self._eraser_points) - 1):
                    eraser_p1 = self._eraser_points[i]
                    eraser_p2 = self._eraser_points[i+1]
                    if GeometryUtil.doSegmentsIntersect(eraser_p1, eraser_p2, line_p1, line_p2):
                        distinct_eraser_segment_hits += 1

                if distinct_eraser_segment_hits >= 1:
                    num_crossed_segments = 2
                else:
                    num_crossed_segments = 0
                highlight_type = 'shape'
            else:
                bbox = obj.getBoundingBox()
                bbox_segments = [
                    (Point(bbox.x, bbox.y), Point(bbox.x + bbox.width, bbox.y)),
                    (Point(bbox.x + bbox.width, bbox.y), Point(bbox.x + bbox.width, bbox.y + bbox.height)),
                    (Point(bbox.x + bbox.width, bbox.y + bbox.height), Point(bbox.x, bbox.y + bbox.height)),
                    (Point(bbox.x, bbox.y + bbox.height), Point(bbox.x, bbox.y))
                ]
                current_crossed_indices = set()
                for i in range(len(self._eraser_points) - 1):
                    eraser_p1 = self._eraser_points[i]
                    eraser_p2 = self._eraser_points[i+1]

                    for idx, (rect_p1, rect_p2) in enumerate(bbox_segments):
                        if GeometryUtil.doSegmentsIntersect(eraser_p1, eraser_p2, rect_p1, rect_p2):
                            current_crossed_indices.add(idx)
                
                num_crossed_segments = len(current_crossed_indices)
                highlight_type = 'bbox'


            if obj not in self._highlight_states:
                self._highlight_states[obj] = {'crossed_count': 0, 'current_color': None, 'highlight_type': highlight_type}
            
            obj_state = self._highlight_states[obj]
            obj_state['highlight_type'] = highlight_type

            if obj_state['current_color'] == "red":
                pass
            elif num_crossed_segments > obj_state['crossed_count']:
                obj_state['crossed_count'] = num_crossed_segments
                if obj_state['crossed_count'] >= 2:
                    obj_state['current_color'] = "red"
                elif obj_state['crossed_count'] >= 1:
                    obj_state['current_color'] = "green"
                else:
                    obj_state['current_color'] = None
            elif num_crossed_segments == 0 and obj_state['crossed_count'] > 0:
                if obj_state['current_color'] != "red":
                    obj_state['crossed_count'] = 0
                    obj_state['current_color'] = None
            elif num_crossed_segments == 0 and obj_state['current_color'] != "red":
                obj_state['current_color'] = None

    def keyPressed(self, keyCode: str):
        pass

    def afterDraw(self, r: TkinterRendererImpl, go: GraphicalObject):
        pass

    def afterDrawAll(self, r: TkinterRendererImpl):
        if len(self._eraser_points) >= 2:
            for i in range(len(self._eraser_points) - 1):
                p1 = self._eraser_points[i]
                p2 = self._eraser_points[i + 1]
                r.drawLine(p1, p2)
        for obj, state in self._highlight_states.items():
                color = state['current_color']
                highlight_type = state['highlight_type']
                if color:
                    if highlight_type == 'bbox':
                        r.draw_bounding_box(obj.getBoundingBox(), color=color)
                    elif highlight_type == 'shape':
                        if isinstance(obj, LineSegment):
                            p1, p2 = obj.getSegment()
                            r.drawLine(p1, p2, color=color)

    def onLeaving(self):
        print("Leaving EraserState.")
        self._eraser_points = []
        self._is_dragging = False
        self._highlight_states = {}
        self.model.notifyListeners()