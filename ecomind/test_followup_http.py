"""Test via HTTP against the fixed FastAPI server on port 8001."""
import sys, io, json, requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

API = "http://127.0.0.1:8001"

INITIAL = (
    "I manage a 2-kilometre stretch of river near a semi-urban area. "
    "The river has experienced declining water levels during summer, and water flow is now intermittent in some sections. "
    "Riparian vegetation has been cleared in several locations for construction, leaving exposed soil along the banks. "
    "Agricultural runoff enters the river during the monsoon, and I have noticed fewer fish, frogs, and aquatic insects over the last five years. "
    "Average summer temperatures are around 34\u00b0C. "
    "There is no practical option to increase the river's water supply. "
    "What interventions should be prioritized to improve aquatic biodiversity and river ecosystem health?"
)

FOLLOWUP = (
    "Construction cannot be completely stopped because development is already approved. "
    "Given this constraint, what biodiversity measures can be implemented within the existing river corridor?"
)

SESSION = "test-http-session-fixed"

def post(query, session_id, env_data=None):
    r = requests.post(f"{API}/api/analyze", json={
        "query": query,
        "environmental_data": env_data or {},
        "session_id": session_id,
    }, timeout=30)
    r.raise_for_status()
    return r.json()

print("=" * 80)
print("STEP 1: Initial assessment via HTTP (port 8001, fixed code)")
print("=" * 80)
r1 = post(INITIAL, SESSION)
print(f"  needs_clarification : {r1['needs_clarification']}")
print(f"  clarification_question: {r1.get('clarification_question')}")
print(f"  reply               : {r1['reply'][:100]}")
print(f"  assessment          : {r1['assessment']}")
print(f"  env_data keys       : {list(r1['environmental_data'].keys())}")
print(f"  recommendations     : {len(r1['recommendations'])}")
for i, rec in enumerate(r1['recommendations']):
    print(f"    [{i+1}] {rec['action'][:90]}")

print()
print("=" * 80)
print("STEP 2: Follow-up via HTTP (same session)")
print("=" * 80)
r2 = post(FOLLOWUP, SESSION)
print(f"  needs_clarification : {r2['needs_clarification']}")
print(f"  clarification_question: {r2.get('clarification_question')}")
print(f"  reply               : {r2['reply'][:100]}")
print(f"  assessment          : {r2['assessment']}")
print(f"  env_data keys       : {list(r2['environmental_data'].keys())}")
print(f"  recommendations     : {len(r2['recommendations'])}")
for i, rec in enumerate(r2['recommendations']):
    print(f"    [{i+1}] {rec['action'][:90]}")

print()
print("=" * 80)
print("VERDICT")
print("=" * 80)

failures = []
if r2['needs_clarification']:
    failures.append(f"Follow-up asked for clarification: {r2.get('clarification_question')}")
if "river" not in str(r2['environmental_data']).lower():
    failures.append("Follow-up lost river context")
if "construction_constraint" not in r2['environmental_data']:
    failures.append("Follow-up did not incorporate construction constraint")
if "ecosystem_type" not in r2['environmental_data'] or r2['environmental_data']['ecosystem_type'] != 'river':
    failures.append("ecosystem_type not preserved as 'river'")

# Check the follow-up reply is NOT the initial boilerplate
if r2['reply'].startswith("I combined your environmental profile"):
    failures.append("Follow-up reply uses initial assessment text instead of follow-up-specific reply")

# Check that recommendation #2 changed to reflect construction constraint
rec2_initial = r1['recommendations'][1]['action'] if len(r1['recommendations']) > 1 else ""
rec2_followup = r2['recommendations'][1]['action'] if len(r2['recommendations']) > 1 else ""
if rec2_initial == rec2_followup:
    print(f"  INFO: Recommendation #2 unchanged between initial and follow-up")
else:
    print(f"  INFO: Recommendation #2 changed:")
    print(f"    Initial : {rec2_initial[:90]}")
    print(f"    Follow-up: {rec2_followup[:90]}")

if failures:
    for f in failures:
        print(f"FAIL: {f}")
else:
    print("PASS: All checks passed")
    print("  - Follow-up preserved river context")
    print("  - Construction constraint incorporated")  
    print("  - No clarification asked on follow-up")
    print("  - Follow-up reply is appropriate")
