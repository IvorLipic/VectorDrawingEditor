# Vector Drawing Editor

Interactive vector drawing application built with Python and Tkinter. Supports lines, ovals, grouping, SVG export, and file serialization.

## How to Run

```
python main.py
```

## Features

- Draw line segments and ovals interactively
- Group and ungroup objects (select + `G` / `U`)
- Reorder overlapping objects (`+` / `-` keys)
- Delete objects with the eraser tool
- Move and resize objects via drag handles
- Save/load drawings in native format (`.txt`)
- Export to SVG

## Design Patterns

### Observer

Two observer chains keep the UI and composite structure synchronized:
- `DocumentModel` notifies `DrawingCanvas` (via `DocumentModelListener`) whenever the drawing changes — `document_model/document_model.py:23` → `gui.py:19`
- `AbstractGraphicalObject` notifies `DocumentModel` and `CompositeShape` (via `GraphicalObjectListener`) when a shape's properties or selection state change — `shapes/abstract_graphical_object.py:16` → `document_model/document_model.py:19`, `shapes/composite_shape.py:6`

### Composite

Shapes and groups share a uniform `GraphicalObject` interface. `LineSegment` (`shapes/line_segment.py`) and `Oval` (`shapes/oval.py`) are leaf objects; `CompositeShape` (`shapes/composite_shape.py`) holds children and delegates all operations (render, translate, bounding box, selection distance) to them transparently.

### Iterator

The model exposes a `list()` method (`document_model/document_model.py:72`) that returns a shallow copy of the internal object list. All rendering, export, eraser, and selection logic iterate over this list using standard Python `for` loops. Reverse iteration is used for top-to-bottom hit-testing in selection.

### Prototype

The toolbar creates new shapes without depending on concrete classes. A `prototype_map` registry (`gui.py:77`) maps shape IDs to prototype instances. When a tool is activated, `AddShapeState` calls `prototype.duplicate()` (`states/add_shape_state.py:19`) to produce a fresh copy. All concrete shapes implement `duplicate()` — `LineSegment.duplicate()` (`shapes/line_segment.py:30`), `Oval.duplicate()` (`shapes/oval.py:51`), `CompositeShape.duplicate()` (`shapes/composite_shape.py:60`).

### Factory

Loading a drawing uses a stack-based factory approach. `GUI._load_drawing()` (gui.py:171) reads each line, looks up the shape ID in the prototype map, and calls `prototype.load(stack, data)` to deserialize. Each shape implements its own `load()` — `LineSegment.load()` (`shapes/line_segment.py:52`), `Oval.load()` (`shapes/oval.py:83`), `CompositeShape.load()` (`shapes/composite_shape.py:78`). Composites pop their children from the stack in reverse order.

### State

User interaction modes are encapsulated as separate state objects implementing the `State` interface (`interfaces/interfaces.py:77`). The `GUI` class acts as the context, delegating mouse/keyboard events to the current state:
- `IdleState` — `states/idle_state.py`
- `AddShapeState` — `states/add_shape_state.py`
- `SelectShapeState` — `states/select_shape_state.py`
- `EraserState` — `states/eraser_state.py`

New tools can be added without modifying the input handling code in `GUI`.

### Bridge

Rendering is decoupled from graphical output via the `Renderer` interface (`interfaces/interfaces.py:70`). Shapes call `render(r)` with a renderer object, unaware of the concrete implementation:
- `TkinterRendererImpl` (`renderers/tkinter_renderer_impl.py`) — draws to the Tkinter canvas
- `SVGRendererImpl` (`renderers/svg_renderer_impl.py`) — produces SVG output to file

This allows adding new output formats without changing any shape code.

## Serialization Format

Drawings are saved as plain text (`.txt`). Each line starts with a shape ID marker followed by data:
- `@LINE x1 y1 x2 y2` — line segment
- `@OVAL cx cy rx ry` — oval (center x, center y, radius x, radius y)
- `@COMP N` — group of N previously loaded objects (stack-based)

Composites can be nested. Example files are in the `texts_svgs/` directory.

## Sample Files

- `texts_svgs/ooup-lab4-slika1.txt` — flat drawing with lines and ovals
- `texts_svgs/ooup-lab4-slika2.txt` — nested composite structure
- `texts_svgs/ooup-lab4-slika2.svg` — corresponding SVG export

## Acknowledgements

University of Zagreb, Faculty of Electrical Engineering and Computing (FER)

Course: [Oblikovni obrasci u programiranju](https://www.fer.unizg.hr/predmet/ooup)
