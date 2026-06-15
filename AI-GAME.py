import tkinter as tk
from tkinter import messagebox
import math
import random

ROWS, COLS = 6, 7

EMPTY = 0
P1 = 1
P2 = 2

CELL = 90
RADIUS = 36
TOP = 90

WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + TOP + 80

BG = "#0f2027"
BOARD = "#14532d"

EMPTY_COLOR = "#d1fae5"
P1_COLOR = "#22c55e"
P2_COLOR = "#000000"

TEXT = "white"
ACCENT = "#86efac"

DEPTH = 5


def make_board():
    return [[EMPTY] * COLS for _ in range(ROWS)]


def valid_cols(board):
    return [c for c in range(COLS) if board[0][c] == EMPTY]


def drop_piece(board, col, piece):

    for r in range(ROWS - 1, -1, -1):

        if board[r][col] == EMPTY:
            board[r][col] = piece
            return r

    return -1


def check_win(board, piece):

    for r in range(ROWS):
        for c in range(COLS - 3):

            if all(board[r][c+i] == piece for i in range(4)):
                return True

    for r in range(ROWS - 3):
        for c in range(COLS):

            if all(board[r+i][c] == piece for i in range(4)):
                return True

    for r in range(ROWS - 3):
        for c in range(COLS - 3):

            if all(board[r+i][c+i] == piece for i in range(4)):
                return True

    for r in range(3, ROWS):
        for c in range(COLS - 3):

            if all(board[r-i][c+i] == piece for i in range(4)):
                return True

    return False


def is_terminal(board):

    return (
        check_win(board, P1)
        or check_win(board, P2)
        or len(valid_cols(board)) == 0
    )


def score_window(window, piece):

    score = 0
    opp = P1 if piece == P2 else P2

    if window.count(piece) == 4:
        score += 100

    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 10

    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 5

    if window.count(opp) == 3 and window.count(EMPTY) == 1:
        score -= 80

    return score


def evaluate(board, piece):

    score = 0

    center = [board[r][COLS // 2] for r in range(ROWS)]
    score += center.count(piece) * 6

    for r in range(ROWS):

        row = board[r]

        for c in range(COLS - 3):

            window = row[c:c+4]
            score += score_window(window, piece)

    for c in range(COLS):

        col = [board[r][c] for r in range(ROWS)]

        for r in range(ROWS - 3):

            window = col[r:r+4]
            score += score_window(window, piece)

    for r in range(ROWS - 3):
        for c in range(COLS - 3):

            window = [board[r+i][c+i] for i in range(4)]
            score += score_window(window, piece)

    for r in range(3, ROWS):
        for c in range(COLS - 3):

            window = [board[r-i][c+i] for i in range(4)]
            score += score_window(window, piece)

    return score


def copy_board(board):
    return [row[:] for row in board]


def minimax(board, depth, alpha, beta, maximizing):

    if depth == 0 or is_terminal(board):

        if check_win(board, P2):
            return None, 1000000

        if check_win(board, P1):
            return None, -1000000

        return None, evaluate(board, P2)

    cols = valid_cols(board)
    best_col = random.choice(cols)

    if maximizing:

        value = -math.inf

        for c in cols:

            b = copy_board(board)
            drop_piece(b, c, P2)

            _, score = minimax(
                b,
                depth - 1,
                alpha,
                beta,
                False
            )

            if score > value:
                value = score
                best_col = c

            alpha = max(alpha, value)

            if alpha >= beta:
                break

        return best_col, value

    else:

        value = math.inf

        for c in cols:

            b = copy_board(board)
            drop_piece(b, c, P1)

            _, score = minimax(
                b,
                depth - 1,
                alpha,
                beta,
                True
            )

            if score < value:
                value = score
                best_col = c

            beta = min(beta, value)

            if alpha >= beta:
                break

        return best_col, value


class Connect4:

    def __init__(self, root):

        self.root = root
        self.root.title("Connect 4")

        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.board = make_board()

        self.turn = True
        self.over = False

        self.mode = None
        self.started = False

        self.moves = 0

        self.p1_score = 0
        self.p2_score = 0
        self.draws = 0

        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            bg=BG,
            highlightthickness=0
        )

        self.canvas.pack()

        self.restart_btn = tk.Button(
            root,
            text="Restart",
            font=("Arial", 12, "bold"),
            bg=BOARD,
            fg="white",
            command=self.restart
        )

        self.restart_btn.pack(pady=5)

        self.canvas.bind("<Button-1>", self.click)

        self.start_screen()

    def start_screen(self):

        self.canvas.delete("all")

        self.canvas.create_text(
            WIDTH//2,
            180,
            text="CONNECT 4",
            font=("Arial", 30, "bold"),
            fill=ACCENT
        )

        self.start_btn = tk.Button(
            self.root,
            text="START",
            font=("Arial", 16, "bold"),
            bg=P1_COLOR,
            fg="white",
            width=12,
            command=self.mode_screen
        )

        self.canvas.create_window(
            WIDTH//2,
            320,
            window=self.start_btn
        )

    def mode_screen(self):

        self.start_btn.destroy()

        self.canvas.delete("all")

        self.canvas.create_text(
            WIDTH//2,
            120,
            text="SELECT MODE",
            font=("Arial", 24, "bold"),
            fill=ACCENT
        )

        ai_btn = tk.Button(
            self.root,
            text="Human vs AI",
            font=("Arial", 14, "bold"),
            bg=P1_COLOR,
            fg="white",
            width=15,
            command=lambda: self.start_game("AI")
        )

        human_btn = tk.Button(
            self.root,
            text="Human vs Human",
            font=("Arial", 14, "bold"),
            bg="black",
            fg="white",
            width=15,
            command=lambda: self.start_game("HUMAN")
        )

        self.canvas.create_window(WIDTH//2, 240, window=ai_btn)
        self.canvas.create_window(WIDTH//2, 320, window=human_btn)

    def start_game(self, mode):

        self.mode = mode

        self.started = True
        self.over = False

        self.turn = True
        self.moves = 0

        self.board = make_board()

        self.draw_board()

    def draw_board(self):

        self.canvas.delete("all")

        if not self.started:
            return

        if self.mode == "AI":

            turn_text = "Your Turn" if self.turn else "AI Turn"

        else:

            turn_text = (
                "Player 1 Turn"
                if self.turn
                else "Player 2 Turn"
            )

        self.canvas.create_text(
            WIDTH//2,
            20,
            text=turn_text,
            fill=TEXT,
            font=("Arial", 16, "bold")
        )

        self.canvas.create_text(
            WIDTH//2,
            50,
            text=f"P1:{self.p1_score}  AI/P2:{self.p2_score}  Draw:{self.draws}",
            fill=ACCENT,
            font=("Arial", 11, "bold")
        )

        self.canvas.create_rectangle(
            0,
            TOP,
            WIDTH,
            TOP + ROWS * CELL,
            fill=BOARD
        )

        for r in range(ROWS):
            for c in range(COLS):

                x = c * CELL + CELL//2
                y = TOP + r * CELL + CELL//2

                piece = self.board[r][c]

                color = EMPTY_COLOR

                if piece == P1:
                    color = P1_COLOR

                elif piece == P2:
                    color = P2_COLOR

                self.canvas.create_oval(
                    x - RADIUS,
                    y - RADIUS,
                    x + RADIUS,
                    y + RADIUS,
                    fill=color,
                    outline=""
                )

    def find_row(self, col):

        for r in range(ROWS - 1, -1, -1):

            if self.board[r][col] == EMPTY:
                return r

        return -1

    def animate(self, col, piece):

        final_row = self.find_row(col)

        if final_row == -1:
            return

        for r in range(final_row + 1):

            if r > 0:
                self.board[r - 1][col] = EMPTY

            self.board[r][col] = piece

            self.draw_board()

            self.root.update()

            self.root.after(45)

        return final_row

    def click(self, event):

        if not self.started or self.over:
            return

        col = event.x // CELL

        if col >= COLS:
            return

        if self.find_row(col) == -1:
            return

        if self.mode == "AI":

            if not self.turn:
                return

            self.animate(col, P1)

            self.moves += 1

            if check_win(self.board, P1):
                self.finish("You Win!", "p1")
                return

            if len(valid_cols(self.board)) == 0:
                self.finish("Draw!", "draw")
                return

            self.turn = False

            self.draw_board()

            self.root.after(300, self.ai_move)

        else:

            piece = P1 if self.turn else P2

            self.animate(col, piece)

            self.moves += 1

            if check_win(self.board, piece):

                text = (
                    "Player 1 Wins!"
                    if piece == P1
                    else "Player 2 Wins!"
                )

                self.finish(text, "p1")
                return

            if len(valid_cols(self.board)) == 0:
                self.finish("Draw!", "draw")
                return

            self.turn = not self.turn

            self.draw_board()

    def ai_move(self):

        col, _ = minimax(
            self.board,
            DEPTH,
            -math.inf,
            math.inf,
            True
        )

        if col is not None:

            self.animate(col, P2)

            self.moves += 1

            if check_win(self.board, P2):
                self.finish("AI Wins!", "p2")
                return

            if len(valid_cols(self.board)) == 0:
                self.finish("Draw!", "draw")
                return

        self.turn = True

        self.draw_board()

    def finish(self, text, mode):

        self.over = True

        if mode == "p1":
            self.p1_score += 1

        elif mode == "p2":
            self.p2_score += 1

        else:
            self.draws += 1

        self.draw_board()

        again = messagebox.askyesno(
            "Game Over",
            f"{text}\n\nTry Again?"
        )

        if again:
            self.start_game(self.mode)

    def restart(self):

        self.started = False
        self.over = False

        self.mode = None

        self.moves = 0

        self.board = make_board()

        self.turn = True

        self.start_screen()


if __name__ == "__main__":

    root = tk.Tk()

    game = Connect4(root)

    root.mainloop()