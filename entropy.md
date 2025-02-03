### **What is Entropy?**
**Entropy** measures **uncertainty** or **information gain**. Think of it as a way to quantify "how much you don’t know."  
- **Low entropy** = Less uncertainty (you know a lot).  
- **High entropy** = High uncertainty (you know little).  

In Wordle, **maximizing entropy** means picking a guess that **reduces uncertainty the most**, splitting the remaining possible words into the smallest groups. This is like asking the question that eliminates the most possibilities, no matter the answer.

---

### **Example: Why Entropy > Simple Probability**
Imagine you have **100 possible target words left**.  
You have two candidate guesses: **WORD A** and **WORD B**.  

#### **Case 1: WORD A**  
- When you guess WORD A, the feedback (green/yellow/gray) splits the 100 words into **50 groups of 2 words each**.  
  - Example: Each feedback pattern (e.g., `GXXXY`, `XYGXG`) narrows the list to exactly 2 words.  
- **Entropy** here is **high** because every feedback pattern gives you **maximal information**, cutting the possibilities by half.  

#### **Case 2: WORD B**  
- When you guess WORD B, the feedback splits the 100 words into:  
  - **1 group of 90 words** (common feedback pattern).  
  - **10 groups of 1 word each** (rare patterns).  
- **Entropy** here is **low** because most of the time (90%), you’re stuck with 90 words left.  

#### **Which guess is better?**  
- **WORD A** is better because it guarantees you’ll always narrow the list to 2 words, no matter the feedback.  
- **WORD B** is risky because 90% of the time, you barely reduce the possibilities.  

Entropy rewards guesses that **evenly distribute** remaining words across feedback patterns, minimizing worst-case scenarios.

---

### **Simple Probability vs. Entropy**
1. **Simple Probabilistic Approach**:  
   - Guess words with the **most common letters** (e.g., `E`, `A`, `S`).  
   - Problem: Common letters might overlap in many words, so feedback like gray/yellow doesn’t eliminate many options.  

2. **Entropy Approach**:  
   - Guess words that **split the remaining words into the most balanced groups** based on feedback.  
   - Advantage: Guarantees the **fastest reduction** of uncertainty, even if the word has "uncommon" letters.  

---

### **Real-World Analogy**
Imagine you’re playing "20 Questions":  
- **Bad Question**: "Is it a living thing?" (If yes, you still have millions of options left.)  
- **Good Question**: "Is it a mammal that lives in the ocean?" (Splits possibilities into whales/dolphins vs. others.)  

Entropy is like asking the **"best question"** to narrow down possibilities efficiently.

---