---
title: Wordle Assistant
emoji: 🔤
colorFrom: blue
colorTo: purple
sdk: docker
app_file: main.py
pinned: false
---

# Wordle Assistant

An assistant to solve Wordle puzzles by suggesting the best next guess based on your previous guesses and feedback. 
This assistant is designed for targets that are **not historical Wordle answers** (i.e., it has a static vocabulary of 12k allowed guesses excluding the historical answers updated daily).

---

## Entropy-Based Suggestions

Uses information theory to recommend the best next guess. More about [entropy](entropy.md)

---

## How to Use

### 1. **Install Dependencies**
Make sure you have Python installed, then install Mesop:
```bash
pip install -r requirements.txt
```

### 2. **Run the App**
```bash
mesop main.py
```

### 3. **Open the App**
Open your browser and navigate to:
```
http://localhost:32123
```

---

### 4. **Using the Assistant**
1. **Enter Your Guess**:
   - Type your 5-letter guess in the "Your Guess" field (e.g., `CRANE`).

2. **Enter Feedback**:
   - Enter the feedback you received for your guess (e.g., `GXXYX` for 🟩⬛⬛🟨⬛).
   - Use:
     - `G` for green (correct letter in the correct position).
     - `Y` for yellow (correct letter in the wrong position).
     - `X` for gray (letter not in the word).

3. **Submit**:
   - Click the "Submit" button to update the assistant.

4. **View Suggestions**:
   - The assistant will display:
     - The **remaining possible words**.
     - The **top recommended next guess**.

5. **Repeat**:
   - Use the recommended guess in your next Wordle attempt.
   - Enter the new feedback and repeat the process until you solve the puzzle.

---

## Code Overview

### Key Functions
1. **`get_feedback_pattern`**:
   - Simulates Wordle feedback for a given guess and target.

2. **`filter_possible_targets`**:
   - Filters the remaining possible words based on the guess and feedback.

3. **`calculate_entropy`**:
   - Computes the entropy of a candidate word to measure its information gain.

4. **`get_top_suggestion`**:
   - Finds the single best next guess based on entropy.

5. **`handle_submit`**:
   - Updates the state with the new guess and feedback.

---