# 🔐 PUSH CHECKLIST - MANDATORY BEFORE EVERY PUSH

**Every push must follow this checklist. No exceptions.**

---

## 1️⃣ RUN ALL TESTS (Non-Negotiable)

```bash
python -m scripts.test_mvp
python -m scripts.test_db  
python -m scripts.test_llm_reasoning
```

### ❌ STOP IF ANY TEST FAILS
- Fix the issue first
- Re-run tests
- Only proceed if ALL tests PASS ✅

---

## 2️⃣ UPDATE DOCUMENTATION (Required)

- [ ] **reports/TEST_REPORT.md** - Update with today's date and test results
- [ ] **docs/DESIGN_DEVELOPMENT_DOCUMENT.md** - Add change log entry:
  ```
  **YYYY-MM-DD:** [action verb] [what changed] - [why/impact]
  Example: 2026-07-08: Added repo safety layers - prevents bad pushes
  ```
- [ ] **docs/LESSONS_LEARNED.md** - Add if new patterns discovered
- [ ] **docs/QUICK_REFERENCE.md** - Update if commands changed

---

## 3️⃣ PRE-PUSH VALIDATION (10-Point Checklist)

- [ ] All code changes have explanatory comments (WHY, not just WHAT)
- [ ] DESIGN_DEVELOPMENT_DOCUMENT.md has dated change log entry
- [ ] reports/TEST_REPORT.md reflects latest results with today's date
- [ ] LESSONS_LEARNED.md updated if significant learning occurred
- [ ] Commit message follows format: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- [ ] No orphaned code or commented-out blocks
- [ ] All imports are used and documented
- [ ] Error handling added for external dependencies (APIs, databases)
- [ ] Logging added for important operations
- [ ] User is aware: What changed and why?

---

## 4️⃣ GIT OPERATIONS

```bash
git status              # Verify no surprise files
git add .              # Stage all changes
git commit -m "type: description - date"
git push               # Upload to remote
```

---

## 5️⃣ IF TESTS FAIL

❌ **DO NOT PUSH**
- Fix the issue
- Re-run tests  
- Document the fix in LESSONS_LEARNED.md
- Only then commit and push

---

## 🚨 What Could Go Wrong (And How We Prevent It)

| Issue | Prevention |
|-------|-----------|
| Push without running tests | Checklist enforces |
| Missing test report | Checklist enforces |
| .env file accidentally committed | Git hook blocks |
| Large binaries (>10MB) | Git hook blocks |
| Documentation out of sync | Checklist + design doc |
| Future AI forgets steps | Checklist + automated |

---

## 🔗 Related Files

- [docs/AI_INSTRUCTIONS.md](docs/AI_INSTRUCTIONS.md)
- [docs/DESIGN_DEVELOPMENT_DOCUMENT.md](docs/DESIGN_DEVELOPMENT_DOCUMENT.md)
- [reports/TEST_REPORT.md](reports/TEST_REPORT.md)
- [docs/LESSONS_LEARNED.md](docs/LESSONS_LEARNED.md)

---

**Remember:** This is not optional. It protects the repo.
