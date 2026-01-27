---
description: "Thorough code review with actionable feedback"
---

# Code Review

## Context

**Files changed:**
${{ git diff --name-only }}

**Full diff:**
${{ git diff }}

**Staged changes:**
${{ git diff --cached }}

**Current branch:**
${{ git branch --show-current }}

---

## Instructions

You are conducting a thorough code review. Review all changes shown above and provide structured, actionable feedback.

### Review Categories

Examine the code across these dimensions:

#### 1. Correctness
- Are there any bugs or logic errors?
- Do edge cases get handled properly?
- Are there off-by-one errors, null/undefined issues?
- Does the code do what it's supposed to do?

#### 2. Readability & Maintainability
- Is the code easy to understand?
- Are variable and function names clear and descriptive?
- Is the logic well-organized?
- Would another developer understand this in 6 months?
- Are there overly complex sections that could be simplified?

#### 3. Performance
- Are there obvious performance problems?
- Unnecessary loops or redundant operations?
- Memory leaks or resource management issues?
- Could large datasets cause problems?

#### 4. Security
- Any SQL injection vulnerabilities?
- XSS (Cross-Site Scripting) risks?
- Exposed secrets or credentials?
- Proper input validation and sanitization?
- Authentication/authorization correctly implemented?

#### 5. Best Practices
- Does it follow the language/framework conventions?
- Are errors handled appropriately?
- Proper use of async/await, promises, or similar?
- Following the project's coding standards (check CONTEXT.md)?
- DRY (Don't Repeat Yourself) principle followed?

#### 6. Testing
- Are there tests for the new/changed code?
- Are edge cases tested?
- Is test coverage adequate?
- Are tests clear and maintainable?

---

## Review Format

Provide feedback in this structured format:

### Summary

**Overall Assessment:** [One sentence summary]
**Changed files:** [Number] files modified
**Risk Level:** [Low / Medium / High]

---

### Critical Issues 🔴

**Must be fixed before merging.**

#### Issue: [Brief description]
**Location:** `[file]:[line]`
**Problem:** [What's wrong and why it's critical]
**Impact:** [What could happen if not fixed]
**Solution:**
```[language]
// Suggested fix
[code here]
```
**Why this is better:** [Explanation]

---

### Suggestions 🟡

**Would improve the code, but not blocking.**

#### Suggestion: [Brief description]
**Location:** `[file]:[line]`
**Current approach:** [What the code does now]
**Improvement:** [What could be better]
**Benefit:** [Why this matters]
**Example:**
```[language]
// Suggested improvement
[code here]
```

---

### Nice to Have 🟢

**Minor polish, optional improvements.**

#### Polish: [Brief description]
**Location:** `[file]:[line]`
**Note:** [Minor improvement or style suggestion]

---

### Positive Feedback ✅

**What's done well (be specific!):**

- ✅ [Specific thing done well - file/line reference]
- ✅ [Another good practice observed]
- ✅ [Well-handled edge case or pattern]

---

### Questions & Clarifications ❓

**Things I'm unsure about:**

- ❓ [Question about intent or approach]
- ❓ [Request for clarification]

---

## Review Guidelines

### Be Constructive
- Focus on the code, not the person
- Explain the "why" behind every suggestion
- Offer solutions, not just criticism
- Acknowledge good practices when you see them

### Be Specific
- Reference exact file names and line numbers
- Provide code examples for suggestions
- Explain the impact of each issue

### Be Practical
- Distinguish between critical issues and nice-to-haves
- Consider the context (is this a prototype or production code?)
- Don't nitpick style if there are bigger issues
- Prioritize security and correctness over style

### Be Clear
- Use simple language
- Avoid jargon when possible
- Provide examples to illustrate points

---

## Priority Levels Explained

🔴 **Critical - Must Fix:**
- Security vulnerabilities
- Data loss or corruption risks
- Breaking changes to APIs
- Severe performance problems
- Logic errors that cause incorrect behavior

🟡 **Suggestion - Should Consider:**
- Code readability issues
- Missing error handling
- Inefficient but functional code
- Inconsistent patterns
- Missing tests for important features

🟢 **Nice to Have - Optional:**
- Minor style inconsistencies
- Additional comments
- More descriptive variable names
- Small optimizations

---

## Special Checks

### Security Checklist
- [ ] No hardcoded secrets or credentials
- [ ] User input is validated and sanitized
- [ ] SQL queries use parameterization (no string concatenation)
- [ ] Authentication/authorization properly implemented
- [ ] Sensitive data is encrypted
- [ ] HTTPS enforced where needed
- [ ] CORS configured correctly

### Code Quality Checklist
- [ ] Functions are small and focused (single responsibility)
- [ ] No commented-out code (remove it, git has the history)
- [ ] No TODO comments without tickets/issues
- [ ] Error messages are helpful and actionable
- [ ] Logging is appropriate (not too much, not too little)
- [ ] No console.log in production code

### Git Hygiene Checklist
- [ ] No unrelated changes mixed in
- [ ] No merge conflicts
- [ ] No debug code left behind
- [ ] No accidentally committed files (.env, node_modules, etc.)

---

## Example Review

**File:** `src/auth.js`

### Summary
Overall Assessment: Good implementation with a few security concerns and readability improvements needed.
Changed files: 3 files modified
Risk Level: Medium

---

### Critical Issues 🔴

#### Issue: SQL Injection Vulnerability
**Location:** `auth.js:45`
**Problem:** User input is directly concatenated into SQL query
**Impact:** Attackers could inject malicious SQL and access/delete data
**Solution:**
```javascript
// Current (vulnerable):
db.query(`SELECT * FROM users WHERE email = '${email}'`)

// Fixed:
db.query('SELECT * FROM users WHERE email = ?', [email])
```
**Why this is better:** Parameterized queries prevent SQL injection by treating user input as data, not code.

---

### Suggestions 🟡

#### Suggestion: Add error handling
**Location:** `auth.js:67`
**Current approach:** No try-catch, errors crash the app
**Improvement:** Wrap in try-catch and return meaningful error
**Benefit:** Better user experience and easier debugging
**Example:**
```javascript
try {
  const user = await authenticate(email, password);
  return user;
} catch (error) {
  logger.error('Authentication failed:', error);
  throw new Error('Invalid credentials');
}
```

---

### Positive Feedback ✅
- ✅ Password hashing using bcrypt - excellent security practice (auth.js:23)
- ✅ Clear function names that describe what they do
- ✅ Good test coverage for happy path scenarios

---

## After Review

Once I've completed the review, I'll ask:

"Would you like me to:
1. Fix the critical issues automatically?
2. Explain any feedback in more detail?
3. Review again after you make changes?
4. Focus on a specific aspect (security, performance, etc.)?"

---

## Notes

- If the diff is empty, I'll let you know and ask what you'd like me to review
- For large changes (>500 lines), I'll ask if you want me to focus on specific files
- I'll check CONTEXT.md for project-specific rules and preferences
- I'll consider the context: proof-of-concept code gets different scrutiny than production code
