# VPR v8.2 Enhancement Plan

**Date:** November 5, 2025  
**Status:** 📋 Planning  
**Goal:** Add draw prevention and move variety while maintaining quality

---

## 🎯 Primary Objective: Draw Prevention

### Problem Statement
Chess engines playing themselves often fall into repetitive patterns, leading to:
- Draw by threefold repetition
- Draw by 50-move rule
- Boring, predictable gameplay
- Poor tournament diversity

### Solution: Intelligent Randomness
Add **controlled variation** that:
- ✅ Preserves move quality (no random bad moves)
- ✅ Prevents repetition draws
- ✅ Increases gameplay variety
- ✅ Maintains tactical soundness

---

## 📋 Proposed v8.2 Features

### 1. **Decisive Play & Initiative** (PRIORITY 1)
**What:** Prevent passive rook shuffling and encourage forward progress  
**How:** Penalize non-progressive moves, reward attacking moves

**Problem Identified:**
- VPR makes "shifty rook moves" when it can't find gainful moves
- Lacks decisiveness in equal positions
- No initiative or forward progress
- Passive play leads to time waste and missed opportunities

**Solution - Multi-Layered Approach:**

#### A. Non-Progressive Move Penalty
```python
def _is_non_progressive_move(self, board: chess.Board, move: chess.Move) -> bool:
    """
    Detect passive/repetitive moves that don't advance the position
    
    Non-progressive moves:
    - Rook/Queen moves along same rank/file without purpose
    - Knight retreating to original square
    - Moving same piece twice in a row (tempo loss)
    - Moves that don't improve piece activity
    """
    piece = board.piece_at(move.from_square)
    if not piece:
        return False
    
    # Check if rook/queen just shuffling without attacking/defending
    if piece.piece_type in [chess.ROOK, chess.QUEEN]:
        from_attacks = len(board.attacks(move.from_square))
        to_attacks = len(board.attacks(move.to_square))
        
        # If not attacking more squares and not capturing, it's passive
        if to_attacks <= from_attacks and not board.is_capture(move):
            return True
    
    # Check if retreating to starting square
    if self._is_retreating_to_start(move, piece):
        return True
    
    # Check if moving same piece repeatedly (last_move tracking)
    if self._is_repeated_piece_move(move):
        return True
    
    return False

def _evaluate_move_progressiveness(self, board: chess.Board, move: chess.Move) -> float:
    """
    Reward progressive, attacking moves. Penalize passive shuffling.
    
    Returns:
        Bonus/penalty in centipawns
    """
    penalty = 0
    
    # Passive move penalty
    if self._is_non_progressive_move(board, move):
        penalty -= 20  # -20cp for shuffling
    
    # Bonus for forward progress
    piece = board.piece_at(move.from_square)
    if piece:
        # Bonus for advancing pawns (space gain)
        if piece.piece_type == chess.PAWN:
            if piece.color == chess.WHITE and chess.square_rank(move.to_square) > chess.square_rank(move.from_square):
                penalty += 5  # Small bonus for pawn advance
            elif piece.color == chess.BLACK and chess.square_rank(move.to_square) < chess.square_rank(move.from_square):
                penalty += 5
        
        # Bonus for centralizing pieces
        to_center_distance = self._distance_to_center(move.to_square)
        from_center_distance = self._distance_to_center(move.from_square)
        if to_center_distance < from_center_distance:
            penalty += 3  # Small bonus for centralization
        
        # Bonus for attacking enemy pieces
        to_attacks = board.attacks(move.to_square)
        enemy_pieces_attacked = sum(1 for sq in to_attacks 
                                    if board.piece_at(sq) and 
                                    board.piece_at(sq).color != piece.color)
        if enemy_pieces_attacked > 0:
            penalty += enemy_pieces_attacked * 2  # Bonus for attacking
    
    return penalty
```

#### B. Last Move Tracking
```python
def __init__(self):
    # ... existing init code ...
    self.last_moved_piece = None  # Track what piece moved last
    self.last_move_to_square = None  # Track where it moved to
    self.consecutive_piece_moves = 0  # How many times same piece moved
```

#### C. Positional Initiative Bonus
```python
def _evaluate_initiative(self, board: chess.Board) -> float:
    """
    Reward active, attacking positions. Penalize passive setups.
    
    Initiative factors:
    - Number of pieces attacking enemy territory
    - Control of center squares
    - Advanced pawn structure
    - Active piece placement
    """
    initiative_score = 0
    my_color = board.turn
    
    # Count pieces in enemy territory
    enemy_half = range(32, 64) if my_color == chess.WHITE else range(0, 32)
    my_pieces_in_enemy_territory = sum(1 for sq in enemy_half 
                                       if board.piece_at(sq) and 
                                       board.piece_at(sq).color == my_color)
    initiative_score += my_pieces_in_enemy_territory * 5
    
    # Center control (e4, e5, d4, d5)
    center_squares = [chess.E4, chess.E5, chess.D4, chess.D5]
    center_control = sum(1 for sq in center_squares 
                        if board.is_attacked_by(my_color, sq))
    initiative_score += center_control * 3
    
    return initiative_score
```

**Integration:**
- Apply during move evaluation in `_evaluate_board()`
- Factor into move ordering in `_order_moves()`
- Penalize passive play by -20cp
- Reward initiative with +5 to +15cp

**Settings:**
- Passive move penalty: -20cp
- Initiative bonus: +5 to +15cp
- Centralization bonus: +3cp
- Attack bonus: +2cp per enemy piece attacked

**Expected Impact:**
- **Eliminates rook shuffling** - makes such moves unattractive
- **Encourages forward play** - pawns, piece centralization
- **Rewards attacking moves** - increases tactical opportunities
- **Forces decisions** - even in equal positions, choose most progressive move

---

### 2. **Contempt Factor** (PRIORITY 2)
**What:** Bias evaluation to avoid draws  
**How:** Add small penalty to draw positions
```python
def _evaluate_with_contempt(self, board: chess.Board, base_eval: float) -> float:
    """
    Apply contempt factor to discourage draws
    
    Args:
        board: Current position
        base_eval: Base material evaluation
        
    Returns:
        Adjusted evaluation with contempt applied
    """
    # If position is drawish (eval near 0), add contempt
    if abs(base_eval) < 50:  # Within 0.5 pawn of equality
        # Slight bias to keep playing (5-10 centipawns)
        return base_eval + self.contempt_value
    return base_eval
```

**Settings:**
- Contempt value: 5-15 centipawns (configurable)
- Applied to: Positions with |eval| < 50cp
- Phase-aware: Higher in opening/middlegame, lower in endgame

**Impact:**
- Prevents premature draw agreements
- Encourages active play in equal positions
- Minimal effect on clearly won/lost positions

---

### 3. **Multi-PV Selection with Randomness** (PRIORITY 3)
**What:** Select from top N moves with quality weighting  
**How:** Choose among best moves with controlled randomness
```python
def _select_move_with_variety(self, top_moves: List[Tuple[chess.Move, float]]) -> chess.Move:
    """
    Select move from top candidates with quality-weighted randomness
    
    Strategy:
    - If best move significantly better (>30cp): Always play it
    - If top 2-3 moves within 15cp: Choose with weighted probability
    - If all equal: Random selection from top 3
    
    Args:
        top_moves: List of (move, score) sorted by score
        
    Returns:
        Selected move with controlled variety
    """
    if not top_moves:
        return None
    
    best_score = top_moves[0][1]
    
    # Significant advantage - always play best
    if len(top_moves) > 1 and best_score - top_moves[1][1] > 30:
        return top_moves[0][0]
    
    # Find moves within acceptable margin (15cp)
    acceptable_margin = 15
    candidates = []
    for move, score in top_moves[:5]:  # Consider top 5
        if best_score - score <= acceptable_margin:
            # Weight by quality (closer to best = higher weight)
            weight = 1.0 / (1.0 + (best_score - score) / 10.0)
            candidates.append((move, weight))
    
    # Weighted random selection
    if len(candidates) > 1:
        return random.choices([m for m, w in candidates], 
                             weights=[w for m, w in candidates])[0]
    
    return top_moves[0][0]
```

**Settings:**
- Acceptance margin: 15 centipawns (configurable)
- Max candidates: Top 5 moves
- Weighting: Quality-based (exponential decay)

**Impact:**
- Game variety without sacrificing quality
- Prevents repetitive opening lines
- Still plays best move when it matters

---

### 4. **Position Repetition Detection** (PRIORITY 4)
**What:** Track position repetitions and avoid them  
**How:** Maintain position history, penalize repeating positions
```python
def _detect_repetition(self, board: chess.Board) -> int:
    """
    Detect how many times current position has occurred
    
    Returns:
        Number of times position has appeared (0, 1, or 2)
    """
    zobrist = self._get_zobrist_key(board)
    return self.position_history.get(zobrist, 0)

def _evaluate_with_repetition_avoidance(self, board: chess.Board, base_eval: float) -> float:
    """
    Penalize moves leading to repeated positions
    
    Penalties:
    - First repetition: -10cp
    - Second repetition (threefold): -50cp (strong avoidance)
    """
    repetitions = self._detect_repetition(board)
    
    if repetitions == 1:
        return base_eval - 10  # Slight penalty
    elif repetitions >= 2:
        return base_eval - 50  # Strong penalty (avoid draw)
    
    return base_eval
```

**Settings:**
- First repetition penalty: -10cp
- Threefold repetition penalty: -50cp
- History size: Last 100 positions (memory efficient)

**Impact:**
- Actively avoids threefold repetition
- Prevents draw loops
- Encourages position variety

---

### 5. **Evaluation Noise (Optional)** (PRIORITY 5)
**What:** Add tiny random noise to equal-eval moves  
**How:** Break ties with minimal random variation
```python
def _add_evaluation_noise(self, eval: float, max_noise: float = 2.0) -> float:
    """
    Add tiny noise to evaluation to break ties
    
    Only applied when:
    - Multiple moves have identical evaluation
    - Noise is minimal (±2cp max)
    - Doesn't change move ordering significantly
    
    Args:
        eval: Base evaluation
        max_noise: Maximum noise (default 2cp)
        
    Returns:
        Evaluation with tiny noise applied
    """
    noise = random.uniform(-max_noise, max_noise)
    return eval + noise
```

**Settings:**
- Max noise: ±2 centipawns
- Applied: Only when evals within 1cp
- Deterministic seed: Optional for reproducibility

**Impact:**
- Breaks exact evaluation ties
- Minimal effect on move quality
- Increases micro-variety

---

## 📊 Implementation Priority

### Phase 1: Core Improvements (v8.2.0)
1. ✅ **Decisive Play & Initiative** - Fix passive rook shuffling (CRITICAL)
2. ✅ **Contempt Factor** - Discourage equal positions
3. ✅ **Position Repetition Detection** - Foundation for draw avoidance
4. ✅ **Multi-PV Selection** - Controlled move variety

### Phase 2: Optional Enhancements (v8.2.1+)
5. 🔧 **Evaluation Noise** - Tie-breaking (if needed)
6. 🔧 **Opening Book Integration** - Pre-built variety
7. 🔧 **Time-Based Randomness** - Vary thinking time slightly

---

## 🎓 Design Philosophy

### Quality First
- **Never sacrifice move quality for variety**
- Only select from objectively good moves
- Keep tactical soundness intact
- **Be decisive over being passive** - action beats inaction

### Controlled Randomness
- **Not random bad moves** - weighted selection from good moves
- **Quality bounds** - only within acceptable margin (15cp)
- **Context-aware** - more variety in equal positions, less in critical positions

### Draw-Aware
- **Detect repetitions** - track position history
- **Penalize draws** - contempt factor and repetition penalties
- **Encourage variety** - multi-PV selection

### Performance Conscious
- **Minimal overhead** - reuse existing search results
- **No architecture changes** - just selection logic
- **Cache-friendly** - zobrist-based tracking

---

## 🔧 Configuration (Proposed)

```python
# VPR v8.2 Configuration Options
class VPRConfig:
    # Decisive Play
    passive_move_penalty: int = 20  # Centipawns penalty for shuffling
    initiative_bonus_enabled: bool = True
    centralization_bonus: int = 3  # Bonus for moving toward center
    attack_bonus: int = 2  # Bonus per enemy piece attacked
    
    # Draw Prevention
    contempt_value: int = 10  # Centipawns (0 to disable)
    contempt_phase_scaling: bool = True  # Reduce in endgame
    
    # Move Variety
    multi_pv_enabled: bool = True
    multi_pv_margin: int = 15  # Centipawns
    multi_pv_max_candidates: int = 5
    
    # Repetition Avoidance
    repetition_detection: bool = True
    first_repetition_penalty: int = 10  # Centipawns
    threefold_repetition_penalty: int = 50  # Centipawns
    position_history_size: int = 100
    
    # Evaluation Noise (Optional)
    eval_noise_enabled: bool = False
    eval_noise_max: float = 2.0  # Centipawns
```

---

## 📈 Expected Outcomes

### Decisive Play Improvement
- **Current:** Passive rook shuffling in equal positions
- **Target:** Eliminate non-progressive moves, always make forward progress
- **Method:** Position analysis, game review for passive sequences

### Draw Rate Reduction
- **Current:** Unknown (baseline needed)
- **Target:** Reduce by 30-50%
- **Method:** Tournament testing vs v8.1

### Move Variety
- **Current:** Deterministic (same position = same move)
- **Target:** 2-3 unique opening variations in 10 games
- **Method:** Self-play analysis

### Performance Impact
- **Target:** < 3% overhead
- **Tracking:** Position history (~100 zobrist keys)
- **Selection:** O(1) from cached search results

### Quality Preservation
- **Target:** No significant rating loss
- **Method:** Tournament testing vs external engines
- **Metric:** Rating stability (±50 Elo acceptable)

---

## 🧪 Testing Plan

### 1. Unit Tests
- Passive move detection
- Initiative evaluation
- Contempt factor application
- Multi-PV selection logic
- Repetition detection accuracy
- Position history management

### 2. Self-Play Tests
- Passive move frequency (should be near 0%)
- Draw rate measurement (100+ games)
- Move variety analysis (opening diversity)
- Repetition avoidance verification
- Initiative/attacking behavior analysis

### 3. Performance Tests
- Memory usage with position history
- Search speed impact
- NPS comparison vs v8.1

### 4. Quality Tests
- Tournament vs v8.1 (quality baseline)
- Tournament vs external engines (rating stability)
- Tactical test suite (no regression)

---

## 🎯 Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Passive Moves | < 5% of moves | Game analysis (50 games) |
| Initiative Score | > v8.1 baseline | Position evaluation |
| Draw Rate | -30% to -50% | Self-play (100 games) |
| Opening Variety | 2-3 variations | 10-game analysis |
| Performance | < 5% overhead | NPS benchmark |
| Quality | ±50 Elo | Tournament testing |
| Repetitions | < 5% threefold | Self-play (100 games) |

---

## 🚀 Implementation Estimate

### Time Required
- **Decisive Play & Initiative:** 2 hours
- **Repetition Detection:** 1 hour
- **Contempt Factor:** 30 minutes
- **Multi-PV Selection:** 1.5 hours
- **Testing & Validation:** 2.5 hours
- **Documentation:** 30 minutes
- **Total:** ~8 hours

### Lines of Code
- Decisive play detection: ~60 lines
- Initiative evaluation: ~40 lines
- Last move tracking: ~15 lines
- Position history tracking: ~30 lines
- Contempt factor: ~20 lines
- Multi-PV selection: ~40 lines
- Repetition detection: ~25 lines
- Configuration: ~20 lines
- **Total:** ~250 lines

### Risk Level
- **Low:** No search algorithm changes
- **Low:** Features are independent (can be toggled)
- **Medium:** Requires careful testing for quality preservation

---

## 📚 References & Inspiration

### Similar Implementations
- **Stockfish:** Contempt factor and multi-PV
- **Leela Chess Zero:** Policy head (move variety)
- **V7P3R:** Position repetition tracking (if implemented)

### Research
- Contempt factor impact on draw rates
- Multi-PV selection in tournament play
- Randomness vs quality trade-offs

---

## 🔄 Integration with VPR Roadmap

**VPR v8.0** → **VPR v8.1** → **VPR v8.2** → VPR v8.3+

- v8.0: Material Opponent baseline (17K NPS)
- v8.1: Phase awareness + trade intelligence (16K NPS) ✅
- **v8.2: Draw prevention + move variety (THIS DOCUMENT)**
- v8.3+: Additional optimizations (null move, LMR, etc.)

---

## 💡 Future Considerations (v8.3+)

### If Draw Prevention Works Well
- Opening book integration
- Endgame tablebase variety
- Time-based seed variation

### If Quality Issues Arise
- Reduce multi-PV margin (15cp → 10cp)
- Increase quality weighting
- Limit variety to non-critical positions

### Performance Optimizations
- Incremental position history updates
- Compact zobrist storage
- Lazy contempt evaluation

---

## 🎯 Bottom Line

**VPR v8.2 will fix passive play and add intelligent variety without sacrificing quality.**

Four core features:
1. ✅ **Decisive Play & Initiative** - Eliminate rook shuffling, force forward progress (CRITICAL FIX)
2. ✅ **Contempt Factor** - Discourage premature draws
3. ✅ **Position Repetition Detection** - Track and avoid repeats
4. ✅ **Multi-PV Selection** - Quality-weighted move variety

All features:
- Toggleable (can be disabled)
- Low overhead (< 5%)
- Quality-preserving (±50 Elo acceptable)
- **Decisiveness-improving** (eliminate passive play)
- Draw-reducing (target: -30% to -50%)

**Ready for implementation after v8.1 validation in tournament play.**

---

**Status:** Awaiting v8.1 tournament results  
**Next Action:** Establish v8.1 baseline, then implement v8.2 features  
**Timeline:** Ready to start after v8.1 tournament testing
