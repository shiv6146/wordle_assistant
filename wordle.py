import math
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd

# Load the list of valid Wordle words
WORDLE_WORDS = pd.read_csv('wordle_words.csv')['wordle_words']

class WordleVisualizer:
    def __init__(self):
        self.attempt_history = []
        self.entropy_history = []
        self.targets_history = []
        
    def update(self, attempt, entropy_data, remaining_targets):
        """Store data for visualization"""
        self.attempt_history.append(attempt)
        self.entropy_history.append(entropy_data)
        self.targets_history.append(len(remaining_targets))
        
    def plot(self):
        """Generate insight plots"""
        plt.figure(figsize=(12, 6))
        
        # Plot 1: Entropy distribution
        plt.subplot(1, 2, 1)
        for i, (candidates, entropies) in enumerate(self.entropy_history):
            plt.scatter([i+1]*len(entropies), entropies, alpha=0.5, label=f'Attempt {i+1}')
        plt.title('Entropy Distribution per Attempt')
        plt.xlabel('Attempt Number')
        plt.ylabel('Entropy (bits)')
        plt.xticks(range(1, len(self.attempt_history)+1))
        
        # Plot 2: Possible targets reduction
        plt.subplot(1, 2, 2)
        plt.plot(self.attempt_history, self.targets_history, 'bo-')
        plt.title('Possible Targets Reduction')
        plt.xlabel('Attempt Number')
        plt.ylabel('Remaining Targets')
        plt.xticks(self.attempt_history)
        plt.yscale('log')
        
        plt.tight_layout()
        plt.savefig('wordle_analysis.png')
        plt.close()
        print("\nVisualization saved as 'wordle_analysis.png'")

def get_feedback(guess, target):
    """Simulates Wordle feedback (for testing)"""
    feedback = ['X'] * 5
    target_counts = defaultdict(int)
    for char in target:
        target_counts[char] += 1

    # First pass for green letters
    for i, (g_char, t_char) in enumerate(zip(guess, target)):
        if g_char == t_char:
            feedback[i] = 'G'
            target_counts[g_char] -= 1

    # Second pass for yellow letters
    for i, g_char in enumerate(guess):
        if feedback[i] == 'X' and target_counts.get(g_char, 0) > 0:
            feedback[i] = 'Y'
            target_counts[g_char] -= 1

    return ''.join(feedback)

def filter_words(words, green, yellow, gray):
    """Filters words based on feedback"""
    filtered = []
    for word in words:
        valid = True
        # Check green constraints
        for pos, char in green.items():
            if word[pos] != char:
                valid = False
        # Check yellow constraints
        for char, positions in yellow.items():
            if char not in word:
                valid = False
            for pos in positions:
                if word[pos] == char:
                    valid = False
        # Check gray constraints
        for char in gray:
            if char in word:
                valid = False
        if valid:
            filtered.append(word)
    return filtered

def calculate_entropy(candidate, possible_targets):
    """Calculates entropy for a candidate word"""
    pattern_counts = defaultdict(int)
    for target in possible_targets:
        pattern = get_feedback(candidate, target)
        pattern_counts[pattern] += 1
    entropy = 0.0
    total = len(possible_targets)
    for count in pattern_counts.values():
        p = count / total
        entropy -= p * math.log2(p) if p > 0 else 0
    return entropy

def get_best_guess(possible_targets, candidates, visualizer, attempt):
    """Finds the candidate with the highest entropy and records entropy data"""
    entropy_data = []
    candidates_to_show = min(10, len(candidates))  # Show top 10 candidates
    
    # Calculate entropy for all candidates
    entropy_values = []
    for word in candidates:
        entropy = calculate_entropy(word, possible_targets)
        entropy_values.append((entropy, word))
    
    # Sort by entropy and get top candidates
    entropy_values.sort(reverse=True, key=lambda x: x[0])
    top_candidates = [w for _, w in entropy_values[:candidates_to_show]]
    top_entropies = [e for e, _ in entropy_values[:candidates_to_show]]
    
    # Record data for visualization
    visualizer.update(attempt, 
                     (top_candidates, top_entropies),
                     possible_targets)
    
    return entropy_values[0][1]

def play_wordle_cli():
    """CLI interaction loop with visualization"""
    possible_targets = WORDLE_WORDS.copy()
    visualizer = WordleVisualizer()
    attempts = 0
    green = {}
    yellow = defaultdict(set)
    gray = set()

    print("Think of a 5-letter word. The AI will try to guess it!")
    print("Enter feedback as a 5-character string (G=Green, Y=Yellow, X=Gray).")

    while attempts < 6 and len(possible_targets) > 0:
        # Get AI's guess with entropy tracking
        candidates = possible_targets if len(possible_targets) <= 100 else WORDLE_WORDS
        best_guess = get_best_guess(possible_targets, candidates, visualizer, attempts+1)
        print(f"\nAI's guess {attempts + 1}/6: {best_guess.upper()}")

        # Get user feedback
        while True:
            feedback = input("Your feedback (G/Y/X, e.g., GXXYX): ").strip().upper()
            if len(feedback) == 5 and all(c in {'G', 'Y', 'X'} for c in feedback):
                break
            print("Invalid feedback. Use 5 characters (G/Y/X).")

        if feedback == 'GGGGG':
            print("\nAI won! 🎉")
            visualizer.plot()
            return

        # Update constraints
        for i, fb in enumerate(feedback):
            char = best_guess[i]
            if fb == 'G':
                green[i] = char
            elif fb == 'Y':
                yellow[char].add(i)
            elif fb == 'X':
                gray.add(char)

        # Filter possible targets
        possible_targets = filter_words(possible_targets, green, yellow, gray)
        attempts += 1

    print("\nAI lost. 😢 Possible targets:", [w.upper() for w in possible_targets])
    visualizer.plot()

if __name__ == "__main__":
    play_wordle_cli()