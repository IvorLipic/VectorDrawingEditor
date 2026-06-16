from interfaces.interfaces import Renderer
from geometry import Point

class SVGRendererImpl(Renderer):
    def __init__(self, filename: str):
        self.filename = filename
        self._lines = []
        
        # SVG header
        self._lines.append('<svg xmlns="http://www.w3.org/2000/svg" '
                           'xmlns:xlink="http://www.w3.org/1999/xlink" '
                           'width="800" height="600">')

    def close(self):
        self._lines.append('</svg>')
        try:
            with open(self.filename, 'w') as f:
                for line in self._lines:
                    f.write(line + '\n')
            print(f"SVG exported successfully to: {self.filename}")
        except IOError as e:
            print(f"Error writing SVG file: {e}")

    def drawLine(self, s: Point, e: Point, color="blue"):
        self._lines.append(f'  <line x1="{s.x}" y1="{s.y}" x2="{e.x}" y2="{e.y}" '
                           f'stroke="{color}" stroke-width="2" />')

    def fillPolygon(self, points: list[Point]):
        # SVG polygon element: <polygon points="..." style="fill:..;stroke:..;stroke-width:.." />
        # Points are a space-separated list of "x,y" pairs
        points_str = " ".join([f"{p.x},{p.y}" for p in points])
        self._lines.append(f'  <polygon points="{points_str}" style="fill:blue;stroke:red;stroke-width:2" />')