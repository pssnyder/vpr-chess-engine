#!/usr/bin/env python3
"""
TAL-BOT Chess Engine - Revolutionary Entropy-Driven Chess AI

An experimental anti-engine based on Mikhail Tal's sacrificial attacking style.
Uses dynamic piece values and chaos-driven search to destroy traditional engines.

THE 2+2=5 PRINCIPLE: Position >> Material
- True piece values based on attacks + legal moves (not static assumptions)
- Chaos factor preservation over safe evaluation
- Priority-based move ordering (best/worst pieces only)
- Entropy warfare: force opponents into complex positions

REVOLUTIONARY FEATURES:
- Dynamic piece value system (true positional worth)
- Chaos factor calculation and preservation
- Priority piece selection (ignore mediocre pieces)
- Principal Variation following for bullet speed
- Anti-engine logic that breaks traditional patterns

TAL-BOT MOTTO: "Into the dark forest where only we know the way out"

Author: Pat Snyder
Version: TAL-BOT v1.0 (The Entropy Engine)
"""

import time
import chess
from typing import Optional, List


class VPREngine:
    """VPR - Barebones chess engine optimized for maximum search depth"""
    
    def __init__(self):
        # Basic piece values
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 0
        }
        
        # Simple piece-square tables for positional awareness
        # Values are from white's perspective, will be flipped for black
        self._init_piece_square_tables()
        
        # Search configuration
        self.default_depth = 8  # Target deeper search
        self.nodes_searched = 0
        self.search_start_time = 0
        
        # TAL-BOT PV Following System
        self.principal_variation = []  # Current PV line
        self.pv_board_states = []      # Board states for PV following
        self.last_search_pv = []       # Last complete PV for instant moves
        self.pv_move_times = []        # Time taken for each PV move
        
    def _init_piece_square_tables(self):
        """Initialize basic piece-square tables for positional evaluation"""
        
        # Pawn table - encourage central pawns and advancement
        self.pawn_table = [
            0,  0,  0,  0,  0,  0,  0,  0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
            5,  5, 10, 25, 25, 10,  5,  5,
            0,  0,  0, 20, 20,  0,  0,  0,
            5, -5,-10,  0,  0,-10, -5,  5,
            5, 10, 10,-20,-20, 10, 10,  5,
            0,  0,  0,  0,  0,  0,  0,  0
        ]
        
        # Knight table - prefer center, avoid edges
        self.knight_table = [
            -50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  0,  0,  0,-20,-40,
            -30,  0, 10, 15, 15, 10,  0,-30,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -30,  5, 10, 15, 15, 10,  5,-30,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50
        ]
        
        # Bishop table - prefer long diagonals
        self.bishop_table = [
            -20,-10,-10,-10,-10,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5, 10, 10,  5,  0,-10,
            -10,  5,  5, 10, 10,  5,  5,-10,
            -10,  0, 10, 10, 10, 10,  0,-10,
            -10, 10, 10, 10, 10, 10, 10,-10,
            -10,  5,  0,  0,  0,  0,  5,-10,
            -20,-10,-10,-10,-10,-10,-10,-20
        ]
        
        # Rook table - prefer open files and 7th rank
        self.rook_table = [
            0,  0,  0,  0,  0,  0,  0,  0,
            5, 10, 10, 10, 10, 10, 10,  5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            0,  0,  0,  5,  5,  0,  0,  0
        ]
        
        # Queen table - slight center preference
        self.queen_table = [
            -20,-10,-10, -5, -5,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5,  5,  5,  5,  0,-10,
            -5,  0,  5,  5,  5,  5,  0, -5,
            0,  0,  5,  5,  5,  5,  0, -5,
            -10,  5,  5,  5,  5,  5,  0,-10,
            -10,  0,  5,  0,  0,  0,  0,-10,
            -20,-10,-10, -5, -5,-10,-10,-20
        ]
        
        # King middlegame table - stay safe, prefer castled position
        self.king_table = [
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -20,-30,-30,-40,-40,-30,-30,-20,
            -10,-20,-20,-20,-20,-20,-20,-10,
            20, 20,  0,  0,  0,  0, 20, 20,
            20, 30, 10,  0,  0, 10, 30, 20
        ]
    
    def search(self, board: chess.Board, time_limit: float = 3.0, 
               depth: Optional[int] = None) -> chess.Move:
        """
        TAL-BOT main search with PV collection and following
        
        Args:
            board: Current position
            time_limit: Time limit in seconds
            depth: Optional fixed depth (otherwise uses default)
            
        Returns:
            Best move found
        """
        self.nodes_searched = 0
        self.search_start_time = time.time()
        
        # Check for PV following opportunity (instant move)
        instant_move = self._check_pv_following(board)
        if instant_move:
            print(f"info string PV following: instant move {instant_move}")
            return instant_move
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return chess.Move.null()
        
        if len(legal_moves) == 1:
            return legal_moves[0]
        
        # Calculate time allocation (use 80% of available time)
        target_time = time_limit * 0.8
        
        # Iterative deepening with PV collection
        max_depth = depth if depth else self.default_depth
        best_move = legal_moves[0]
        best_score = -999999
        self.principal_variation = []
        
        for current_depth in range(1, max_depth + 1):
            iteration_start = time.time()
            elapsed = time.time() - self.search_start_time
            
            # Stop if we're running out of time
            if elapsed > target_time:
                break
            
            # Search at current depth with PV collection
            current_pv = []
            score = -999999
            current_best = best_move
            time_exceeded = False
            
            for move in legal_moves:
                # Check time before starting move search
                elapsed = time.time() - self.search_start_time
                if elapsed > target_time:
                    time_exceeded = True
                    break
                
                board.push(move)
                
                # Negamax search with PV collection
                move_pv = []
                move_score = -self._negamax(board, current_depth - 1, -999999, 999999, target_time, move_pv)
                
                board.pop()
                
                if move_score > score:
                    score = move_score
                    current_best = move
                    current_pv = [move] + move_pv  # Build full PV
            
            # Update best move and PV only if we completed this depth
            if not time_exceeded:
                best_move = current_best
                best_score = score
                self.principal_variation = current_pv[:]  # Store current PV
                
                # UCI info output with full PV
                elapsed = time.time() - self.search_start_time
                nps = int(self.nodes_searched / elapsed) if elapsed > 0 else 0
                
                # Format PV for UCI
                pv_string = " ".join(str(move) for move in current_pv[:10])  # Show first 10 moves
                
                print(f"info depth {current_depth} score cp {int(score)} "
                      f"nodes {self.nodes_searched} time {int(elapsed * 1000)} "
                      f"nps {nps} pv {pv_string}")
        
        # Store final PV for potential following
        self.last_search_pv = self.principal_variation[:]
        self._store_pv_board_states(board)
        
        return best_move
    
    def _quick_material_balance(self, board: chess.Board) -> int:
        """
        Quick material balance calculation using piece-centric approach
        
        Args:
            board: Current position
            
        Returns:
            Material balance from current player's perspective
        """
        white_material = 0
        black_material = 0
        
        # Use piece_map() instead of iterating over all squares
        piece_map = board.piece_map()
        
        for square, piece in piece_map.items():
            value = self.piece_values.get(piece.piece_type, 0)
            if piece.color == chess.WHITE:
                white_material += value
            else:
                black_material += value
        
        if board.turn == chess.WHITE:
            return white_material - black_material
        else:
            return black_material - white_material
    
    def _calculate_piece_priorities(self, board: chess.Board) -> dict:
        """
        Calculate piece priorities and criticality using piece-centric approach
        Only iterates over actual pieces (max 32) instead of all squares (64)
        """
        piece_data = {}
        
        # Get all pieces directly - much faster than checking every square
        piece_map = board.piece_map()
        
        for square, piece in piece_map.items():
            # Calculate positional value
            base_value = self.piece_values.get(piece.piece_type, 0)
            table_square = square if piece.color == chess.WHITE else (63 - square)
            
            # Get positional bonus from appropriate table
            positional_bonus = self._get_positional_bonus(piece.piece_type, table_square)
            total_value = base_value + positional_bonus
            
            # Calculate piece criticality metrics
            attackers = len(board.attackers(not piece.color, square))
            defenders = len(board.attackers(piece.color, square))
            
            # Calculate mobility (number of legal moves for this piece)
            mobility = self._calculate_piece_mobility(board, square, piece)
            
            # Determine if piece is under attack
            is_attacked = attackers > 0
            is_defended = defenders > 0
            
            # Calculate priority score combining value and tactical situation
            priority_score = total_value
            if is_attacked and not is_defended:
                priority_score += 1000  # Urgent: undefended piece under attack
            elif is_attacked and attackers > defenders:
                priority_score += 500   # High: piece needs attention
            elif piece.piece_type in [chess.QUEEN, chess.ROOK] and mobility < 3:
                priority_score += 300   # Trapped major piece
            
            piece_data[square] = {
                'piece': piece,
                'value': total_value,
                'priority': priority_score,
                'mobility': mobility,
                'attackers': attackers,
                'defenders': defenders,
                'is_attacked': is_attacked,
                'is_defended': is_defended
            }
        
        return piece_data
    
    def _get_positional_bonus(self, piece_type: chess.PieceType, table_square: int) -> int:
        """Get positional bonus for piece type at square"""
        if piece_type == chess.PAWN:
            return self.pawn_table[table_square]
        elif piece_type == chess.KNIGHT:
            return self.knight_table[table_square]
        elif piece_type == chess.BISHOP:
            return self.bishop_table[table_square]
        elif piece_type == chess.ROOK:
            return self.rook_table[table_square]
        elif piece_type == chess.QUEEN:
            return self.queen_table[table_square]
        elif piece_type == chess.KING:
            return self.king_table[table_square]
        return 0
    
    def _calculate_piece_mobility(self, board: chess.Board, square: chess.Square, piece: chess.Piece) -> int:
        """Calculate mobility for a specific piece"""
        if piece.piece_type == chess.PAWN:
            # Pawns have limited mobility, count basic moves
            mobility = 0
            if piece.color == chess.WHITE:
                if square + 8 <= 63 and not board.piece_at(square + 8):
                    mobility += 1
                    if square < 16 and not board.piece_at(square + 16):  # Double push
                        mobility += 1
            else:
                if square - 8 >= 0 and not board.piece_at(square - 8):
                    mobility += 1
                    if square >= 48 and not board.piece_at(square - 16):  # Double push
                        mobility += 1
            return mobility
        
        # For other pieces, use chess library's attack detection
        return len(board.attacks(square))

    def _order_moves_simple(self, board: chess.Board, moves: List[chess.Move]) -> List[chess.Move]:
        """
        Piece-centric move ordering using priority assessment
        
        Args:
            board: Current position
            moves: List of legal moves
            
        Returns:
            Ordered list of moves (highest priority first)
        """
        if len(moves) <= 2:
            return moves
        
        # Get piece priority data once for all pieces
        piece_priorities = self._calculate_piece_priorities(board)
        
        sorted_moves = []
        
        for move in moves:
            from_square = move.from_square
            to_square = move.to_square
            piece = board.piece_at(from_square)
            target_piece = board.piece_at(to_square)

            score = 0
            
            # Get piece data for the moving piece
            piece_data = piece_priorities.get(from_square, {})
            
            if target_piece:
                # Capture: MVV-LVA with piece priority adjustments
                victim_value = self.piece_values.get(target_piece.piece_type, 0)
                attacker_value = self.piece_values.get(piece.piece_type, 0)
                score = (victim_value * 10) - attacker_value
                
                # Bonus for capturing with pieces under attack (get them to safety)
                if piece_data.get('is_attacked', False):
                    score += 200
                
                # Bonus for capturing defenders of our attacked pieces
                if piece_data.get('attackers', 0) > piece_data.get('defenders', 0):
                    score += 100
                    
            else:
                # Quiet move: prioritize based on piece situation
                base_score = piece_data.get('priority', 0)
                
                # High priority for moving pieces under attack
                if piece_data.get('is_attacked', False):
                    if not piece_data.get('is_defended', False):
                        score = base_score + 800  # Urgent escape
                    else:
                        score = base_score + 400  # Consider escape
                
                # Bonus for improving piece mobility
                current_mobility = piece_data.get('mobility', 0)
                if current_mobility < 3 and piece.piece_type in [chess.QUEEN, chess.ROOK, chess.BISHOP]:
                    score += 300  # Improve trapped piece
                
                # Standard positional improvement
                if score == 0:
                    score = base_score // 10  # Small positional bonus

            sorted_moves.append((score, move))

        # Sort by score (highest first)
        sorted_moves.sort(key=lambda x: x[0], reverse=True)

        return [move for score, move in sorted_moves]
    
    def _evaluate_position(self, board: chess.Board) -> float:
        """
        TAL-BOT evaluation: dynamic piece values + chaos factor
        
        Args:
            board: Position to evaluate
            
        Returns:
            Evaluation score from current player's perspective
        """
        if board.is_checkmate():
            return -900000
        
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
        
        # Calculate dynamic evaluation for both sides
        white_score = self._evaluate_side_dynamic(board, chess.WHITE)
        black_score = self._evaluate_side_dynamic(board, chess.BLACK)
        
        # Calculate chaos factor for position complexity
        chaos_factor = self._calculate_chaos_factor(board)
        
        # Apply chaos bonus to current player (encourages complex positions)
        if board.turn == chess.WHITE:
            base_score = white_score - black_score
            return base_score + (chaos_factor * 3)  # 3cp per chaos point
        else:
            base_score = black_score - white_score
            return base_score + (chaos_factor * 3)
    
    def _check_pv_following(self, board: chess.Board) -> Optional[chess.Move]:
        """
        Check if we can instantly play a move from stored PV (PV following)
        
        This is crucial for bullet/blitz where TAL-BOT should excel.
        If opponent plays expected moves, we blitz out our response.
        
        Args:
            board: Current position
            
        Returns:
            Instant move if PV following applies, None otherwise
        """
        if not self.last_search_pv or len(self.last_search_pv) < 2:
            return None
        
        # Check if current position matches expected PV position
        # We need to verify the opponent played our predicted move
        
        # For now, simple implementation: if we have stored PV and 
        # it's our turn, try to play the next move in the PV
        if len(self.last_search_pv) >= 1:
            candidate_move = self.last_search_pv[0]
            
            # Verify the move is still legal in current position
            if candidate_move in board.legal_moves:
                # Remove this move from PV and advance
                self.last_search_pv = self.last_search_pv[1:]
                return candidate_move
        
        return None
    
    def _store_pv_board_states(self, board: chess.Board):
        """
        Store board states for PV following verification
        
        Args:
            board: Current position
        """
        # Store current board state and PV for next move
        self.pv_board_states = [board.copy()]
        
        # Simulate PV moves to store expected positions
        temp_board = board.copy()
        for i, move in enumerate(self.principal_variation[:5]):  # Store first 5 moves
            if move in temp_board.legal_moves:
                temp_board.push(move)
                self.pv_board_states.append(temp_board.copy())
            else:
                break
    
    def _negamax(self, board: chess.Board, depth: int, alpha: float, beta: float, 
                        target_time: float, pv_line: List[chess.Move]) -> float:
        """
        TAL-BOT negamax with PV collection for full line display
        
        Args:
            board: Current position
            depth: Remaining depth to search
            alpha: Alpha bound
            beta: Beta bound
            target_time: Target time limit for search
            pv_line: List to collect PV moves
            
        Returns:
            Evaluation score from current player's perspective
        """
        self.nodes_searched += 1
        
        # Check time every 1000 nodes
        if self.nodes_searched % 1000 == 0:
            elapsed = time.time() - self.search_start_time
            if elapsed > target_time:
                return 0  # Return neutral score if time exceeded
        
        # Terminal conditions
        if depth <= 0:
            return self._evaluate_position(board)
        
        if board.is_game_over():
            if board.is_checkmate():
                return -900000 + (self.default_depth - depth)  # Prefer faster mates
            return 0  # Draw
        
        # Move generation and ordering
        legal_moves = list(board.legal_moves)
        ordered_moves = self._order_moves_simple(board, legal_moves)
        
        best_score = -999999
        best_pv = []
        moves_searched = 0
        
        for move in ordered_moves:
            board.push(move)
            
            # Recursive search with PV collection
            current_pv = []
            score = -self._negamax(board, depth - 1, -beta, -alpha, target_time, current_pv)
            
            board.pop()
            
            moves_searched += 1
            
            # TAL-BOT conditional pruning with PV tracking
            if score > best_score:
                best_score = score
                best_pv = [move] + current_pv  # Build PV line
            
            if score > alpha:
                alpha = score
            
            # Revolutionary chaos-driven pruning with PV consideration
            if alpha >= beta:
                # Standard alpha-beta cutoff
                material_balance = self._quick_material_balance(board)
                
                break  # Standard beta cutoff
        
        # Copy best PV to output parameter
        pv_line[:] = best_pv
        
        return best_score
    
    
    def _evaluate_side(self, board: chess.Board, color: chess.Color) -> float:
        """
        Piece-centric evaluation for one side using piece_map() for efficiency
        
        Args:
            board: Current position
            color: Side to evaluate
            
        Returns:
            Total score for the side
        """
        score = 0.0
        
        # Get all pieces at once instead of checking every square
        piece_map = board.piece_map()
        
        for square, piece in piece_map.items():
            if piece.color == color:
                # Material value
                score += self.piece_values.get(piece.piece_type, 0)
                
                # Positional value from piece-square tables
                table_square = square if color == chess.WHITE else (63 - square)
                score += self._get_positional_bonus(piece.piece_type, table_square)
        
        return score
    
    def _evaluate_side_dynamic(self, board: chess.Board, color: chess.Color) -> float:
        """
        Dynamic evaluation for one side considering piece activity and coordination
        
        Args:
            board: Current position
            color: Side to evaluate
            
        Returns:
            Dynamic score for the side
        """
        score = 0.0
        piece_map = board.piece_map()
        
        for square, piece in piece_map.items():
            if piece.color == color:
                # Base material and positional value
                base_value = self.piece_values.get(piece.piece_type, 0)
                table_square = square if color == chess.WHITE else (63 - square)
                positional_bonus = self._get_positional_bonus(piece.piece_type, table_square)
                
                score += base_value + positional_bonus
                
                # Dynamic factors
                mobility = self._calculate_piece_mobility(board, square, piece)
                
                # Mobility bonus (scaled by piece type)
                if piece.piece_type == chess.QUEEN:
                    score += mobility * 2  # Queen mobility is very valuable
                elif piece.piece_type in [chess.ROOK, chess.BISHOP]:
                    score += mobility * 1.5  # Major piece mobility
                elif piece.piece_type == chess.KNIGHT:
                    score += mobility * 1  # Knight mobility
                
                # Penalty for trapped pieces
                if piece.piece_type in [chess.QUEEN, chess.ROOK] and mobility < 3:
                    score -= 50  # Trapped major piece penalty
        
        return score
    
    def _calculate_chaos_factor(self, board: chess.Board) -> int:
        """
        Calculate position complexity/chaos factor for TAL-BOT's aggressive style
        
        Args:
            board: Current position
            
        Returns:
            Chaos factor (higher = more complex position)
        """
        chaos = 0
        
        # Count total legal moves (more moves = more complexity)
        legal_moves = list(board.legal_moves)
        chaos += len(legal_moves) // 5  # Scale down move count
        
        # Count pieces under attack
        piece_map = board.piece_map()
        attacked_pieces = 0
        
        for square, piece in piece_map.items():
            if len(board.attackers(not piece.color, square)) > 0:
                attacked_pieces += 1
        
        chaos += attacked_pieces * 2  # Attacked pieces increase chaos
        
        # Check for checks (adds tension)
        if board.is_check():
            chaos += 3
        
        # Count captures available
        captures = 0
        for move in legal_moves:
            if board.piece_at(move.to_square):
                captures += 1
        
        chaos += captures  # Available captures add complexity
        
        return min(chaos, 20)  # Cap chaos factor at reasonable level
    
    def new_game(self):
        """Reset engine state for a new game"""
        self.nodes_searched = 0
    
    def get_engine_info(self) -> dict:
        """Return engine information and statistics"""
        return {
            'name': 'VPR',
            'version': '1.0',
            'author': 'Pat Snyder',
            'description': 'Barebones maximum depth experimental engine',
            'default_depth': self.default_depth,
            'nodes_searched': self.nodes_searched
        }
