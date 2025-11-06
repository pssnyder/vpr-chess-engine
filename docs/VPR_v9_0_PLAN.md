# VPR v9.0 Development Plan - C0BR4 Intelligence Architecture Port

**Date:** November 5, 2025  
**Status:** 📋 Planning  
**Goal:** Port C0BR4's proven intelligence workflow to Python VPR

---

## 🎯 Core Philosophy: Learn from C0BR4's Success

C0BR4 v2.9 is battle-tested in 24/7 production on Lichess with proven tournament performance. VPR v9.0 will port C0BR4's intelligent evaluation and search architecture to Python while maintaining VPR's speed advantage.

---

## 📊 C0BR4 Architecture Analysis

### What Makes C0BR4 Strong

#### 1. **Multi-Component Evaluation System**
```csharp
// C0BR4's SimpleEvaluator.cs approach
evaluation += EvaluateMaterial(board);
evaluation += PieceSquareTables.EvaluatePosition(board, gamePhase);
evaluation += RookCoordination.Evaluate(board, gamePhase);
evaluation += KingSafety.Evaluate(board, gamePhase);
evaluation += KingEndgame.Evaluate(board, gamePhase);
evaluation += CastlingIncentive.Evaluate(board, gamePhase);
evaluation += CastlingRights.Evaluate(board, gamePhase);
```

**Key Insights:**
- Modular evaluation components (easy to tune/disable)
- Game phase awareness (opening/middlegame/endgame)
- Position-specific bonuses (king safety, rook coordination)
- Castling incentives (encourages development)

#### 2. **Intelligent Move Ordering**
```csharp
// C0BR4's MoveOrdering.cs scoring system
1. Captures (MVV-LVA: 10000 + value_difference)
2. Promotions (9000 + promotion_piece_value)
3. Checks (500 bonus)
4. Center control (10 bonus)
5. Piece development (5 bonus for N/B from back rank)
```

**Key Insights:**
- Hierarchical move scoring (captures >> promotions >> checks)
- MVV-LVA for capture ordering (Most Valuable Victim - Least Valuable Attacker)
- Positional bonuses (center, development)
- Simple but effective

#### 3. **Search with Iterative Deepening**
```csharp
// C0BR4's TranspositionSearchBot.cs approach
for (int depth = 1; depth <= maxDepth; depth++)
{
    SearchWithPV(board, depth);
    // Output UCI info at each depth
    // Break if time up or mate found
}
```

**Key Insights:**
- Gradual depth increase (always has a move ready)
- PV (Principal Variation) tracking
- Time management built-in
- Mate detection optimization

#### 4. **Quiescence Search**
```csharp
// Extend search in tactical positions
if (depth == 0)
    return QuiescenceSearch(board, alpha, beta);
```

**Key Insights:**
- Prevents horizon effect
- Searches captures/checks until quiet
- Critical for tactical accuracy

#### 5. **Transposition Table**
```csharp
// Cache positions with Zobrist hashing
transpositionTable.TryGetEntry(board, depth, alpha, beta, out ttEntry);
transpositionTable.StoreEntry(board, depth, score, bestMove, nodeType);
```

**Key Insights:**
- Avoid re-searching same positions
- 100K entry default (memory efficient)
- Stores depth, score, best move, node type

---

## 🚀 VPR v9.0 Implementation Plan

### Phase 1: Advanced Evaluation System

#### A. Multi-Component Evaluator (Port C0BR4's SimpleEvaluator)
```python
class VPRAdvancedEvaluator:
    """
    Port of C0BR4's multi-component evaluation system
    """
    
    def evaluate(self, board: chess.Board) -> float:
        """
        Comprehensive position evaluation
        Returns score in centipawns from side-to-move perspective
        """
        # Calculate game phase (0.0 = endgame, 1.0 = opening)
        game_phase = self._calculate_game_phase(board)
        
        # Core evaluation components
        score = 0
        score += self._evaluate_material(board)
        score += self._evaluate_piece_square_tables(board, game_phase)
        score += self._evaluate_king_safety(board, game_phase)
        score += self._evaluate_rook_coordination(board, game_phase)
        score += self._evaluate_castling_rights(board, game_phase)
        score += self._evaluate_king_endgame(board, game_phase)
        
        # Return from side-to-move perspective
        return score if board.turn == chess.WHITE else -score
    
    def _calculate_game_phase(self, board: chess.Board) -> float:
        """
        Calculate game phase based on material (0.0 = endgame, 1.0 = opening)
        Port of C0BR4's GamePhase.CalculatePhase()
        """
        total_material = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type != chess.KING:
                total_material += self.piece_values[piece.piece_type]
        
        # Starting material ~7800cp, endgame threshold ~2500cp
        opening_material = 7800
        endgame_material = 2500
        
        phase = (total_material - endgame_material) / (opening_material - endgame_material)
        return max(0.0, min(1.0, phase))  # Clamp to [0, 1]
    
    def _evaluate_piece_square_tables(self, board: chess.Board, phase: float) -> float:
        """
        Interpolate between opening and endgame piece-square tables
        Port of C0BR4's PieceSquareTables.EvaluatePosition()
        """
        score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if not piece:
                continue
            
            # Get opening and endgame table values
            opening_value = self.pst_opening[piece.piece_type][square]
            endgame_value = self.pst_endgame[piece.piece_type][square]
            
            # Interpolate based on game phase
            value = opening_value * phase + endgame_value * (1 - phase)
            
            # Apply from piece color perspective
            score += value if piece.color == chess.WHITE else -value
        
        return score
```

#### B. King Safety Evaluation (Port C0BR4's KingSafety)
```python
def _evaluate_king_safety(self, board: chess.Board, phase: float) -> float:
    """
    Evaluate king safety based on pawn shield and piece proximity
    More important in opening/middlegame, less in endgame
    """
    if phase < 0.3:  # Endgame - king safety less critical
        return 0
    
    safety_weight = phase  # Scale with game phase
    score = 0
    
    for color in [chess.WHITE, chess.BLACK]:
        king_square = board.king(color)
        if not king_square:
            continue
        
        # Pawn shield bonus
        pawn_shield = self._evaluate_pawn_shield(board, king_square, color)
        
        # Open file penalty
        open_file_penalty = self._evaluate_king_open_files(board, king_square, color)
        
        # Enemy piece proximity penalty
        attack_penalty = self._evaluate_king_attackers(board, king_square, color)
        
        king_safety = (pawn_shield - open_file_penalty - attack_penalty) * safety_weight
        score += king_safety if color == chess.WHITE else -king_safety
    
    return score
```

#### C. Rook Coordination (Port C0BR4's RookCoordination)
```python
def _evaluate_rook_coordination(self, board: chess.Board, phase: float) -> float:
    """
    Bonus for rooks on same file/rank, open files, 7th rank
    """
    if phase > 0.7:  # Not relevant in opening
        return 0
    
    score = 0
    
    for color in [chess.WHITE, chess.BLACK]:
        rooks = board.pieces(chess.ROOK, color)
        
        # Rooks on open files
        for rook_square in rooks:
            if self._is_open_file(board, chess.square_file(rook_square), color):
                score += 20 if color == chess.WHITE else -20
        
        # Rooks on 7th rank (2nd rank for black)
        for rook_square in rooks:
            rank = chess.square_rank(rook_square)
            if (color == chess.WHITE and rank == 6) or (color == chess.BLACK and rank == 1):
                score += 30 if color == chess.WHITE else -30
        
        # Doubled rooks bonus
        if len(rooks) == 2:
            r1, r2 = list(rooks)
            if chess.square_file(r1) == chess.square_file(r2):
                score += 15 if color == chess.WHITE else -15
    
    return score
```

#### D. Castling Incentive (Port C0BR4's CastlingIncentive)
```python
def _evaluate_castling_rights(self, board: chess.Board, phase: float) -> float:
    """
    Encourage castling in opening/middlegame
    """
    if phase < 0.5:  # Less relevant in late middlegame/endgame
        return 0
    
    score = 0
    
    # Bonus for having castling rights (encourages not moving king/rooks early)
    if board.has_kingside_castling_rights(chess.WHITE):
        score += 15 * phase
    if board.has_queenside_castling_rights(chess.WHITE):
        score += 10 * phase
    if board.has_kingside_castling_rights(chess.BLACK):
        score -= 15 * phase
    if board.has_queenside_castling_rights(chess.BLACK):
        score -= 10 * phase
    
    # Bonus for actually castled
    white_king = board.king(chess.WHITE)
    black_king = board.king(chess.BLACK)
    
    if white_king in [chess.G1, chess.C1]:  # Castled position
        score += 30 * phase
    if black_king in [chess.G8, chess.C8]:  # Castled position
        score -= 30 * phase
    
    return score
```

#### E. King Endgame Activity (Port C0BR4's KingEndgame)
```python
def _evaluate_king_endgame(self, board: chess.Board, phase: float) -> float:
    """
    In endgame, active king is critical
    """
    if phase > 0.4:  # Not relevant until late middlegame
        return 0
    
    endgame_weight = 1.0 - phase  # Increases as game progresses
    score = 0
    
    for color in [chess.WHITE, chess.BLACK]:
        king_square = board.king(color)
        if not king_square:
            continue
        
        # Centralization bonus
        center_distance = self._distance_to_center(king_square)
        centralization = (4 - center_distance) * 10  # Max +40cp for perfect center
        
        # Advanced position bonus (push toward enemy)
        if color == chess.WHITE:
            advancement = chess.square_rank(king_square) * 5  # +0 to +35
        else:
            advancement = (7 - chess.square_rank(king_square)) * 5
        
        king_activity = (centralization + advancement) * endgame_weight
        score += king_activity if color == chess.WHITE else -king_activity
    
    return score
```

---

### Phase 2: Intelligent Move Ordering (Port C0BR4's MoveOrdering)

```python
class VPRMoveOrdering:
    """
    Port of C0BR4's hierarchical move ordering system
    """
    
    def order_moves(self, board: chess.Board, moves: List[chess.Move]) -> List[chess.Move]:
        """
        Order moves by expected strength for better alpha-beta pruning
        """
        if len(moves) <= 1:
            return moves
        
        # Score each move
        scored_moves = [(move, self._score_move(board, move)) for move in moves]
        
        # Sort by score (highest first)
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        
        return [move for move, score in scored_moves]
    
    def _score_move(self, board: chess.Board, move: chess.Move) -> int:
        """
        Score move for ordering (higher = search first)
        
        C0BR4's hierarchy:
        1. Captures (MVV-LVA): 10000 + value_difference
        2. Promotions: 9000 + piece_value
        3. Checks: 500
        4. Center control: 10
        5. Development: 5
        """
        score = 0
        
        moving_piece = board.piece_at(move.from_square)
        captured_piece = board.piece_at(move.to_square)
        
        # 1. Captures - MVV-LVA
        if captured_piece:
            victim_value = self.piece_values[captured_piece.piece_type]
            attacker_value = self.piece_values[moving_piece.piece_type]
            score += 10000 + (victim_value - attacker_value)
        
        # 2. Promotions
        if move.promotion:
            score += 9000 + self.piece_values[move.promotion]
        
        # 3. Checks
        board.push(move)
        if board.is_check():
            score += 500
        board.pop()
        
        # 4. Center control (e4, e5, d4, d5)
        if move.to_square in [chess.E4, chess.E5, chess.D4, chess.D5]:
            score += 10
        
        # 5. Development (knights/bishops from back rank)
        if moving_piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
            from_rank = chess.square_rank(move.from_square)
            if (moving_piece.color == chess.WHITE and from_rank == 0) or \
               (moving_piece.color == chess.BLACK and from_rank == 7):
                score += 5
        
        return score
    
    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 300,
        chess.BISHOP: 300,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 10000
    }
```

---

### Phase 3: Search with Iterative Deepening (Port C0BR4's TranspositionSearchBot)

```python
class VPRIterativeSearchEngine:
    """
    Port of C0BR4's iterative deepening search with transposition table
    """
    
    def __init__(self):
        self.evaluator = VPRAdvancedEvaluator()
        self.move_ordering = VPRMoveOrdering()
        self.transposition_table = {}  # zobrist_key -> (depth, score, best_move, node_type)
        self.nodes_searched = 0
        self.quiescence_nodes = 0
    
    def search(self, board: chess.Board, time_limit: float) -> chess.Move:
        """
        Iterative deepening search with time management
        """
        self.nodes_searched = 0
        self.quiescence_nodes = 0
        start_time = time.time()
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        best_move = legal_moves[0]
        best_score = -50000
        
        # Iterative deepening (depth 1 to max_depth)
        for depth in range(1, 11):  # Up to depth 10
            if time.time() - start_time >= time_limit * 0.9:  # 90% time safety
                break
            
            move, score, pv = self._search_with_pv(board, depth)
            
            if move:
                best_move = move
                best_score = score
                
                # UCI output
                elapsed = int((time.time() - start_time) * 1000)
                nps = int(self.nodes_searched / (elapsed / 1000)) if elapsed > 0 else 0
                pv_str = ' '.join([m.uci() for m in pv])
                
                print(f"info depth {depth} score cp {score} nodes {self.nodes_searched} "
                      f"nps {nps} time {elapsed} pv {pv_str}")
            
            # Stop if mate found
            if abs(score) > 20000:
                break
        
        return best_move
    
    def _search_with_pv(self, board: chess.Board, depth: int) -> Tuple[chess.Move, int, List[chess.Move]]:
        """
        Search at fixed depth, return best move, score, and principal variation
        """
        moves = list(board.legal_moves)
        if not moves:
            return None, -50000, []
        
        # Order moves for better pruning
        moves = self.move_ordering.order_moves(board, moves)
        
        best_move = moves[0]
        best_score = -50000
        best_pv = []
        alpha = -50000
        beta = 50000
        
        for move in moves:
            board.push(move)
            score, pv = self._alpha_beta(board, depth - 1, -beta, -alpha)
            score = -score
            board.pop()
            
            if score > best_score:
                best_score = score
                best_move = move
                best_pv = [move] + pv
                alpha = max(alpha, score)
        
        return best_move, best_score, best_pv
    
    def _alpha_beta(self, board: chess.Board, depth: int, alpha: int, beta: int) -> Tuple[int, List[chess.Move]]:
        """
        Alpha-beta search with transposition table
        """
        self.nodes_searched += 1
        
        # Check transposition table
        zobrist = chess.polyglot.zobrist_hash(board)
        if zobrist in self.transposition_table:
            tt_depth, tt_score, tt_move, tt_type = self.transposition_table[zobrist]
            if tt_depth >= depth:
                # Can use cached score if conditions met
                if tt_type == 'exact':
                    return tt_score, [tt_move] if tt_move else []
                elif tt_type == 'alpha' and tt_score <= alpha:
                    return tt_score, [tt_move] if tt_move else []
                elif tt_type == 'beta' and tt_score >= beta:
                    return tt_score, [tt_move] if tt_move else []
        
        # Quiescence search at leaf nodes
        if depth == 0:
            return self._quiescence_search(board, alpha, beta), []
        
        # Check for terminal positions
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            if board.is_check():
                return -30000 + (10 - depth), []  # Checkmate, prefer quicker mates
            else:
                return 0, []  # Stalemate
        
        # Order moves
        legal_moves = self.move_ordering.order_moves(board, legal_moves)
        
        best_move = None
        best_pv = []
        best_score = -50000
        
        for move in legal_moves:
            board.push(move)
            score, pv = self._alpha_beta(board, depth - 1, -beta, -alpha)
            score = -score
            board.pop()
            
            if score > best_score:
                best_score = score
                best_move = move
                best_pv = [move] + pv
            
            alpha = max(alpha, score)
            if alpha >= beta:
                # Beta cutoff - store in TT
                self.transposition_table[zobrist] = (depth, beta, best_move, 'beta')
                return beta, best_pv
        
        # Store in transposition table
        if best_score <= alpha:
            self.transposition_table[zobrist] = (depth, alpha, best_move, 'alpha')
        else:
            self.transposition_table[zobrist] = (depth, best_score, best_move, 'exact')
        
        return best_score, best_pv
    
    def _quiescence_search(self, board: chess.Board, alpha: int, beta: int) -> int:
        """
        Search captures and checks until position is quiet
        Port of C0BR4's quiescence search
        """
        self.quiescence_nodes += 1
        
        # Stand pat - evaluate current position
        stand_pat = self.evaluator.evaluate(board)
        
        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat
        
        # Generate and order tactical moves (captures, promotions, checks)
        tactical_moves = []
        for move in board.legal_moves:
            if board.is_capture(move) or move.promotion or board.gives_check(move):
                tactical_moves.append(move)
        
        if not tactical_moves:
            return stand_pat
        
        # Order tactical moves
        tactical_moves = self.move_ordering.order_moves(board, tactical_moves)
        
        for move in tactical_moves:
            board.push(move)
            score = -self._quiescence_search(board, -beta, -alpha)
            board.pop()
            
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        
        return alpha
```

---

## 📊 Implementation Timeline

### Phase 1: Advanced Evaluation (Week 1)
- **Day 1-2:** Multi-component evaluator structure
- **Day 3:** Piece-square tables (opening/endgame)
- **Day 4:** King safety evaluation
- **Day 5:** Rook coordination + castling incentives
- **Day 6:** King endgame activity
- **Day 7:** Testing and tuning

### Phase 2: Move Ordering (Week 2)
- **Day 1:** MVV-LVA capture ordering
- **Day 2:** Promotion + check scoring
- **Day 3:** Positional bonuses (center, development)
- **Day 4-5:** Integration and testing
- **Day 6-7:** Performance optimization

### Phase 3: Search Engine (Week 3)
- **Day 1-2:** Iterative deepening framework
- **Day 3-4:** Alpha-beta with transposition table
- **Day 5-6:** Quiescence search
- **Day 7:** PV tracking and UCI output

### Phase 4: Testing & Validation (Week 4)
- **Day 1-2:** Unit tests for all components
- **Day 3-4:** Performance benchmarking
- **Day 5-6:** Tournament testing vs v8.1
- **Day 7:** Documentation and release

---

## 🎯 Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Evaluation Quality** | More nuanced than v8.1 | Position assessment tests |
| **Move Ordering** | 90%+ best move first | Alpha-beta cutoff rate |
| **Search Depth** | 6-8 ply in 3 seconds | Performance benchmark |
| **Playing Strength** | +100-200 Elo vs v8.1 | Tournament matches |
| **Code Quality** | Clean, modular, testable | Code review |
| **Performance** | 15K+ NPS | Speed benchmark |

---

## 🎓 Design Philosophy

### C0BR4's Proven Principles
1. **Modular Components** - Easy to tune/disable individual features
2. **Game Phase Awareness** - Different strategies for different phases
3. **Hierarchical Move Ordering** - Simple but effective priority system
4. **Iterative Deepening** - Always have a move ready, time-aware
5. **Quiescence Search** - Critical for tactical accuracy

### VPR's Core Values
- **Clean Python** - Readable, maintainable code
- **Performance** - Optimize hot paths
- **Testable** - Comprehensive test coverage
- **Documented** - Clear comments and docstrings

### Combined Approach
- Port C0BR4's intelligence
- Maintain VPR's code quality
- Optimize for Python idioms
- Keep it fast and clean

---

## 🔧 Configuration

```python
# VPR v9.0 Configuration
class VPRConfig:
    # Search parameters
    max_search_depth: int = 10
    transposition_table_size: int = 100000  # Entries
    
    # Evaluation weights (tunable)
    material_weight: float = 1.0
    pst_weight: float = 1.0
    king_safety_weight: float = 1.5
    rook_coordination_weight: float = 0.8
    castling_weight: float = 1.0
    king_endgame_weight: float = 1.2
    
    # Move ordering
    mvv_lva_enabled: bool = True
    check_bonus: int = 500
    center_bonus: int = 10
    development_bonus: int = 5
    
    # Time management
    time_safety_margin: float = 0.9  # Use 90% of allocated time
```

---

## 📚 Key Differences from v8.1

| Feature | VPR v8.1 | VPR v9.0 (C0BR4 Port) |
|---------|----------|----------------------|
| **Evaluation** | Material + basic phase awareness | Multi-component modular system |
| **Move Ordering** | Good/bad captures | MVV-LVA + hierarchical scoring |
| **Search** | Simple alpha-beta | Iterative deepening + TT |
| **Quiescence** | Basic | Full tactical extension |
| **Game Phase** | 3-state detection | Continuous interpolation |
| **King Safety** | None | Full shield + proximity eval |
| **Endgame** | Basic | King activity + advanced |

---

## 🎯 Bottom Line

**VPR v9.0 will port C0BR4's battle-tested intelligence architecture to Python.**

Core ports:
1. ✅ **Multi-Component Evaluation** - Modular, phase-aware assessment
2. ✅ **Intelligent Move Ordering** - MVV-LVA + hierarchical scoring
3. ✅ **Iterative Deepening Search** - Time-aware, always ready
4. ✅ **Quiescence Search** - Tactical accuracy
5. ✅ **Transposition Table** - Zobrist hashing

**Expected outcome: +100-200 Elo over v8.1 with proven tournament architecture.**

---

**Status:** Ready to implement  
**Base:** VPR v8.1 (16.3K NPS, phase-aware)  
**Target:** C0BR4 v2.9 intelligence in Python  
**Timeline:** 4 weeks to production-ready v9.0
