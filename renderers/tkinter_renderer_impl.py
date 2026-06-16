import tkinter as tk
from interfaces.interfaces import Renderer
from geometry import Point, Rectangle

class TkinterRendererImpl(Renderer):
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas

    def drawLine(self, s: Point, e: Point, color="blue"):
        self.canvas.create_line(s.x, s.y, e.x, e.y, fill=color, width=2)

    def fillPolygon(self, points: list[Point]):
        # Convert list of Point objects to flat list of x, y coordinates
        coords = []
        for p in points:
            coords.append(p.x)
            coords.append(p.y)
        
        # Fill polygon (blue)
        self.canvas.create_polygon(coords, fill="blue", outline="red", width=2)

    # Helper to draw hot points (small squares)
    def draw_hot_point(self, p: Point, size=4, color="black"):
        x1 = p.x - size // 2
        y1 = p.y - size // 2
        x2 = p.x + size // 2
        y2 = p.y + size // 2
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

    # Helper to draw bounding box (dashed rectangle)
    def draw_bounding_box(self, bbox: Rectangle, color="gray"):
        x1 = bbox.x
        y1 = bbox.y
        x2 = bbox.x + bbox.width
        y2 = bbox.y + bbox.height
        self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, dash=(3, 2))