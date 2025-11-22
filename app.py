import tkinter as tk
from PIL import Image, ImageTk

IMG_SIZE = 30
FILTER_SIZE = 3
STRIDE = 3
FM_SIZE = IMG_SIZE // STRIDE
CELL_SIZE = 20

FEATURES = ["eye", "ear", "leg", "neck", "arm", "wing"]

HARDCODED_MAPS = {
    "eye": [
        [0,0,0,0,1,1,0,0,0,0],
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
    "leg": [
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,1,0,1,1,0,0,0],
        [0,0,0,1,0,1,1,0,0,0],
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
    return {f: [[bool(v) for v in row] for row in HARDCODED_MAPS[f]] for f in FEATURES}


class ConvolutionGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Convolution Activity")

        # Title
        tk.Label(root, text="Guess the Animal!",
                 font=("Arial", 26, "bold")).grid(row=0, column=0, columnspan=3, pady=10)

        # Load giraffe image (when guessed correctly)
        try:
            self.giraffe_img = Image.open("giraffe2.png")
            self.giraffe_img = self.giraffe_img.resize(
                (IMG_SIZE * CELL_SIZE, IMG_SIZE * CELL_SIZE))
            self.giraffe_img_tk = ImageTk.PhotoImage(self.giraffe_img)
        except:
            self.giraffe_img_tk = None

        self.image_revealed = False

        self.feature_maps = make_feature_maps()

        self.user_maps = {
            f: [[None for _ in range(FM_SIZE)] for _ in range(FM_SIZE)]
            for f in FEATURES
        }

        # Start with no selected position
        self.cursor_row = None
        self.cursor_col = None

        self.selected_feature = FEATURES[0]

        # Key bindings
        root.bind("<Left>", self.move_left)
        root.bind("<Right>", self.move_right)
        root.bind("<Up>", self.move_up)
        root.bind("<Down>", self.move_down)

        # LEFT panel
        control = tk.Frame(root)
        control.grid(row=1, column=0, padx=10)
        tk.Label(control, text="Select Filter:", font=("Arial", 14)).pack()

        self.filter_buttons = {}
        for f in FEATURES:
            btn = tk.Button(control, text=f.capitalize(), width=12,
                            command=lambda ff=f: self.select_feature(ff))
            btn.pack(pady=4)
            self.filter_buttons[f] = btn

        # CENTER image canvas
        self.img_canvas = tk.Canvas(root,
                                    width=IMG_SIZE * CELL_SIZE,
                                    height=IMG_SIZE * CELL_SIZE,
                                    bg="black")
        self.img_canvas.grid(row=1, column=1, padx=10, pady=10)
        self.draw_grid(self.img_canvas, IMG_SIZE)
        self.img_canvas.bind("<Button-1>", self.handle_image_click)

        # RIGHT feature maps
        fm_frame = tk.Frame(root)
        fm_frame.grid(row=1, column=2, padx=10)
        self.fm_canvases = {}

        idx = 0
        for r in range(2):
            for c in range(3):
                if idx >= len(FEATURES):
                    break
                f = FEATURES[idx]

                sub = tk.Frame(fm_frame)
                sub.grid(row=r, column=c, padx=5, pady=10)

                tk.Label(sub, text=f"{f.capitalize()} Map",
                         font=("Arial", 13)).pack()

                canvas = tk.Canvas(sub,
                                   width=FM_SIZE * CELL_SIZE,
                                   height=FM_SIZE * CELL_SIZE,
                                   bg="white")
                canvas.pack()

                self.draw_grid(canvas, FM_SIZE)
                self.fm_canvases[f] = canvas

                idx += 1

        # Guess box
        guess_frame = tk.Frame(root)
        guess_frame.grid(row=2, column=1, pady=10)

        tk.Label(guess_frame, text="Your Guess:", font=("Arial", 14)).pack(side="left")
        self.guess_entry = tk.Entry(guess_frame, font=("Arial", 14))
        self.guess_entry.pack(side="left", padx=5)
        tk.Button(guess_frame, text="Guess!", font=("Arial", 12),
                  command=self.check_guess).pack(side="left")

        self.feedback_label = tk.Label(root, text="", font=("Arial", 18))
        self.feedback_label.grid(row=3, column=1)

        self.select_feature(self.selected_feature)
        self.redraw_all_feature_maps()

    # -------------------------------------------------

    def draw_grid(self, canvas, size):
        for i in range(size):
            for j in range(size):
                canvas.create_rectangle(
                    j * CELL_SIZE, i * CELL_SIZE,
                    (j+1)*CELL_SIZE, (i+1)*CELL_SIZE,
                    outline="gray"
                )

    # -------------------------------------------------

    def select_feature(self, feature):
        self.selected_feature = feature

        for f, btn in self.filter_buttons.items():
            btn.config(bg="lightblue" if f == feature else "SystemButtonFace")

        self.redraw_feature_map(feature)

    # -------------------------------------------------

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

    # -------------------------------------------------

    def reveal_current_position(self):
        if self.cursor_row is None:
            return

        f = self.selected_feature
        truth = self.feature_maps[f][self.cursor_row][self.cursor_col]
        color = "red" if truth else "blue"

        self.user_maps[f][self.cursor_row][self.cursor_col] = color
        self.redraw_feature_map(f)
        self.highlight_patch()

    # -------------------------------------------------

    def handle_image_click(self, event):
        if self.image_revealed:
            return

        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE

        fm_row = row // STRIDE
        fm_col = col // STRIDE

        if not (0 <= fm_row < FM_SIZE and 0 <= fm_col < FM_SIZE):
            return

        self.cursor_row, self.cursor_col = fm_row, fm_col
        self.reveal_current_position()
        self.highlight_feature_cell(fm_row, fm_col)


    # -------------------------------------------------
    # Arrow key movement
    # -------------------------------------------------

    def move_left(self, event):
        if self.cursor_col is not None and self.cursor_col > 0:
            self.cursor_col -= 1
            self.reveal_current_position()
            self.highlight_feature_cell(self.cursor_row, self.cursor_col)


    def move_right(self, event):
        if self.cursor_col is not None and self.cursor_col < FM_SIZE - 1:
            self.cursor_col += 1
            self.reveal_current_position()
            self.highlight_feature_cell(self.cursor_row, self.cursor_col)


    def move_up(self, event):
        if self.cursor_row is not None and self.cursor_row > 0:
            self.cursor_row -= 1
            self.reveal_current_position()
            self.highlight_feature_cell(self.cursor_row, self.cursor_col)


    def move_down(self, event):
        if self.cursor_row is not None and self.cursor_row < FM_SIZE - 1:
            self.cursor_row += 1
            self.reveal_current_position()
            self.highlight_feature_cell(self.cursor_row, self.cursor_col)


    # -------------------------------------------------

    def highlight_patch(self):
        self.img_canvas.delete("patch")
        if self.cursor_row is None:
            return

        top = self.cursor_row * STRIDE
        left = self.cursor_col * STRIDE

        self.img_canvas.create_rectangle(
            left * CELL_SIZE,
            top * CELL_SIZE,
            (left + FILTER_SIZE) * CELL_SIZE,
            (top + FILTER_SIZE) * CELL_SIZE,
            outline="yellow",
            width=3,
            tags="patch"
        )
    def highlight_feature_cell(self, r, c):
        """Highlight the (r,c) cell in the currently selected feature map."""
        canvas = self.fm_canvases[self.selected_feature]

        # Remove previous highlight on this feature map
        canvas.delete("fm_patch")

        # Draw the yellow outline
        canvas.create_rectangle(
            c * CELL_SIZE,
            r * CELL_SIZE,
            (c + 1) * CELL_SIZE,
            (r + 1) * CELL_SIZE,
            outline="yellow",
            width=3,
            tags="fm_patch"
        )

    # -------------------------------------------------
    # Guessing logic
    # -------------------------------------------------

    def check_guess(self):
        guess = self.guess_entry.get().strip().lower()

        if guess == "giraffe":
            self.feedback_label.config(text="Correct!", fg="green")
            self.reveal_image()
        else:
            self.feedback_label.config(text="❌ Incorrect!", fg="red")

    def reveal_image(self):
        if not self.giraffe_img_tk:
            self.feedback_label.config(text="(Missing giraffe2.png)", fg="orange")
            return

        self.image_revealed = True
        self.img_canvas.delete("all")

        self.img_canvas.create_image(
            0, 0, anchor="nw", image=self.giraffe_img_tk
        )

        self.img_canvas.image = self.giraffe_img_tk  # prevent garbage collection


root = tk.Tk()
game = ConvolutionGame(root)
root.mainloop()
