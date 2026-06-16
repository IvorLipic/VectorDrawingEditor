import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from document_model.document_model import DocumentModel, DocumentModelListener
from interfaces.interfaces import GraphicalObject, State
from renderers.tkinter_renderer_impl import TkinterRendererImpl
from geometry import Point
from shapes.line_segment import LineSegment
from shapes.oval import Oval
from states.idle_state import IdleState
from states.add_shape_state import AddShapeState
from states.select_shape_state import SelectShapeState
from states.eraser_state import EraserState
from renderers.svg_renderer_impl import SVGRendererImpl
from shapes.composite_shape import CompositeShape

class GUI:
    pass

class DrawingCanvas(tk.Canvas, DocumentModelListener):
    def __init__(self, parent, model: DocumentModel, gui_instance: GUI, **kwargs):
        super().__init__(parent, **kwargs)
        self.model = model
        self.model.addDocumentModelListener(self)
        self.config(bg="white")

        self.gui_instance = gui_instance

        self.bind("<Button-1>", self._on_mouse_down)
        self.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.bind("<B1-Motion>", self._on_mouse_dragged)

    def documentChange(self):
        self.redraw()

    def redraw(self):
        self.delete("all")

        renderer = TkinterRendererImpl(self)

        current_state = self.gui_instance.get_current_state()

        for obj in self.model.list():
            obj.render(renderer)
            current_state.afterDraw(renderer, obj)
            
        current_state.afterDrawAll(renderer)
    
    def _on_mouse_down(self, event):
        mouse_point = Point(event.x, event.y)
        shift_down = (event.state & 0x0001) != 0
        ctrl_down = (event.state & 0x0004) != 0
        self.gui_instance.get_current_state().mouseDown(mouse_point, shift_down, ctrl_down)
        self.redraw()

    def _on_mouse_up(self, event):
        mouse_point = Point(event.x, event.y)
        shift_down = (event.state & 0x0001) != 0
        ctrl_down = (event.state & 0x0004) != 0
        self.gui_instance.get_current_state().mouseUp(mouse_point, shift_down, ctrl_down)
        self.redraw()

    def _on_mouse_dragged(self, event):
        mouse_point = Point(event.x, event.y)
        self.gui_instance.get_current_state().mouseDragged(mouse_point)
        self.redraw()


class GUI(tk.Tk):
    def __init__(self, prototype_objects: list[GraphicalObject]):
        super().__init__()
        self.title("Vector Drawing Program")
        self.geometry("800x600")

        self.model = DocumentModel()
        self._current_state = IdleState()

        self.prototype_map = {}
        for proto in prototype_objects:
            self.prototype_map[proto.getShapeID()] = proto
        if "@COMP" not in self.prototype_map:
            self.prototype_map["@COMP"] = CompositeShape()

        # Create main frames
        self.toolbar_frame = ttk.Frame(self, padding="5")
        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X)

        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self.drawing_canvas = DrawingCanvas(self.canvas_frame, self.model, self, bd=2, relief="sunken")
        self.drawing_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.bind("<KeyPress>", self._on_key_press)

        # Populate toolbar with prototype objects (buttons)
        for obj_proto in prototype_objects:
            btn = ttk.Button(self.toolbar_frame, text=obj_proto.getShapeName(),
                             command=lambda p=obj_proto: self.set_state(AddShapeState(self.model, p)))
            btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Other buttons
        select_btn = ttk.Button(self.toolbar_frame, text="Select",
                                command=lambda: self.set_state(SelectShapeState(self.model)))
        select_btn.pack(side=tk.LEFT, padx=5, pady=2)
        clear_btn = ttk.Button(self.toolbar_frame, text="Clear", command=self.model.clear)
        clear_btn.pack(side=tk.LEFT, padx=5, pady=2)
        eraser_btn = ttk.Button(self.toolbar_frame, text="Eraser",
                                command=lambda: self.set_state(EraserState(self.model)))
        eraser_btn.pack(side=tk.LEFT, padx=5, pady=2)
        svg_export_btn = ttk.Button(self.toolbar_frame, text="SVG Export", command=self._export_svg)
        svg_export_btn.pack(side=tk.LEFT, padx=5, pady=2)
        save_btn = ttk.Button(self.toolbar_frame, text="Save", command=self._save_drawing)
        save_btn.pack(side=tk.LEFT, padx=5, pady=2)
        load_btn = ttk.Button(self.toolbar_frame, text="Load", command=self._load_drawing)
        load_btn.pack(side=tk.LEFT, padx=5, pady=2)
    
    # Provide the current state to canvas
    def get_current_state(self) -> State:
        return self._current_state

    def set_state(self, new_state: State):
        self._current_state.onLeaving()
        self._current_state = new_state
        self.drawing_canvas.redraw()
        print(f"Current state set to: {self._current_state.__class__.__name__}")
    
    def _on_key_press(self, event):
        key_code = event.keysym

        if(key_code == "Escape"):
            self.set_state(IdleState())
            return
        
        self._current_state.keyPressed(key_code)
        self.drawing_canvas.redraw()
    
    def _export_svg(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".svg",
            filetypes=[("SVG files", "*.svg"), ("All files", "*.*")],
            title="Export SVG As"
        )
        if filename:
            try:
                svg_renderer = SVGRendererImpl(filename)
                for obj in self.model.list():
                    obj.render(svg_renderer)
                svg_renderer.close()
            except Exception as e:
                tk.messagebox.showerror("SVG Export Error", f"Failed to export SVG: {e}")
    
    def _save_drawing(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="Save drawing as"
        )
        if filename:
            try:
                rows_to_save = []
                for obj in self.model.list():
                    obj.save(rows_to_save)

                with open(filename, 'w') as f:
                    for row in rows_to_save:
                        f.write(row + '\n')
                messagebox.showinfo("Save successful", f"Drawing saved to: {filename}")
            except Exception as e:
                messagebox.showerror("Error while saving", f"Save failed: {e}")
    
    def _load_drawing(self):
        filename = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="Load drawing"
        )
        if filename:
            try:
                loaded_rows: list[str] = []
                with open(filename, 'r') as f:
                    loaded_rows = f.readlines()

                object_stack: list[GraphicalObject] = []
                
                for line in loaded_rows:
                    line = line.strip()
                    if not line:
                        continue

                    parts = line.split(' ', 1)
                    shape_id = parts[0]
                    data = parts[1] if len(parts) > 1 else ""

                    prototype = self.prototype_map.get(shape_id)
                    
                    if prototype:
                        prototype.load(object_stack, data)
                    else:
                        print(f"Unknown shape ID encountered: {shape_id}. Skipping line: {line}")

                self.model.clear()
                for obj in object_stack:
                    self.model.addGraphicalObject(obj)
                
                messagebox.showinfo("Load successful", f"Drawing loaded from: {filename}")

            except Exception as e:
                messagebox.showerror("Error while loading", f"Load failed: {e}")


def main():
    prototype_objects = [LineSegment(), Oval()]
    app = GUI(prototype_objects)
    app.mainloop()

if __name__ == "__main__":
    main()