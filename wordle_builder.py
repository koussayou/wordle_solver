import tkinter as tk
from tkinter import messagebox
from collections import defaultdict

# Load the allowed Wordle word list from file
with open("wordle.txt") as f:
    WORD_LIST = [line.strip().lower() for line in f if len(line.strip()) == 5 and line.strip().isalpha()]

confirmed_letters = [None] * 5
present_letters = {}
absent_letters = set()
guess_history = []

# Store all matching words after each round
matching_words = []

def apply_feedback(guess, feedback):
    global confirmed_letters, present_letters, absent_letters
    for i, (c, f) in enumerate(zip(guess, feedback)):
        if f == 'g':
            confirmed_letters[i] = c
        elif f == 'y':
            if c not in present_letters:
                present_letters[c] = set()
            present_letters[c].add(i)
        elif f == 'x':
            if c not in guess[:i] + guess[i+1:]:
                absent_letters.add(c)

def is_valid_word(word):
    for i, c in enumerate(word):
        if confirmed_letters[i] and word[i] != confirmed_letters[i]:
            return False
        if c in absent_letters:
            return False
        for pc in present_letters:
            if pc not in word:
                return False
            if any(word[i] == pc for i in present_letters[pc]):
                return False
    return True

def update_matching_words():
    global matching_words
    matching_words = [w for w in WORD_LIST if is_valid_word(w)]

def get_ranked_words():
    freq = defaultdict(int)
    for w in matching_words:
        for c in set(w):
            freq[c] += 1
    ranked = sorted(matching_words, key=lambda w: sum(freq[c] for c in set(w)), reverse=True)
    return ranked

class WordleSolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wordle Solver")
        self.guess_var = tk.StringVar()
        self.feedback_var = tk.StringVar()

        tk.Label(root, text="Enter Guess (e.g., crane)").pack()
        tk.Entry(root, textvariable=self.guess_var, font=('Courier', 16), width=10, justify='center').pack()

        tk.Label(root, text="Enter Feedback (g=green, y=yellow, x=gray)").pack()
        tk.Entry(root, textvariable=self.feedback_var, font=('Courier', 16), width=10, justify='center').pack()

        tk.Button(root, text="Submit", command=self.submit).pack(pady=5)

        self.canvas = tk.Canvas(root, width=300, height=300)
        self.canvas.pack()

        self.output = tk.Text(root, height=10, width=40, font=('Courier', 12))
        self.output.pack()

        self.row_index = 0

    def draw_feedback_row(self, guess, feedback):
        colors = {'g': 'green', 'y': 'gold', 'x': 'gray'}
        for i, (c, f) in enumerate(zip(guess.upper(), feedback)):
            x0 = i * 60 + 10
            y0 = self.row_index * 60 + 10
            x1 = x0 + 50
            y1 = y0 + 50
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=colors[f], outline='black')
            self.canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=c, fill='white', font=('Courier', 20, 'bold'))
        self.row_index += 1

    def submit(self):
        guess = self.guess_var.get().lower()
        feedback = self.feedback_var.get().lower()
        if len(guess) != 5 or len(feedback) != 5:
            messagebox.showerror("Error", "Both guess and feedback must be 5 characters long.")
            return
        apply_feedback(guess, feedback)
        guess_history.append((guess, feedback))
        update_matching_words()
        ranked = get_ranked_words()
        self.draw_feedback_row(guess, feedback)
        self.output.insert(tk.END, f"\nPossible words (top 20):\n")
        for word in ranked[:20]:
            self.output.insert(tk.END, word.upper() + "\n")
        self.guess_var.set("")
        self.feedback_var.set("")

if __name__ == '__main__':
    root = tk.Tk()
    app = WordleSolverApp(root)
    root.mainloop()
