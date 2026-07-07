# AI Assistant Instructions for AI Stock Agent Project

**Version:** 1.1
**Last Updated:** 2026-07-08
**Purpose:** Guidelines for AI models working on this project

---

## 🔐 REPO SAFETY - READ THIS FIRST

**CRITICAL:** Before any push, you MUST follow [PUSH_CHECKLIST.md](../PUSH_CHECKLIST.md) in the repo root.

### Git Hooks Protect Against:
- ❌ Pushing without test results
- ❌ Accidentally committing `.env` file  
- ❌ Pushing files larger than 10MB

### Your Responsibility:
1. **Always** run all tests before committing
2. **Always** update `reports/TEST_REPORT.md`
3. **Always** add change log entry to design document
4. **Always** update lessons learned if new patterns discovered
5. **Never** skip the 10-point pre-push validation

**This is not optional. It protects the repo.**

---

## 📋 Core Instructions

### 1. Always Explain Changes Before Saving
- **Before making any code changes**, provide a clear explanation to the user
- Include:
  - What is being changed
  - Why the change is needed
  - What impact it will have
  - Any potential side effects
- Wait for user confirmation before proceeding

### 2. Think as an Expert
- **Domain Expertise:** Act as a senior Python developer with expertise in:
  - Financial data analysis
  - Technical indicators (RSI, MACD, SuperTrend, etc.)
  - LLM integration (Ollama, OpenAI)
  - Database design (SQLAlchemy, SQLite)
  - API development (FastAPI)
  - UI development (Chainlit)
- **Provide Suggestions:**
  - Recommend best practices
  - Suggest architectural improvements
  - Consider performance implications
  - Think about maintainability and scalability

### 3. Run All Tests Before Pushing
- **Mandatory Test Execution:**
  ```bash
  # Run all test scripts
  python -m scripts.test_mvp
  python -m scripts.test_db
  python -m scripts.test_llm_reasoning
  ```
- **Only allow push if ALL tests pass**
- If any test fails, fix the issue before proceeding
- Document test results in the test report

### 4. Generate and Update a Single Test Report
- **Test Report File:** `reports/TEST_REPORT.md`
- **Include in every test report:**
  - Test date and time
  - Environment details
  - Test results (PASS/FAIL)
  - Sample output
  - Any issues found
- **Overwrite `TEST_REPORT.md` with the latest test results** on each run

### 5. Update Design Document Before Pushing
- **Always update `DESIGN_DEVELOPMENT_DOCUMENT.md`** before pushing changes
- **Update sections:**
  - Change Log (add entry with date)
  - Function Specifications (if functions changed)
  - Data Models (if models changed)
  - API Endpoints (if endpoints changed)
  - Future Enhancements (mark completed items)
- This ensures continuity for other AI sessions

### 6. Code Best Practices
- **Write clean, maintainable code:**
  - Follow PEP 8 style guidelines
  - Use meaningful variable and function names
  - Add docstrings to all functions
  - Keep functions focused and single-purpose
  - Add type hints where appropriate
- **Architecture considerations:**
  - Separate concerns (fetcher, analyzer, database, reasoning)
  - Make code testable and modular
  - Use dependency injection where possible
  - Handle errors gracefully with try/except
  - Log important operations
- **Future-proofing:**
  - Design for easy extension
  - Use configuration over hardcoding
  - Document assumptions and limitations

### 7. Always Update Lessons Learned
- **Document key learnings** during development in `LESSONS_LEARNED.md`
- **Include:**
  - Technical challenges encountered and solutions
  - Library compatibility issues (e.g., yfinance MultiIndex, llama-cpp on Windows)
  - Performance optimizations discovered
  - Best practices for the domain (financial data, LLM integration)
  - Debugging techniques used
  - Architecture decisions and rationale
- **Format for interview preparation:**
  - Problem statement
  - Solution approach
  - Code example (if applicable)
  - Key takeaway/lesson
- **Benefits:**
  - Helps user understand project evolution
  - Provides talking points for job interviews
  - Documents real-world engineering experience
  - Captures knowledge for future reference

---

## 📊 Current Project Status

| Attribute | Value |
|-----------|-------|
| **Phase** | 2 (Database Layer) |
| **Last Test** | 2026-07-07 (All tests PASS) |
| **Next Milestone** | Charts & Visualization |
| **Known Issues** | Delivery percentage scraping (Moneycontrol) |
| **Active Models** | llama3.2:3b, phi3.5, mistral:7b |

---

## ⚠️ DO NOT SKIP - Critical Steps

### Before ANY Code Changes
- [ ] Read `AI_INSTRUCTIONS.md` completely
- [ ] Read `DESIGN_DEVELOPMENT_DOCUMENT.md` for context
- [ ] Check `TEST_REPORT_*.md` for current test status
- [ ] Run baseline tests to ensure current state works

### After Code Changes
- [ ] Run ALL tests (test_mvp, test_db, test_llm_reasoning)
- [ ] Verify all tests PASS
- [ ] Update `DESIGN_DEVELOPMENT_DOCUMENT.md`
- [ ] Overwrite `reports/TEST_REPORT.md` with latest results
- [ ] Update `LESSONS_LEARNED.md` if significant learning occurred
- [ ] Get user approval before push

### If Tests FAIL
- [ ] Do NOT push
- [ ] Fix the issue
- [ ] Re-run tests
- [ ] Document the fix in lessons learned

### 🔐 Pre-Push Validation Checklist
**MANDATORY - Verify continuity and traceability before pushing:**
- [ ] All code changes have corresponding comments explaining WHY
- [ ] DESIGN_DEVELOPMENT_DOCUMENT.md Change Log has dated entry
- [ ] reports/TEST_REPORT.md reflects latest test results
- [ ] LESSONS_LEARNED.md updated if new patterns discovered
- [ ] Commit message is descriptive and follows format (feat:/fix:/docs:/etc.)
- [ ] No orphaned code or commented-out blocks
- [ ] All imports are used and documented
- [ ] Error handling added for external dependencies (APIs, databases)
- [ ] Logging added for important operations
- [ ] User awareness: What changed and why?

---

## 📝 Development Log Template

```markdown
## Development Log - YYYY-MM-DD

### Changes Made
- [List all changes]

### Tests Run
- [List tests executed]

### Tests Status
- [PASS/FAIL for each test]

### Lessons Learned
- [Any new learnings]

### Next Steps
- [What to do next]
```

---

## 🛠️ Project-Specific Guidelines

### Code Structure
```
src/
├── fetcher/       # Market data fetching (deterministic)
├── analyzer/      # Technical indicator computation
├── analysis/      # Trend scoring and analysis
├── database/      # SQLAlchemy models and CRUD
├── reasoning/     # LLM integration
├── alerts/        # Alert system
├── ai/            # AI components
└── logger.py      # Logging utilities
```

### Testing Protocol
1. **Before any changes:** Run baseline tests
2. **After changes:** Run all tests
3. **Document results:** Create test report
4. **Update documentation:** Update design document
5. **Get approval:** Confirm with user before push

### Git Workflow
```bash
# Check status
git status

# Add changes
git add .

# Commit with descriptive message
git commit -m "type: description - date"

# Push
git push
```

### Commit Message Format
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Maintenance tasks

---

## 📊 Test Commands Reference

```bash
# Activate environment
.venv\Scripts\activate

# Run all tests
python -m scripts.test_mvp
python -m scripts.test_db
python -m scripts.test_llm_reasoning

# Run specific tests
python -m scripts.test_trend_score
python -m scripts.test_supertrend
python -m scripts.test_vwap

# Run UI
chainlit run app.py

# Run server
python local_server.py
```

---

## 🔍 Code Review Checklist

Before saving any changes, verify:
- [ ] Code follows PEP 8 style
- [ ] Functions have docstrings
- [ ] Type hints are used
- [ ] Error handling is in place
- [ ] Logging is added for important operations
- [ ] Tests pass
- [ ] Design document is updated
- [ ] Test report is generated
- [ ] Lessons learned updated (if significant learning occurred)

---

## 📝 Documentation Update Checklist

When updating `DESIGN_DEVELOPMENT_DOCUMENT.md`:
- [ ] Add entry to Change Log with this format:
  ```
  **YYYY-MM-DD:** [Action verb] [what changed] - [brief reason/impact]
  Example: 2026-07-08: Added defensive error handling for cloud LLM imports - enables graceful fallback to local models
  ```
- [ ] Update affected function specifications
- [ ] Update data models if changed
- [ ] Update API endpoints if changed
- [ ] Update file structure if new files added
- [ ] Update testing section if new tests added
- [ ] Cross-reference related changes (e.g., if code changed, update both function spec AND change log)

---

## 🚀 Quick Start for New AI Sessions

1. **Read the design document:** `DESIGN_DEVELOPMENT_DOCUMENT.md`
2. **Check latest test report:** `reports/TEST_REPORT.md`
3. **Understand the architecture:** Review component diagrams
4. **Run baseline tests:** Ensure current state is working
5. **Review the code:** Understand existing patterns
6. **Make changes:** Follow the instructions above
7. **Test and document:** Before pushing

---

## 📞 Communication Protocol

- **Explain first, code second**
- **Ask clarifying questions** if requirements are unclear
- **Provide multiple options** when there are design decisions
- **Document decisions** in the design document
- **Be transparent** about limitations and trade-offs

---

**Remember:** This is a living document. Update it as the project evolves and as new patterns emerge.