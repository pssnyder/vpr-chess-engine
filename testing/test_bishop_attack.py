#!/usr/bin/env python3
"""
Quick test of the specific position with bishop under attack
"""

import chess
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from vpr import VPREngine

def test_bishop_under_attack():
    """Test the specific position where bishop is under attack"""
    print("=== Testing Bishop Under Attack Position ===")
    
    engine = VPREngine()
    
    # Position where bishop on c4 is attacked by pawn on d5
    board = chess.Board("rnbqkb1r/pp3ppp/2p2n2/3pp3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq d6 0 5")
    
    print(f"Position: {board.fen()}")
    print("White bishop on c4 is under attack by black pawn on d5")
    
    # Check if the bishop is actually under attack
    bishop_square = chess.C4
    attackers = board.attackers(chess.BLACK, bishop_square)
    
    print(f"\nAttackers of bishop on c4: {len(attackers)}")
    for attacker_square in attackers:
        attacker_piece = board.piece_at(attacker_square)
        print(f"  {attacker_piece.symbol()} on {chess.square_name(attacker_square)}")
    
    # Calculate piece priorities
    piece_priorities = engine._calculate_piece_priorities(board)
    
    # Find the bishop's data
    if bishop_square in piece_priorities:
        bishop_data = piece_priorities[bishop_square]
        print(f"\nBishop analysis:")
        print(f"  Potential: {bishop_data['potential']:.2f}")
        print(f"  Priority: {bishop_data['priority']:.0f}")
        print(f"  Is weak: {bishop_data['is_weak']}")
        print(f"  Attackers: {bishop_data['attackers']}")
        print(f"  Opportunity score: {bishop_data.get('opportunity_score', 0)}")
    
    # Check piece-focused move generation
    moves = engine._generate_piece_focused_moves(board)
    
    print(f"\nTop 10 moves from piece-focused generation:")
    bishop_moves = []
    for i, move in enumerate(moves[:10]):
        from_square = move.from_square
        piece = board.piece_at(from_square)
        move_type = "CAPTURE" if board.piece_at(move.to_square) else "QUIET"
        
        if from_square == bishop_square:
            bishop_moves.append(move)
        
        print(f"{i+1:2d}. {move} ({piece.symbol()}, {move_type})")
    
    print(f"\nBishop escape moves in top 10: {len(bishop_moves)}")
    if bishop_moves:
        print(f"Bishop moves: {[str(move) for move in bishop_moves]}")
        print("✅ Engine correctly prioritizes saving the attacked bishop")
    else:
        print("❌ Engine may not be prioritizing bishop safety")
    
    # Test the specific piece analysis for the bishop
    bishop_analysis = engine._analyze_piece_opportunities(board, bishop_square, board.piece_at(bishop_square))
    
    print(f"\nDetailed bishop opportunity analysis:")
    print(f"  Under attack: {bishop_analysis['is_under_attack']}")
    print(f"  Threat level: {bishop_analysis['threat_level']}")
    print(f"  Opportunity score: {bishop_analysis['opportunity_score']}")
    print(f"  Critical moves: {len(bishop_analysis['critical_moves'])}")
    print(f"  Escape squares: {len(bishop_analysis['escape_squares'])}")
    
    if bishop_analysis['critical_moves']:
        print(f"  Critical moves: {[str(move) for move in bishop_analysis['critical_moves']]}")

if __name__ == "__main__":
    test_bishop_under_attack()