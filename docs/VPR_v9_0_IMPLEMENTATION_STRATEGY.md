# VPR v9.0 Implementation Strategy

**Date:** November 5, 2025  
**Strategy:** Port C0BR4's core intelligence incrementally  
**Goal:** Solve rook shuffling + tactical blindness with minimal, proven heuristics

---

## 🎯 Phase 1: Critical Foundation (v9.0.0)

### What We're Porting from C0BR4:

**Priority 1: Move Ordering (MVV-LVA)**
- Solves: Poor alpha-beta pruning efficiency
- Implementation: ~50 lines
- Impact: 3-5x search speedup from better cutoffs

**Priority 2: Basic Piece-Square Tables**
- Solves: Rook shuffling, passive play
- Implementation: ~100 lines (tables + evaluation)
- Impact: Positional understanding, forward progress

**Priority 3: Positional Bonuses**
- Center control (+10cp)
- Development bonus (+5cp for N/B from back rank)
- Solves: Decisiveness in equal positions

### What We're KEEPING from VPR v8.1:
- ✅ Phase detection (already working well)
- ✅ Time management (phase-aware)
- ✅ SEE implementation (tactical intelligence)
- ✅ Basic search structure

---

## 📝 Implementation Order:

### Step 1: Add C0BR4's MVV-LVA Move Ordering (~30 min)
```python
def _score_move_c0br4_style(self, board, move):
    """
    C0BR4's hierarchical move scoring
    
    1. Captures: 10000 + (victim_value - attacker_value)
    2. Promotions: 9000 + piece_value
    3. Checks: 500
    4. Center: 10
    5. Development: 5
    """
```

### Step 2: Add Basic Piece-Square Tables (~45 min)
```python
# Opening PST - encourages development, center control
OPENING_PST = {
    chess.PAWN: [...],
    chess.KNIGHT: [...],
    # etc
}

# Endgame PST - encourages king activity
ENDGAME_PST = {
    # Different tables for endgame
}
```

### Step 3: Integrate PST into Evaluation (~20 min)
```python
def _evaluate_board(self, board):
    score = 0
    phase = self._detect_game_phase(board)
    
    # Material
    score += self._evaluate_material(board)
    
    # Piece-square tables (new!)
    score += self._evaluate_pst(board, phase)
    
    return score
```

### Step 4: Testing & Validation (~30 min)
- Test that move ordering improves
- Test that rook shuffling is reduced
- Performance check (target: 15K+ NPS)

---

## 🎯 Success Criteria for v9.0.0:

| Metric | Target | Test Method |
|--------|--------|-------------|
| **Rook Shuffling** | < 10% of moves | Game analysis |
| **Move Ordering** | 70%+ good moves first | Cutoff analysis |
| **Performance** | 15K+ NPS | Benchmark |
| **Playing Strength** | +50-100 Elo vs v8.1 | Tournament |

---

## 📊 Incremental Rollout:

- **v9.0.0**: MVV-LVA + Basic PST (~2 hours work)
- **v9.0.1**: King safety basics (if needed)
- **v9.0.2**: Rook coordination (if needed)
- **v9.1.0**: Iterative deepening + TT improvements

Each version battle-tested before proceeding!

---

## 🚀 Let's Start:

Focus on the absolute minimum:
1. ✅ Fix move ordering (MVV-LVA)
2. ✅ Add PST (positional understanding)
3. ✅ Test against v8.1

If it works, we incrementally add more C0BR4 features.
If it doesn't, we have minimal changes to debug.

**C0BR4's lesson: ONE CHANGE AT A TIME, BATTLE TEST EACH**
