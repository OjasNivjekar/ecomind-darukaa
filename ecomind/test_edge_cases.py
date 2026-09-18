"""Test edge case: follow-up on a session that has no prior state (simulates server restart).
With the fix, this should NOT ask for clarification since the follow-up query
mentions 'construction' but not soil_organic_carbon/rainfall. However, without
a prior initial assessment, it won't have the full river context either.

The key fix is: a true follow-up (same session, initial_complete=True) will
never trigger the clarification flow, even if the follow-up query alone
doesn't mention enough fields.
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

from backend.service import run_assessment, _sessions

FOLLOWUP = (
    "Construction cannot be completely stopped because development is already approved. "
    "Given this constraint, what biodiversity measures can be implemented within the existing river corridor?"
)

# Test 1: Fresh session with only the follow-up (no initial assessment)
print("=" * 80)
print("TEST 1: Follow-up only, no prior initial assessment (fresh session)")
print("=" * 80)
r = run_assessment(FOLLOWUP, {}, "orphan-session")
print(f"  needs_clarification: {r.needs_clarification}")
print(f"  clarification_question: {r.clarification_question}")
print(f"  env_data: {r.environmental_data}")
print()
if r.needs_clarification:
    print("  EXPECTED: This is a fresh session with no context, clarification is correct.")
else:
    print("  NOTE: No clarification asked (the follow-up extracted enough fields on its own).")

# Test 2: Simulate the bug scenario - initial assessment works, then server restart, then follow-up
print()
print("=" * 80)
print("TEST 2: Initial assessment -> clear sessions (simulate restart) -> follow-up")
print("=" * 80)
INITIAL = (
    "I manage a 2-kilometre stretch of river near a semi-urban area. "
    "The river has experienced declining water levels during summer, and water flow is now intermittent in some sections. "
    "Riparian vegetation has been cleared in several locations for construction, leaving exposed soil along the banks. "
    "Agricultural runoff enters the river during the monsoon, and I have noticed fewer fish, frogs, and aquatic insects over the last five years. "
    "Average summer temperatures are around 34\u00b0C. "
    "There is no practical option to increase the river's water supply. "
    "What interventions should be prioritized to improve aquatic biodiversity and river ecosystem health?"
)

r1 = run_assessment(INITIAL, {}, "restart-session")
print(f"  Initial: needs_clarification={r1.needs_clarification}, assessment={r1.assessment}")

# Simulate server restart by clearing the session
_sessions.clear()
print("  >>> Cleared all sessions (simulating server restart)")

r2 = run_assessment(FOLLOWUP, {}, "restart-session")
print(f"  Follow-up: needs_clarification={r2.needs_clarification}")
print(f"  Follow-up clarification: {r2.clarification_question}")
print(f"  Follow-up env_data: {r2.environmental_data}")
print()
if r2.needs_clarification:
    print("  BUG CONFIRMED: After server restart, follow-up is treated as new assessment")
    print("  and asks for soil organic carbon/rainfall because the session context was lost.")
    print("  NOTE: This is the original bug the user reported. The in-memory session fix helps")
    print("  within a single server lifetime, but server restarts will still lose context.")
    print("  The fix ensures that within a running server, follow-ups always work correctly.")
else:
    print("  Follow-up works even after session clear (query extracted enough fields).")
