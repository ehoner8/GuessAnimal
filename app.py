import tkinter as tk
import random

IMG_SIZE = 30
FILTER_SIZE = 3
STRIDE = 3
FM_SIZE = IMG_SIZE // STRIDE
CELL_SIZE = 20

FEATURES = ["eye", "ear", "leg", "neck", "arm", "wing"]

HARDCODED_MAPS = {
    "eye": [
        [0,0,0,0,1,0,1,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
    ],
    "ear": [
        [0,0,0,1,0,0,1,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
    ],
    "leg": [
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,1,1,0,1,1,0,0,0],
        [0,0,1,1,0,1,1,0,0,0],
    ],
    "neck": [
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,1,0,0,0,0],
        [0,0,0,0,0,1,0,0,0,0],
        [0,0,0,0,0,1,0,0,0,0],
        [0,0,0,0,0,1,0,0,0,0],
        [0,0,0,0,0,1,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
    ],
    "arm": [
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
    ],
    "wing": [
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
    ]
}

def make_feature_maps():
    fm = {}
    for f in FEATURES:
        fm[f] = [[bool(val) for val in row] for row in HARDCODED_MAPS[f]]
    return fm


class ConvolutionGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Convolution Activity")

        title = tk.Label(self.root, text="Guess the Animal!",
                         font=("Arial", 24, "bold"))
        title.grid(row=0, column=0, columnspan=3, pady=10)

        self.feature_maps = make_feature_maps()
        self.filter_buttons = {}
        self.fm_canvases = {}

        self.user_maps = {
            f: [[None for _ in range(FM_SIZE)] for _ in range(FM_SIZE)]
            for f in FEATURES
        }

        # cursor position inside 10x10 feature map
        self.cursor_row = 0
        self.cursor_col = 0

        self.selected_feature = FEATURES[0]

        # Key bindings for arrow movement
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)
        self.root.bind("<Up>", self.move_up)
        self.root.bind("<Down>", self.move_down)

        # LEFT control panel
        control = tk.Frame(root)
        control.grid(row=1, column=0, padx=10)

        tk.Label(control, text="Select Filter:", font=("Arial", 14)).pack()
        for f in FEATURES:
            btn = tk.Button(control, text=f.capitalize(), width=12,
                            command=lambda ff=f: self.select_feature(ff))
            btn.pack(pady=4)
            self.filter_buttons[f] = btn

        # CENTER: image
        self.img_canvas = tk.Canvas(root,
                                    width=IMG_SIZE * CELL_SIZE,
                                    height=IMG_SIZE * CELL_SIZE,
                                    bg="black")
        self.img_canvas.grid(row=1, column=1, padx=10, pady=10)
        self.draw_grid(self.img_canvas, IMG_SIZE)

        self.img_canvas.bind("<Button-1>", self.handle_image_click)

        # RIGHT: all feature maps
        fm_frame = tk.Frame(root)
        fm_frame.grid(row=1, column=2, padx=10)

        idx = 0
        for r in range(2):
            for c in range(3):
                if idx >= len(FEATURES):
                    break

                f = FEATURES[idx]
                sub = tk.Frame(fm_frame)
                sub.grid(row=r, column=c, padx=5, pady=5)

                tk.Label(sub, text=f"{f.capitalize()} Map",
                         font=("Arial", 12)).pack()

                canvas = tk.Canvas(sub,
                                   width=FM_SIZE * CELL_SIZE,
                                   height=FM_SIZE * CELL_SIZE,
                                   bg="white")
                canvas.pack()

                self.draw_grid(canvas, FM_SIZE)
                self.fm_canvases[f] = canvas

                idx += 1

        self.select_feature(self.selected_feature)
        self.redraw_all_feature_maps()
        self.highlight_patch(self.cursor_row, self.cursor_col)

    # ---------------- Utility ----------------

    def draw_grid(self, canvas, size):
        for i in range(size):
            for j in range(size):
                canvas.create_rectangle(j*CELL_SIZE, i*CELL_SIZE,
                                        (j+1)*CELL_SIZE, (i+1)*CELL_SIZE,
                                        outline="gray")

    def select_feature(self, feature):
        self.selected_feature = feature

        for f, btn in self.filter_buttons.items():
            btn.config(bg="lightblue" if f == feature else "SystemButtonFace")

    def redraw_all_feature_maps(self):
        for f in FEATURES:
            self.redraw_feature_map(f)

    def redraw_feature_map(self, feature):
        canvas = self.fm_canvases[feature]
        canvas.delete("cell")
        for r in range(FM_SIZE):
            for c in range(FM_SIZE):
                color = self.user_maps[feature][r][c]
                if color:
                    canvas.create_rectangle(
                        c*CELL_SIZE, r*CELL_SIZE,
                        (c+1)*CELL_SIZE, (r+1)*CELL_SIZE,
                        fill=color, outline="gray", tags="cell"
                    )

    # ---------------- Reveal logic used by click & arrow keys ----------------

    def reveal_current_position(self):
        f = self.selected_feature
        truth = self.feature_maps[f][self.cursor_row][self.cursor_col]
        color = "red" if truth else "blue"

        self.user_maps[f][self.cursor_row][self.cursor_col] = color
        self.redraw_feature_map(f)
        self.highlight_patch(self.cursor_row, self.cursor_col)

    # ---------------- Mouse click ----------------

    def handle_image_click(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        fm_row = row // STRIDE
        fm_col = col // STRIDE

        if not (0 <= fm_row < FM_SIZE and 0 <= fm_col < FM_SIZE):
            return

        self.cursor_row = fm_row
        self.cursor_col = fm_col
        self.reveal_current_position()

    # ---------------- Arrow key movement ----------------

    def move_left(self, event):
        if self.cursor_col > 0:
            self.cursor_col -= 1
            self.reveal_current_position()

    def move_right(self, event):
        if self.cursor_col < FM_SIZE - 1:
            self.cursor_col += 1
            self.reveal_current_position()

    def move_up(self, event):
        if self.cursor_row > 0:
            self.cursor_row -= 1
            self.reveal_current_position()

    def move_down(self, event):
        if self.cursor_row < FM_SIZE - 1:
            self.cursor_row += 1
            self.reveal_current_position()

    # ---------------- Highlight 3×3 patch ----------------

    def highlight_patch(self, fm_row, fm_col):
        self.img_canvas.delete("patch")
        top = fm_row * STRIDE
        left = fm_col * STRIDE

        self.img_canvas.create_rectangle(
            left * CELL_SIZE,
            top * CELL_SIZE,
            (left + FILTER_SIZE) * CELL_SIZE,
            (top + FILTER_SIZE) * CELL_SIZE,
            outline="yellow",
            width=3,
            tags="patch"
        )


root = tk.Tk()
game = ConvolutionGame(root)
root.mainloop()
