#  Evaluation Mapping — AI PR Reviewer

## Scoring Logic
Each finding contributes to the overall score based on severity.

| Severity | Weight | Deduction |
|-----------|---------|-----------|
| Low | 1 | -1 point |
| Medium | 2 | -3 points |
| High | 3 | -6 points |

Final Score = 100 - Σ(deductions)

## Example
| File | Issue | Severity | Deduction |
|------|--------|-----------|------------|
| app/routes.py | Unused import | Low | -1 |
| core/auth.py | Hardcoded token | High | -6 |

Total deductions: 7  
**Final Score: 93**

## Additional Metrics
- Findings count
- Severity ratio (High/Total)
- AI agreement with static check (% match)
