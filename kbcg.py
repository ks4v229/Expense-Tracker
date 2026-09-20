import tkinter as tk
from tkinter import messagebox
import csv
import random





class KBCGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Kaun Banega Crorepati")
        self.root.geometry("900x620")
        self.root.config(bg="#0b1220")

        # Game variables
        self.questions = []
        self.current = 0            # current question index (0-based)
        self.money = 0              # current prize (exact prize of last cleared question)
        self.safe_money = 0         # last guaranteed prize (safe milestone)
        self.lifelines = {
            "5050": False,
            "audience": False,
            "phone": False,
            "flip": False
        }
        self.removed_options = set()
        self.used_questions_idx = set()
        # Safe milestones (0-based indices). Q5 -> index 4, Q10 -> index 9
        self.milestones = {4: 10000, 9: 320000}

        # Load CSV and build UI
        try:
            self.load_csv()






        except Exception as e:
            messagebox.showerror("CSV Error", f"Could not load Questions.csv\nError: {e}")
            root.destroy()
            return

        self.create_ui()
        self.show_question()






    def load_csv(self):
        # Keep CSV structure unchanged: name, option1..4, answer (1-based), money
        with open("Questions.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.questions.append({
                    "name": row["name"],
                    "options": [row["option1"], row["option2"], row["option3"], row["option4"]],
                    "answer": int(row["answer"]),
                    "money": int(row["money"])
                })





    def create_ui(self):
        title = tk.Label(self.root, text="KAUN BANEGA CROREPATI", 
                         font=("Helvetica", 24, "bold"), fg="#e6b800", bg="#0b1220")
        title.pack(pady=12)

        self.q_label = tk.Label(self.root, text="", font=("Arial", 16, "bold"),
                                wraplength=760, fg="#ffffff", bg="#0b1220", justify="left")
        self.q_label.pack(pady=10)

        # Option buttons (2x2 grid)
        opts_frame = tk.Frame(self.root, bg="#0b1220")
        opts_frame.pack(pady=6)
        self.buttons = []
        for i in range(4):
            btn = tk.Button(opts_frame, text="", font=("Arial", 14), width=40, height=2,
                            bg="#252a34", fg="white", bd=0, activebackground="#3a3f49",
                            command=lambda i=i: self.check_answer(i))
            btn.grid(row=i//2, column=i%2, padx=8, pady=8)
            self.buttons.append(btn)

        # Lifeline buttons
        lifeline_frame = tk.Frame(self.root, bg="#0b1220")
        lifeline_frame.pack(pady=12)

        self.ll_5050 = tk.Button(lifeline_frame, text="50:50", command=self.use_5050,
                                 bg="#334155", fg="white", width=14)
        self.ll_5050.grid(row=0, column=0, padx=6)

        self.ll_aud = tk.Button(lifeline_frame, text="Audience Poll", command=self.use_audience,
                                bg="#334155", fg="white", width=14)
        self.ll_aud.grid(row=0, column=1, padx=6)

        self.ll_phone = tk.Button(lifeline_frame, text="Phone a Friend", command=self.use_phone,
                                  bg="#334155", fg="white", width=14)
        self.ll_phone.grid(row=0, column=2, padx=6)

        self.ll_flip = tk.Button(lifeline_frame, text="Flip Question", command=self.use_flip,
                                 bg="#334155", fg="white", width=14)
        self.ll_flip.grid(row=0, column=3, padx=6)

        # Bottom controls: money and quit
        bottom = tk.Frame(self.root, bg="#0b1220")
        bottom.pack(pady=10, fill="x")

        self.money_label = tk.Label(bottom, text=f"Current Prize: ₹{self.money}    Safe: ₹{self.safe_money}",
                                    font=("Arial", 14, "bold"), fg="#e6b800", bg="#0b1220")
        self.money_label.pack(side="left", padx=12)

        quit_btn = tk.Button(bottom, text="Quit & Take Money", command=self.quit_game,
                             bg="#d9534f", fg="white", width=18)
        quit_btn.pack(side="right", padx=12)




    def show_question(self):
        # Reset removed options by default (unless 50:50 applied earlier for current question)
        self.removed_options = set()
        if self.current >= len(self.questions):
            messagebox.showinfo("Completed", f"Congratulations! You completed all questions.\nYou take home: ₹{self.money}")
            self.root.destroy()
            return

        q = self.questions[self.current]
        # Mark current question index as used (for flip logic)
        self.used_questions_idx.add(self.current)
        # Update question and options display
        self.q_label.config(text=f"Q{self.current+1}: {q['name']}")
        for i, opt_text in enumerate(q["options"]):
            self.buttons[i].config(text=opt_text, state="normal", bg="#252a34", fg="white")

        # Update money label
        self.money_label.config(text=f"Current Prize: ₹{self.money}    Safe: ₹{self.safe_money}")

        # Disable already-used lifeline buttons
        self.ll_5050.config(state="disabled" if self.lifelines["5050"] else "normal")
        self.ll_aud.config(state="disabled" if self.lifelines["audience"] else "normal")
        self.ll_phone.config(state="disabled" if self.lifelines["phone"] else "normal")
        self.ll_flip.config(state="disabled" if self.lifelines["flip"] else "normal")





    def check_answer(self, idx):
        """Handle answer click. Fixes applied:
           - reward = question's prize (not cumulative add)
           - wrong answer -> player drops to last safe milestone
        """
        q = self.questions[self.current]
        correct_idx = q["answer"] - 1  # CSV uses 1-based answer

        # If option was disabled by 50:50, warn
        if idx in self.removed_options:
            messagebox.showwarning("Removed", "This option was removed by 50:50. Choose another.")
            return

        if idx == correct_idx:
            # CORRECT: set money to this question's prize (not add)
            self.money = q["money"]
            # If this question is a milestone, update safe_money
            if self.current in self.milestones:
                self.safe_money = self.milestones[self.current]

            messagebox.showinfo("Correct!", f"Correct answer!\nYou win ₹{self.money}")
            self.current += 1
            self.show_question()
        else:
            # WRONG: compute guaranteed amount (last safe milestone)
            guaranteed = 0
            for m_idx in sorted(self.milestones):
                if self.current - 1 >= m_idx:
                    guaranteed = self.milestones[m_idx]
            # Player loses down to guaranteed
            self.money = guaranteed
            messagebox.showerror("Wrong Answer",
                                 f"Wrong!\nCorrect was: {q['options'][correct_idx]}\nYou drop to safe level and take home: ₹{self.money}")
            self.root.destroy()

    # ---------------- Lifelines ----------------


    def use_5050(self):
        if self.lifelines["5050"]:
            return messagebox.showwarning("Used", "50:50 already used.")
        self.lifelines["5050"] = True

        q = self.questions[self.current]
        correct = q["answer"] - 1
        wrong_indices = [i for i in range(4) if i != correct]
        disabled = random.sample(wrong_indices, 2)
        self.removed_options = set(disabled)
        for i in disabled:
            self.buttons[i].config(text="", state="disabled")
        messagebox.showinfo("50:50", "Two wrong options removed.")



    def use_audience(self):
        if self.lifelines["audience"]:
            return messagebox.showwarning("Used", "Audience Poll already used.")
        self.lifelines["audience"] = True

        q = self.questions[self.current]
        correct = q["answer"] - 1
        remaining_questions = len(self.questions) - self.current

        # Normal helpful poll for early questions
        if remaining_questions > 3:
            correct_pct = random.randint(40, 70)
            remaining_pct = 100 - correct_pct
            other_indices = [i for i in range(4) if i != correct]
            # distribute remaining_pct among other_indices
            shares = []
            for _ in range(len(other_indices)-1):
                val = random.randint(0, remaining_pct)
                shares.append(val)
                remaining_pct -= val
            shares.append(remaining_pct)
            random.shuffle(shares)

            poll = [0]*4
            poll[correct] = correct_pct
            for i, idx in enumerate(other_indices):
                poll[idx] = shares[i]


        else:
            # MISLEADING poll for last few questions
            correct_pct = random.randint(10, 40)
            # boost one wrong option
            wrong_options = [i for i in range(4) if i != correct]
            misleading = random.choice(wrong_options)
            misleading_pct = random.randint(40, 60)
            leftover = 100 - correct_pct - misleading_pct
            # split leftover among the remaining two options
            remaining_opts = [i for i in range(4) if i not in (correct, misleading)]
            if leftover <= 0:
                # fallback to safe distribution
                poll = [0, 0, 0, 0]
                poll[correct] = max(10, correct_pct)
                poll[misleading] = max(10, misleading_pct)
                for i in remaining_opts:
                    poll[i] = max(0, (100 - poll[correct] - poll[misleading]) // 2)


            else:
                r1 = random.randint(0, leftover)
                r2 = leftover - r1
                poll = [0]*4
                poll[correct] = correct_pct
                poll[misleading] = misleading_pct
                poll[remaining_opts[0]] = r1
                poll[remaining_opts[1]] = r2

        # If options disabled by 50:50, zero them
        for i in range(4):
            if i in self.removed_options:
                poll[i] = 0

        # Show poll
        msg_lines = []
        for i in range(4):
            msg_lines.append(f"Option {i+1}: {self.questions[self.current]['options'][i]}  -->  {poll[i]}%")
        messagebox.showinfo("Audience Poll", "\n".join(msg_lines))

    def use_phone(self):
        if self.lifelines["phone"]:
            return messagebox.showwarning("Used", "Phone a Friend already used.")
        self.lifelines["phone"] = True

        q = self.questions[self.current]
        correct = q["answer"] - 1
        # Friend accuracy declines with difficulty
        if self.current <= 4:
            prob = 0.85
        elif self.current <= 9:
            prob = 0.65
        else:
            prob = 0.45
        if random.random() <= prob:
            suggestion = correct
        else:
            choices = [i for i in range(4) if i != correct and i not in self.removed_options]
            suggestion = random.choice(choices) if choices else correct
        messagebox.showinfo("Phone a Friend", f"Friend suggests Option {suggestion+1}:\n{q['options'][suggestion]}")


    def use_flip(self):
        if self.lifelines["flip"]:
            return messagebox.showwarning("Used", "Flip Question already used.")
        self.lifelines["flip"] = True

        # pick an unused question to swap with current if possible
        unused = [i for i in range(len(self.questions)) if i not in self.used_questions_idx and i != self.current]
        if not unused:
            # fallback to any other question
            unused = [i for i in range(len(self.questions)) if i != self.current]
        new_idx = random.choice(unused)
        # swap
        self.questions[self.current], self.questions[new_idx] = self.questions[new_idx], self.questions[self.current]
        messagebox.showinfo("Flip", "Question flipped. New question displayed.")
        self.show_question()

    def quit_game(self):
        resp = messagebox.askyesno("Quit", f"Do you want to quit and take ₹{self.money}?")
        if resp:
            messagebox.showinfo("Quit", f"You quit the game.\\nTotal Money Won: ₹{self.money}")
            self.root.destroy()





if __name__ == "__main__":
    root = tk.Tk()
    app = KBCGame(root)
    root.mainloop()


