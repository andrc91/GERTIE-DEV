## URGENT: Fix Made Things Worse
Time: 11:15 AM

### Current Status:
❌ Video streams rep1-rep7: Still white
❌ Still captures rep1-rep7: NOW ALSO WHITE (regression!)
✅ Manual reset: Fixes the issue temporarily
✅ Rep8: Working correctly

### What Went Wrong:
Removing the validation that blocked brightness=0 exposed another bug.
The system is not properly applying brightness on startup.

### Need to investigate:
1. Why brightness=0 isn't being applied at startup
2. Potentially conflicting brightness formulas
3. May need to revert and try different approach
