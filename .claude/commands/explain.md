---
description: "Explain code in a clear, non-technical way"
---

# Explain This Code

## Instructions

You are helping me understand code in a clear, non-technical way. I may not have a strong technical background, so your explanations should be accessible and practical.

### How to Explain

When I use this command, I'll either:
1. Provide a file path to explain
2. Paste code directly
3. Reference code I've selected in my editor

Provide a comprehensive explanation with these sections:

---

## 1. High-Level Summary (Plain English)

**What does this code do?**

Explain in 1-3 sentences what this code accomplishes, using everyday language.

Think of explaining to someone who doesn't code:
- "This code checks if a user is logged in before showing their profile"
- "This function takes a list of numbers and finds the average"
- "This component displays a button that changes color when clicked"

---

## 2. Key Components Breakdown

Break down the main parts:

**Main Function/Component:** [Name]
- **Purpose:** [What it does]
- **Inputs:** [What data it receives]
- **Outputs:** [What it produces/returns]

**Important Variables:**
- `[variable name]` - [What it stores/represents]
- `[variable name]` - [What it stores/represents]

**Key Operations:**
1. [Step 1 in plain language]
2. [Step 2 in plain language]
3. [Step 3 in plain language]

---

## 3. Step-by-Step Walkthrough

Walk through the code flow:

```
When this code runs:

1. First, it [does this]
   → This happens because [reason]

2. Then, it [does this]
   → This is important for [reason]

3. Next, it [does this]
   → This ensures that [outcome]

4. Finally, it [does this]
   → The result is [what the user sees/gets]
```

---

## 4. Visual Analogy (if helpful)

Provide a real-world analogy to help understanding:

"Think of this like [everyday analogy]..."

**Examples:**
- "This function is like a vending machine: you put in money (input), select an item (parameters), and get a snack (output)"
- "This loop is like checking each drawer in a filing cabinet until you find the right document"
- "This conditional is like a bouncer at a club: if you meet the requirements, you get in; otherwise, you're redirected"

---

## 5. Technical Details (Optional)

For those wanting deeper understanding:

**Technical pattern:** [e.g., "This uses the Observer pattern", "This is a closure", "This is a recursive function"]

**Language-specific features:**
- [Feature 1] - [Brief explanation]
- [Feature 2] - [Brief explanation]

**Performance considerations:**
- [Any notable performance aspects]

---

## 6. Potential Issues & Edge Cases

What could go wrong or what to watch out for:

⚠️ **Potential Issues:**
- [Issue 1] - [Why it's a concern]
- [Issue 2] - [Why it's a concern]

🐛 **Bugs or Code Smells:**
- [Any code quality issues]
- [Any security concerns]
- [Any performance problems]

---

## 7. Suggested Improvements (if applicable)

If I notice ways to make this code better:

💡 **Suggestions:**
1. [Improvement 1] - [Why it would help]
2. [Improvement 2] - [Why it would help]

---

## Example Explanation

**Code:**
```javascript
function calculateDiscount(price, customerType) {
  if (customerType === 'premium') {
    return price * 0.8;
  }
  return price * 0.95;
}
```

**Explanation:**

### High-Level Summary
This code calculates how much a customer should pay after a discount. Premium customers get a bigger discount (20% off) than regular customers (5% off).

### Key Components
- **Input 1:** `price` - The original price of the item
- **Input 2:** `customerType` - Whether the customer is 'premium' or regular
- **Output:** The final price after applying the discount

### Step-by-Step
1. The function receives the price and customer type
2. It checks: "Is this a premium customer?"
3. If yes → multiply price by 0.8 (which means 20% off, keeping 80%)
4. If no → multiply price by 0.95 (which means 5% off, keeping 95%)
5. Return the discounted price

### Potential Issues
⚠️ The code assumes customerType will always be 'premium' or something else. If someone passes 'gold' or 'vip', they'd only get the 5% discount.

💡 **Suggestion:** Add more customer types or use a default case to handle unexpected values.

---

## Style Guidelines

**DO:**
- Use plain, everyday language
- Provide concrete examples
- Use analogies when helpful
- Break complex concepts into simple steps
- Highlight important gotchas

**DON'T:**
- Use unexplained jargon
- Assume I know advanced concepts
- Skip over "obvious" parts (they might not be obvious to me)
- Be condescending or overly simplistic

**Tone:**
- Friendly and encouraging
- Educational, not lecture-like
- Assume I'm smart but not technical
- Make me feel capable of understanding

---

## What to Focus On

**Prioritize explaining:**
1. **What** the code does (the outcome)
2. **Why** it does it that way (the reasoning)
3. **How** it works (the mechanism)
4. **When** it runs and under what conditions

**Less emphasis on:**
- Exact syntax details (unless crucial to understanding)
- Every single line (focus on the important parts)
- Language history or alternatives (unless directly relevant)

---

After providing the explanation, ask:

"Does this make sense? Would you like me to:
- Explain any specific part in more detail?
- Show examples of how this would work with real data?
- Compare this to alternative approaches?"
