# VPR v8.1 Enhancement Plan

**Date:** November 5, 2025  
**Status:** ✅ COMPLETE  
**Goal:** Add tactical intelligence and phase awareness while maintaining speed

---

## 🎯 Objectives

VPR v8.1 will add four critical heuristics to give the engine strategic awareness and V7P3R's personality:

1. ✅ **Time Management** - Already exists from Material Opponent
2. 🔨 **Game Phase Detection** - Lightweight opening/middlegame/endgame detection
3. 🔨 **Phase-Aware Time Allocation** - Adjust thinking time based on game phase
4. 🔨 **Phase-Aware Trade Evaluation** - Intelligent capture decisions using SEE

---

## 📋 Technical Specifications

### 1. Game Phase Detection

**Implementation (V14.3 Conservative Approach):**
```python
class GamePhase(Enum):
    OPENING = 0      # Move < 6 AND material >= 5500
    MIDDLEGAME = 1   # Default phase (safer fallback)
    ENDGAME = 2      # Material <= 2000

def _detect_game_phase(board: chess.Board) -> GamePhase:
    """
    Conservative phase detection with safer defaults
    
    Uses total material value instead of piece count
    AND logic for opening (stricter)
    Defaults to middlegame when uncertain
    """
    total_material = calculate_total_material(board)
    moves_played = len(board.move_stack)
    
    if moves_played < 6 and total_material >= 5500:
        return GamePhase.OPENING  # Strict: both conditions required
    elif total_material <= 2000:
        return GamePhase.ENDGAME  # Clear endgame
    else:
        return GamePhase.MIDDLEGAME  # Safe default
```

**Rationale:**
- **V14.3 Battle-Tested**: This approach was designed to fix V7P3R v14.2's phase detection issues
- **Conservative AND Logic**: Requires both move < 6 AND high material for opening (vs OR)
- **Total Material**: More accurate than piece counting (accounts for piece values)
- **Middlegame Default**: Safer fallback when uncertain
- **Simpler**: Fewer branches, easier to understand and maintain
- **Performance Impact: <1%** (cached, simple math)

---

### 2. Phase-Aware Time Management

**Current Implementation (Material Opponent):**
```python
if time_left > 1800:   return time_left / 40 + increment * 0.8
elif time_left > 600:  return time_left / 30 + increment * 0.8
elif time_left > 60:   return time_left / 20 + increment * 0.8
else:                  return time_left / 10 + increment * 0.8
```

**Enhanced Implementation:**
```python
# Get game phase first
phase = self._detect_game_phase(self.board)

# Phase-dependent time allocation
if phase == GamePhase.OPENING:
    # Opening: Move faster, less critical decisions
    base_divisor = 50
elif phase == GamePhase.MIDDLEGAME:
    # Middlegame: Think longer, critical tactical battles
    base_divisor = 30
else:  # ENDGAME
    # Endgame: Precision needed but simpler positions
    base_divisor = 40

# Apply base divisor with time pressure adjustments
if time_left > 1800:
    return min(time_left / base_divisor + increment * 0.8, 30)
elif time_left > 600:
    return min(time_left / (base_divisor * 0.9) + increment * 0.8, 20)
elif time_left > 60:
    return min(time_left / (base_divisor * 0.7) + increment * 0.8, 10)
else:
    return min(time_left / (base_divisor * 0.5) + increment * 0.8, 5)
```

**Philosophy:**
- **Opening**: Fast moves, save time, theory-heavy positions
- **Middlegame**: Deep calculation, tactical complexity
- **Endgame**: Precise but faster (fewer pieces = simpler)

**Performance Impact: 0%** (same function, just smarter)

---

### 3. Static Exchange Evaluation (SEE)

**Purpose:** Calculate the material outcome of a capture sequence

**Implementation (adapted from CaptureOpponent):**
```python
def _static_exchange_evaluation(board: chess.Board, move: chess.Move) -> int:
    """
    Calculate material outcome of capture sequence on target square
    
    Returns:
        Net material gain/loss in centipawns (positive = we gain)
    """
    if not board.is_capture(move):
        return 0
    
    # Get initial victim value
    victim = board.piece_at(move.to_square)
    victim_value = PIECE_VALUES[victim.piece_type] if victim else 100  # en passant
    
    # Get attacker value
    attacker = board.piece_at(move.from_square)
    attacker_value = PIECE_VALUES[attacker.piece_type]
    
    # Make the capture
    board.push(move)
    target_square = move.to_square
    gain = [victim_value]
    
    # Simulate exchange sequence
    current_attacker_value = attacker_value
    
    while True:
        # Find smallest attacker that can recapture
        smallest_attacker = None
        smallest_value = float('inf')
        
        for recapture in board.legal_moves:
            if recapture.to_square == target_square:
                piece = board.piece_at(recapture.from_square)
                if piece:
                    piece_value = PIECE_VALUES[piece.piece_type]
                    if piece_value < smallest_value:
                        smallest_value = piece_value
                        smallest_attacker = recapture
        
        if smallest_attacker is None:
            break
        
        gain.append(current_attacker_value)
        current_attacker_value = smallest_value
        board.push(smallest_attacker)
    
    # Restore board state
    for _ in range(len(gain) - 1):
        board.pop()
    board.pop()
    
    # Minimax the gain list
    if len(gain) == 1:
        return gain[0]
    
    for i in range(len(gain) - 1, 0, -1):
        gain[i - 1] = max(gain[i - 1] - gain[i], 0)
    
    return gain[0]
```

**Optimization Note:**
- Only called during move ordering (NOT during evaluation)
- Only called for capture moves
- Cached results with move hash
- **Performance Impact: ~2-3%** (only in move ordering)

---

### 4. Phase-Aware Trade Evaluation

**Implementation:**
```python
def _evaluate_trade(board: chess.Board, move: chess.Move, phase: GamePhase) -> bool:
    """
    Evaluate if a capture is tactically sound based on game phase
    
    Returns:
        True if trade should be prioritized in move ordering
    """
    if not board.is_capture(move):
        return False
    
    # Calculate SEE
    see_value = self._static_exchange_evaluation(board, move)
    
    # Phase-dependent trade acceptance
    if phase == GamePhase.OPENING:
        # Opening: Accept trades losing up to 1 pawn (simplification)
        # Rationale: Simplify position, save time, reduce complexity
        return see_value >= -100
        
    elif phase == GamePhase.MIDDLEGAME:
        # Middlegame: Only accept advantageous trades (strict)
        # Rationale: Critical phase, maximize material advantage
        return see_value >= 0
        
    else:  # ENDGAME
        # Endgame: Accept equal trades (convert advantages)
        # Rationale: Trade pieces when ahead, simplify to winning endgames
        material_balance = self._evaluate_material(board)
        
        if material_balance > 200:  # We're ahead
            return see_value >= -50  # Accept equal trades
        else:
            return see_value >= 0  # Be careful when behind
```

**Trade Examples:**

| Trade | SEE Value | Opening | Middlegame | Endgame (ahead) | Endgame (behind) |
|-------|-----------|---------|------------|-----------------|------------------|
| Q for 2R | -100 | ✅ Accept | ❌ Reject | ✅ Accept | ❌ Reject |
| R for B+N | 0 | ✅ Accept | ✅ Accept | ✅ Accept | ✅ Accept |
| N for 3P | 0 | ✅ Accept | ✅ Accept | ✅ Accept | ✅ Accept |
| Q for 3P | -600 | ❌ Reject | ❌ Reject | ❌ Reject | ❌ Reject |
| B for N | -25 | ✅ Accept | ❌ Reject | ✅ Accept | ❌ Reject |

**Performance Impact: <1%** (uses cached SEE result)

---

### 5. Enhanced Move Ordering

**Modified Priority:**
```python
1. TT move (from transposition table)
2. Checkmate threats
3. Checks
4. GOOD CAPTURES (passing phase-aware trade evaluation) ← NEW!
5. BAD CAPTURES (failing trade evaluation, but still tries) ← NEW!
6. Killer moves
7. Promotions
8. Pawn advances
9. History heuristic
10. Other moves
```

**Implementation Changes:**
```python
def _order_moves(...):
    for move in moves:
        # ... existing TT, checkmate, check logic ...
        
        elif board.is_capture(move):
            phase = self._detect_game_phase(board)
            
            if self._evaluate_trade(board, move, phase):
                # Good capture: high priority
                score = CAPTURE_BONUS + self._mvv_lva_score(board, move) + 100000
            else:
                # Bad capture: lower priority (but still above quiet moves)
                score = CAPTURE_BONUS + self._mvv_lva_score(board, move)
        
        # ... rest of move ordering ...
```

**Rationale:**
- Good captures examined first (likely to cause beta cutoffs)
- Bad captures still examined (might be forced/only moves)
- Separation improves alpha-beta pruning efficiency

---

## 📊 Performance Budget

| Component | Lines of Code | Performance Impact | Benefit |
|-----------|---------------|-------------------|---------|
| Game Phase Detection | ~20 | <1% (cached) | High |
| Phase-Aware Time Mgmt | ~15 | 0% (same logic) | High |
| SEE Implementation | ~60 | 2-3% (move ordering only) | Very High |
| Trade Evaluation | ~25 | <1% (uses SEE cache) | High |
| Enhanced Move Ordering | ~10 | 0% (reorders existing) | High |
| **TOTAL** | **~130 lines** | **<5%** | **V7P3R DNA** |

---

## 🎯 Success Criteria

### Must Achieve:
- [ ] NPS maintained > 16,000 (within 10% of v8.0)
- [ ] All baseline tests still pass
- [ ] Trade evaluation working correctly
- [ ] Phase detection accurate
- [ ] Time management phase-aware

### Should Achieve:
- [ ] Better tactical play in test positions
- [ ] Smarter capture decisions
- [ ] Improved time usage (more time in middlegame)
- [ ] Fewer "waiting moves" in opening

### Nice to Have:
- [ ] NPS improved through better move ordering
- [ ] Deeper search in middlegame (more time allocated)
- [ ] Cleaner games (fewer bad trades)

---

## 🧪 Testing Plan

### 1. Baseline Validation
```bash
python testing/test_vpr_baseline.py
```
Expected: All tests pass, NPS ≥ 15,000

### 2. Trade Evaluation Tests
Create `test_vpr_v8_1_trades.py`:
- Test SEE calculation accuracy
- Test phase-dependent trade acceptance
- Test known trade positions (Q for 2R, etc.)

### 3. Performance Regression
```bash
python testing/test_vpr_vs_material_opponent.py
```
Expected: NPS within 10% of Material Opponent

### 4. Phase Detection Tests
- Verify opening detection (move < 10, 12+ pieces)
- Verify middlegame detection (6-11 pieces)
- Verify endgame detection (≤5 pieces)
- Test edge cases (early trades, etc.)

---

## 🚀 Implementation Order

1. **Add GamePhase enum and detection method**
   - Lines: ~25
   - Location: After NodeType enum
   - Dependencies: None

2. **Modify time management**
   - Lines: ~15 modifications
   - Location: `_calculate_time_limit()` method
   - Dependencies: GamePhase detection

3. **Add SEE implementation**
   - Lines: ~60
   - Location: After `_mvv_lva_score()` method
   - Dependencies: PIECE_VALUES constant

4. **Add trade evaluation**
   - Lines: ~30
   - Location: After SEE method
   - Dependencies: SEE, GamePhase, material eval

5. **Enhance move ordering**
   - Lines: ~15 modifications
   - Location: `_order_moves()` method
   - Dependencies: Trade evaluation

6. **Test and validate**
   - Create test suite
   - Run performance benchmarks
   - Document results

---

## 📝 Code Changes Summary

### New Code (~130 lines):
- `GamePhase` enum (5 lines)
- `_detect_game_phase()` method (20 lines)
- `_static_exchange_evaluation()` method (60 lines)
- `_evaluate_trade()` method (30 lines)
- Phase cache in `__init__()` (2 lines)

### Modified Code (~25 lines):
- `_calculate_time_limit()` - phase-aware divisors (15 lines)
- `_order_moves()` - separate good/bad captures (10 lines)

### Total Impact: ~155 lines changed/added

---

## 🎓 Design Philosophy

### Why These Changes?

1. **Game Phase Detection**: Chess is fundamentally different in opening/middlegame/endgame
2. **Phase-Aware Time**: Don't waste time in simple positions, invest in complex ones
3. **SEE**: Modern engines MUST understand multi-move capture sequences
4. **Trade Evaluation**: Different phases require different strategies

### What Makes This VPR?

- **Lightweight**: <5% performance impact
- **Practical**: Focuses on most impactful heuristics
- **Clean**: No architectural changes, just smarter logic
- **Testable**: Each component can be validated independently

### What Makes This V7P3R DNA?

- **Phase awareness**: V7P3R's strategic thinking
- **Intelligent trades**: Knows when to simplify vs. complicate
- **Time management**: Invests thinking time wisely
- **Tactical understanding**: SEE adds V7P3R's tactical awareness

---

## 🔄 Integration with VPR Roadmap

**VPR v8.0** → **VPR v8.1** → VPR v8.2+

- v8.0: Material Opponent baseline (17K NPS)
- **v8.1: Phase awareness + trade intelligence (THIS DOCUMENT)**
- v8.2: Further optimization (target 25K+ NPS)
- v8.3+: Additional heuristics as needed

---

## 📚 References

- **Material Opponent**: Base architecture and time management
- **Capture Opponent v1.0**: SEE implementation and trade logic
- **V7P3R v14.1**: Phase awareness philosophy and tactical thinking
- **VPR v8.0 Launch Plan**: Overall project roadmap

---

**Status:** Ready for implementation  
**Estimated Time:** 2-3 hours (coding + testing)  
**Risk Level:** Low (all changes isolated, no core search modifications)  
**Expected Outcome:** Smarter VPR with V7P3R personality, <5% speed impact
