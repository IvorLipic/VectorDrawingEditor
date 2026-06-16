import math

class Point:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def translate(self, dp):
        return Point(self._x + dp.x, self._y + dp.y)

    def difference(self, p):
        return Point(self._x - p.x, self._y - p.y)

    def __str__(self):
        return f"({self._x}, {self._y})"

    def __repr__(self):
        return f"Point(x={self._x}, y={self._y})"

class Rectangle:
    def __init__(self, x, y, width, height):
        self._x = x
        self._y = y
        self._width = width
        self._height = height

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def __str__(self):
        return f"Rect(x={self._x}, y={self._y}, w={self._width}, h={self._height})"

class GeometryUtil:
    @staticmethod
    def distanceFromPoint(point1, point2):
        dx = point1.x - point2.x
        dy = point1.y - point2.y
        return math.sqrt(dx**2 + dy**2)

    @staticmethod
    def distanceFromLineSegment(s, e, p):
        segment_length_sq = GeometryUtil.distanceFromPoint(s, e)**2
        if segment_length_sq == 0:
            return GeometryUtil.distanceFromPoint(s, p)

        t = ((p.x - s.x) * (e.x - s.x) + (p.y - s.y) * (e.y - s.y)) / segment_length_sq
        t = max(0, min(1, t))

        closest_point_on_segment = Point(s.x + t * (e.x - s.x), s.y + t * (e.y - s.y))
        return GeometryUtil.distanceFromPoint(p, closest_point_on_segment)
    
    @staticmethod
    def distanceFromPointToLineSegment(p: Point, s1: Point, s2: Point) -> float:
        # Calculate squared length of the segment
        l2 = GeometryUtil.distanceFromPoint(s1, s2)**2
        if l2 == 0.0:  # s1 == s2, segment is a point
            return GeometryUtil.distanceFromPoint(p, s1)

        # Consider the line containing the segment and find the closest point on it
        t = ((p.x - s1.x) * (s2.x - s1.x) + (p.y - s1.y) * (s2.y - s1.y)) / l2
        t = max(0.0, min(1.0, t)) # Clamp t to [0, 1]

        # The closest point on the segment
        projection_x = s1.x + t * (s2.x - s1.x)
        projection_y = s1.y + t * (s2.y - s1.y)
        
        closest_point = Point(int(projection_x), int(projection_y))

        return GeometryUtil.distanceFromPoint(p, closest_point)

    @staticmethod
    def doSegmentsIntersect(p1_s1: Point, p2_s1: Point, p1_s2: Point, p2_s2: Point) -> bool:
        # From: https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
        # Function to calculate orientation
        def orientation(p, q, r):
            val = (q.y - p.y) * (r.x - q.x) - \
                  (q.x - p.x) * (r.y - q.y)
            if val == 0: return 0  # Collinear
            return 1 if val > 0 else 2 # Clockwise or Counterclockwise

        # Function to check if point q lies on segment pr
        def on_segment(p, q, r):
            return (q.x <= max(p.x, r.x) and q.x >= min(p.x, r.x) and
                    q.y <= max(p.y, r.y) and q.y >= min(p.y, r.y))

        o1 = orientation(p1_s1, p2_s1, p1_s2)
        o2 = orientation(p1_s1, p2_s1, p2_s2)
        o3 = orientation(p1_s2, p2_s2, p1_s1)
        o4 = orientation(p1_s2, p2_s2, p2_s1)

        # General case
        if o1 != 0 and o2 != 0 and o3 != 0 and o4 != 0 and \
           o1 != o2 and o3 != o4:
            return True

        # Special cases for collinear segments
        # p1_s1, p2_s1 and p1_s2 are collinear and p1_s2 lies on segment (p1_s1, p2_s1)
        if o1 == 0 and on_segment(p1_s1, p1_s2, p2_s1): return True
        # p1_s1, p2_s1 and p2_s2 are collinear and p2_s2 lies on segment (p1_s1, p2_s1)
        if o2 == 0 and on_segment(p1_s1, p2_s2, p2_s1): return True
        # p1_s2, p2_s2 and p1_s1 are collinear and p1_s1 lies on segment (p1_s2, p2_s2)
        if o3 == 0 and on_segment(p1_s2, p1_s1, p2_s2): return True
        # p1_s2, p2_s2 and p2_s1 are collinear and p2_s1 lies on segment (p1_s2, p2_s2)
        if o4 == 0 and on_segment(p1_s2, p2_s1, p2_s2): return True

        return False # No intersection