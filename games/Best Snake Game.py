import random
import tkinter as tk

CELL = 20
WIDTH = 30
HEIGHT = 20


class SnakeGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Best Snake Game")
        self.resizable(False, False)

        self.canvas = tk.Canvas(self, width=WIDTH * CELL, height=HEIGHT * CELL, bg="black")
        self.canvas.pack()

        self.direction = (1, 0)
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.food = self.new_food()
        self.score = 0
        self.running = True

        self.bind("<Up>", lambda e: self.set_direction(0, -1))
        self.bind("<Down>", lambda e: self.set_direction(0, 1))
        self.bind("<Left>", lambda e: self.set_direction(-1, 0))
        self.bind("<Right>", lambda e: self.set_direction(1, 0))

        self.tick()

    def set_direction(self, dx, dy):
        if (dx, dy) == (-self.direction[0], -self.direction[1]):
            return
        self.direction = (dx, dy)

    def new_food(self):
        while True:
            p = (random.randrange(WIDTH), random.randrange(HEIGHT))
            if p not in self.snake:
                return p

    def tick(self):
        if not self.running:
            return

        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        if (
            new_head[0] < 0
            or new_head[0] >= WIDTH
            or new_head[1] < 0
            or new_head[1] >= HEIGHT
            or new_head in self.snake
        ):
            self.running = False
            self.draw()
            self.canvas.create_text(
                WIDTH * CELL // 2,
                HEIGHT * CELL // 2,
                text=f"Game Over! Score: {self.score}",
                fill="white",
                font=("Arial", 18, "bold"),
            )
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            self.food = self.new_food()
        else:
            self.snake.pop()

        self.draw()
        self.after(100, self.tick)

    def draw(self):
        self.canvas.delete("all")
        for x, y in self.snake:
            self.canvas.create_rectangle(x * CELL, y * CELL, (x + 1) * CELL, (y + 1) * CELL, fill="lime", outline="")
        fx, fy = self.food
        self.canvas.create_oval(fx * CELL, fy * CELL, (fx + 1) * CELL, (fy + 1) * CELL, fill="red", outline="")
        self.canvas.create_text(60, 12, text=f"Score: {self.score}", fill="white", font=("Arial", 12, "bold"))


if __name__ == "__main__":
    SnakeGame().mainloop()
