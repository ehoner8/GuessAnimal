import tkinter as tk
import random

IMG_SIZE = 30        # original image is 30x30
FILTER_SIZE = 3       # 3x3 filter
STRIDE = 3
FM_SIZE = IMG_SIZE // STRIDE  # 10x10 feature map
CELL_SIZE = 20       # visual size of each cell

FEATURES = ["eye", "ear", "leg", "neck", "arm"]

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
}

def make_feature_maps():
    # convert 1→True, 0→False
    fm = {}
    for f in FEATURES:
        fm[f] = [[bool(val) for val in row] for row in HARDCODED_MAPS[f]]
    return fm

class ConvolutionGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Convolution Activity – Stride 3 with 3x3 Filter")
        title = tk.Label(self.root, text="Guess the Animal!",
                         font=("Arial", 24, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=10)

        self.feature_maps = make_feature_maps()  # ground truth activations
        self.filter_buttons = {}

        # store user-revealed colors per filter (None = not revealed yet)
        self.user_maps = {
            f: [[None for _ in range(FM_SIZE)] for _ in range(FM_SIZE)]
            for f in FEATURES
        }

        self.selected_feature = FEATURES[0]

        # left panel
        control_frame = tk.Frame(root)
        control_frame.grid(row=1, column=0, padx=10, pady=10)

        tk.Label(control_frame, text="Select Filter:", font=("Arial", 14)).pack()
        for f in FEATURES:
            btn = tk.Button(control_frame, text=f.capitalize(),
                            width=12, font=("Arial", 12),
                            command=lambda ff=f: self.select_feature(ff))
            btn.pack(pady=4)

            self.filter_buttons[f] = btn

        # right panel
        grid_frame = tk.Frame(root)
        grid_frame.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(grid_frame, text="Hidden Image (30x30)", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10)
        tk.Label(grid_frame, text="Feature Map (10x10)", font=("Arial", 14)).grid(row=0, column=1, padx=10, pady=10)
        self.img_canvas = tk.Canvas(grid_frame,
                                    width=IMG_SIZE * CELL_SIZE,
                                    height=IMG_SIZE * CELL_SIZE,
                                    bg="black")
        self.draw_grid(self.img_canvas, IMG_SIZE)
        self.img_canvas.bind("<Button-1>", self.handle_image_click)

        self.fm_canvas = tk.Canvas(grid_frame,
                                   width=FM_SIZE * CELL_SIZE,
                                   height=FM_SIZE * CELL_SIZE,
                                   bg="white")
        self.img_canvas.grid(row=1, column=0, padx=10, pady=10)
        self.fm_canvas.grid(row=1, column=1, padx=10, pady=10)
        self.draw_grid(self.fm_canvas, FM_SIZE)

        self.redraw_feature_map()

    def draw_grid(self, canvas, size):
        for i in range(size):
            for j in range(size):
                canvas.create_rectangle(j * CELL_SIZE,
                                        i * CELL_SIZE,
                                        (j + 1) * CELL_SIZE,
                                        (i + 1) * CELL_SIZE,
                                        outline="gray")

    def select_feature(self, feature):
        self.selected_feature = feature

        # highlight selected button
        for f, btn in self.filter_buttons.items():
            if f == feature:
                btn.config(bg="lightblue")
            else:
                btn.config(bg="SystemButtonFace")

        self.redraw_feature_map()

    def redraw_feature_map(self):
        self.fm_canvas.delete("cell")

        current_map = self.user_maps[self.selected_feature]

        for r in range(FM_SIZE):
            for c in range(FM_SIZE):
                color = current_map[r][c]
                if color:
                    self.fm_canvas.create_rectangle(
                        c * CELL_SIZE, r * CELL_SIZE,
                        (c + 1) * CELL_SIZE, (r + 1) * CELL_SIZE,
                        fill=color, outline="gray", tags="cell"
                    )

    def handle_image_click(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE

        # snap click to nearest stride-aligned top-left index
        fm_row = row // STRIDE
        fm_col = col // STRIDE

        if fm_row < 0 or fm_row >= FM_SIZE or fm_col < 0 or fm_col >= FM_SIZE:
            return

        # retrieve true yes/no from feature map (in your backend logic)
        truth = self.feature_maps[self.selected_feature][fm_row][fm_col]

        # color based on yes/no
        color = "red" if truth else "blue"

        # save into user state
        self.user_maps[self.selected_feature][fm_row][fm_col] = color

        # draw on feature-map canvas
        self.fm_canvas.create_rectangle(
            fm_col * CELL_SIZE, fm_row * CELL_SIZE,
            (fm_col + 1) * CELL_SIZE, (fm_row + 1) * CELL_SIZE,
            fill=color, outline="gray", tags="cell"
        )

        # highlight 3x3 patch on original image (optional)
        self.highlight_patch(fm_row, fm_col)

    def highlight_patch(self, fm_row, fm_col):
        self.img_canvas.delete("patch")
        top = fm_row * STRIDE
        left = fm_col * STRIDE

        # draw highlight around the patch
        self.img_canvas.create_rectangle(
            left * CELL_SIZE,
            top * CELL_SIZE,
            (left + FILTER_SIZE) * CELL_SIZE,
            (top + FILTER_SIZE) * CELL_SIZE,
            outline="yellow", width=3, tags="patch"
        )


root = tk.Tk()
game = ConvolutionGame(root)
root.mainloop()
