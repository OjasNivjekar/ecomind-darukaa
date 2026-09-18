"""Test conversational memory: initial assessment followed by a follow-up."""
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

from backend.service import run_assessment

INITIAL = (
    "I manage a 2-kilometre stretch of river near a semi-urban area. "
    "The river has experienced declining water levels during summer, and water flow is now intermittent in some sections. "
    "Riparian vegetation has been cleared in several locations for construction, leaving exposed soil along the banks. "
    "Agricultural runoff enters the river during the monsoon, and I have noticed fewer fish, frogs, and aquatic insects over the last five years. "
    "Average summer temperatures are around 34°C. "
    "There is no practical option to increase the river's water supply. "
    "What interventions should be prioritized to improve aquatic biodiversity and river ecosystem health?"
)

FOLLOWUP = (
    "Construction cannot be completely stopped because development is already approved. "
    "Given this constraint, what biodiversity measures can be implemented within the existing river corridor?"
)

SESSION = "test-session-1"

print("=" * 80)
print("STEP 1: Initial assessment")
print("=" * 80)
r1 = run_assessment(INITIAL, {}, SESSION)
print(f"  needs_clarification : {r1.needs_clarification}")
print(f"  clarification_question: {r1.clarification_question}")
print(f"  assessment          : {r1.assessment}")
print(f"  env_data keys       : {list(r1.environmental_data.keys())}")
print(f"  recommendations     : {len(r1.recommendations)}")
for i, rec in enumerate(r1.recommendations):
    print(f"    [{i+1}] {rec.action[:90]}")
print(f"  key_interactions    : {len(r1.key_interactions)}")
for ki in r1.key_interactions:
    print(f"    - {ki[:100]}")

print()
print("=" * 80)
print("STEP 2: Follow-up")
print("=" * 80)
r2 = run_assessment(FOLLOWUP, {}, SESSION)
print(f"  needs_clarification : {r2.needs_clarification}")
print(f"  clarification_question: {r2.clarification_question}")
print(f"  assessment          : {r2.assessment}")
print(f"  env_data keys       : {list(r2.environmental_data.keys())}")
print(f"  recommendations     : {len(r2.recommendations)}")
for i, rec in enumerate(r2.recommendations):
    print(f"    [{i+1}] {rec.action[:90]}")
print(f"  key_interactions    : {len(r2.key_interactions)}")
for ki in r2.key_interactions:
    print(f"    - {ki[:100]}")

print()
print("=" * 80)
print("VERDICT")
print("=" * 80)
if r2.needs_clarification:
    print(f"FAIL: Follow-up asked for clarification: {r2.clarification_question}")
elif "river" not in str(r2.environmental_data).lower():
    print("FAIL: Follow-up lost river context")
elif not any("construction" in str(r2.environmental_data).lower() for _ in [1]):
    print("FAIL: Follow-up did not incorporate construction constraint")
else:
    print("PASS: Follow-up preserved river context and incorporated construction constraint")
    has_corridor_rec = any("corridor" in rec.action.lower() or "construction" in rec.action.lower() or "buffer" in rec.action.lower() or "riparian" in rec.action.lower() for rec in r2.recommendations)
    if has_corridor_rec:
        print("PASS: Recommendations reflect corridor/construction-aware advice")
    else:
        print("INFO: Recommendations present but may not specifically address construction constraint")
