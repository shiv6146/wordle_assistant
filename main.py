import mesop as me
import math
from collections import defaultdict
import pandas as pd
from dataclasses import field
import requests
from bs4 import BeautifulSoup

INTRO = '''
# Wordle Assistant

An assistant to solve Wordle puzzles by suggesting the best next guess based on your previous guesses and feedback. 
This assistant is designed for targets that are **not historical Wordle answers** (i.e., it has a static vocabulary of 12k allowed guesses excluding the historical answers updated daily).

---

'''

USING = '''
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

'''

def get_wordle_words():
   # URL of the webpage to scrape
	url = 'https://www.wordunscrambler.net/word-list/wordle-word-list'

	# Send a GET request to the webpage
	response = requests.get(url)
	response.raise_for_status()  # Ensure the request was successful

	# Parse the webpage content
	soup = BeautifulSoup(response.text, 'html.parser')

	# Find all sections that start with "Wordle Words List Starting With"
	sections = soup.find_all('h3', string=lambda text: text and text.startswith('Wordle Words List Starting With'))

	# Initialize a list to store the words
	wordle_words = []

	# Iterate through each section
	for section in sections:
		# The next sibling tag after <h3> is the <ul> containing the words
		ul_tag = section.find_next_sibling('ul')
		if ul_tag:
			# Find all <li> tags within the <ul>
			li_tags = ul_tag.find_all('li')
			# Extract and store the word from each <li> tag
			for li in li_tags:
				word = li.get_text(strip=True)
				wordle_words.append(word)
	
	return wordle_words


ANSWER_WORDS = get_wordle_words()  # Historical answers
ALLOWED_GUESSES = list(pd.read_csv('https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt', header=None)[0])  # Allowed guesses
possible_targets_initial = list(set(ALLOWED_GUESSES) - set(ANSWER_WORDS))

@me.stateclass
class State:
    possible_targets: list[str] = field(default_factory=lambda: [*possible_targets_initial.copy()])
    previous_guesses: list[str]
    feedback_history: list[str]
    current_guess: str = ""
    current_feedback: str = ""

@me.page(
  security_policy=me.SecurityPolicy(
    allowed_iframe_parents=[
      'https://shiva6146-wordle-assistant.hf.space',
    ]
  )
)

def load(e: me.LoadEvent):
	me.set_theme_mode("system")

def get_feedback_pattern(guess: str, target: str) -> str:
    # (Keep the same implementation as before)
    feedback = ['X'] * 5
    target_counts = defaultdict(int)
    for c in target:
        target_counts[c] += 1
    # Green pass
    for i, (g, t) in enumerate(zip(guess, target)):
        if g == t:
            feedback[i] = 'G'
            target_counts[g] -= 1
    # Yellow pass
    for i, g in enumerate(guess):
        if feedback[i] == 'X' and target_counts.get(g, 0) > 0:
            feedback[i] = 'Y'
            target_counts[g] -= 1
    return ''.join(feedback)

def filter_possible_targets(guess: str, feedback: str, possible_targets: list[str]):
  filtered = []
  for word in possible_targets:
    valid = True
    target_counts = defaultdict(int)
    for c in word:
      target_counts[c] += 1
    # Check greens
    for i, (g, fb) in enumerate(zip(guess, feedback)):
      if fb == 'G':
        if word[i] != g:
          valid = False
        else:
          target_counts[g] -= 1
    # Check yellows
    if valid:
      for i, (g, fb) in enumerate(zip(guess, feedback)):
        if fb == 'Y':
          if g not in word or word[i] == g or target_counts[g] <= 0:
            valid = False
          else:
            target_counts[g] -= 1
    # Check grays
    if valid:
      gray_chars = [g for g, fb in zip(guess, feedback) if fb == 'X']
      for g in gray_chars:
        total_gy = sum(1 for gr, f in zip(guess, feedback) if gr == g and f in ['G', 'Y'])
        if word.count(g) > total_gy:
          valid = False
          break
    if valid:
      filtered.append(word)
  return filtered

def calculate_entropy(candidate: str, possible_targets: tuple[str, ...]):
    pattern_counts = defaultdict(int)
    for target in possible_targets:
        pattern = get_feedback_pattern(candidate, target)
        pattern_counts[pattern] += 1
    entropy = 0.0
    total = len(possible_targets)
    for count in pattern_counts.values():
        p = count / total
        entropy -= p * math.log2(p) if p > 0 else 0
    return entropy

def get_top_suggestion(possible_targets: tuple[str, ...], previous_guesses: tuple[str, ...]):
    candidates = [word for word in ALLOWED_GUESSES if word not in previous_guesses]
    if len(possible_targets) <= 15:
        candidates = [word for word in candidates if word in possible_targets]
    
    # Find the single best candidate
    best_entropy = -1
    best_word = ""
    for word in candidates[:500]:  # Limit for performance
        entropy = calculate_entropy(word, possible_targets)
        if entropy > best_entropy:
            best_entropy = entropy
            best_word = word
    return best_word

@me.page(on_load=load, path="/", title="Wordle Assistant")
def app():
    state = me.state(State)

    with me.box(style=me.Style(padding=me.Padding.all(16), border=me.Border.all(
            me.BorderSide(width=1, style="solid", color="#ddd")
        ))):
        me.markdown(INTRO)
        with me.expansion_panel(key="usage",title="How to use the assistant?",description="",icon="",):
            me.markdown(USING)
        with me.box(style=me.Style(display="flex",
        flex_direction="row", margin=me.Margin(top=16))):
            me.input(
                label="Your Guess",
                on_blur=lambda e: setattr(state, "current_guess", e.value.lower()),
                style=me.Style(width="200px")
            )
            me.input(
                label="Feedback (G/Y/X)",
                on_blur=lambda e: setattr(state, "current_feedback", e.value.upper()),
                style=me.Style(width="200px")
            )
        me.button(
            "Submit",
            on_click=handle_submit,
            style=me.Style(margin=me.Margin(top=16))
        )

    if state.previous_guesses:
        with me.box(style=me.Style(padding=me.Padding.all(8), margin=me.Margin(top=32))):
            me.text("Game History:", type="headline-6")
            for guess, feedback in zip(state.previous_guesses, state.feedback_history):
                me.text(f"{guess.upper()} → {feedback}", type="body-1")

    if state.possible_targets:
        with me.box(style=me.Style(padding=me.Padding.all(8), margin=me.Margin(top=32))):
            me.text(f"Remaining Possible Words: {len(state.possible_targets)}", type="body-1")
            if len(state.possible_targets) <= 20:
                me.text("Possible options: " + ", ".join(state.possible_targets).upper())
            
            suggestion = get_top_suggestion(state.possible_targets, state.previous_guesses)
            if suggestion:
                me.text("Recommended Next Guess:", type="headline-6")
                me.text(suggestion.upper(), type="subtitle-1", style=me.Style(
                    font_size="24px",
                    color="#2ecc71",
                    margin=me.Margin(top=8)
                ))

def handle_submit(event: me.ClickEvent):
    state = me.state(State)
    # Validate input
    feedback = state.current_feedback.upper()
    if not all(c in {'G', 'Y', 'X'} for c in feedback):
        return

    # Update guesses and feedback history
    state.previous_guesses.append(state.current_guess.lower())
    state.feedback_history.append(feedback)
    state.possible_targets = filter_possible_targets(
        state.current_guess.lower(),
        feedback,
        state.possible_targets
    )

    # Reset input fields
    state.current_guess = ""
    state.current_feedback = ""