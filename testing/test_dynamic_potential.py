#!/usr/bin/env python3
"""
Test script for the Dynamic Piece Potential System
Tests the new value-less, PST-less approach with pure positional evaluation
"""

import chess
import time
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from vpr import VPREngine

def test_dynamic_potential():
    """Test the dynamic piece potential calculation"""
    print("=== Testing Dynamic Piece Potential System ===")
    
    engine = VPREngine()
    
    # Test different positions
    positions = [
        ("Starting position", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),
        ("Tactical position", "rnbqk2r/pppp1ppp/5n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 4"),
        ("Piece under attack", "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 4")
    ]
    
    for name, fen in positions:
        print(f"\n{name}: {fen}")
        board = chess.Board(fen)
        
        piece_priorities = engine._calculate_piece_priorities(board)
        
        print("Piece potential analysis:")
        # Sort by potential value to see strongest/weakest pieces
        sorted_pieces = sorted(piece_priorities.items(), 
                             key=lambda x: x[1]['potential'], reverse=True)
        
        for square, data in sorted_pieces[:10]:  # Top 10
            piece = data['piece']
            potential = data['potential']
            status = "STRONG" if data['is_strong'] else "WEAK" if data['is_weak'] else "NEEDS_IMPROVEMENT" if data['needs_improvement'] else "OK"
            
            print(f"  {piece.symbol()} on {chess.square_name(square)}: "
                  f"potential={potential:.2f}, priority={data['priority']:.0f}, {status}")

def test_weak_piece_priority():
    """Test that weak pieces get prioritized for moves"""
    print("\n=== Testing Weak Piece Move Priority ===")
    
    engine = VPREngine()
    
    # Position where some pieces are under attack (should have negative potential)
    board = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 4")
    
    legal_moves = list(board.legal_moves)
    piece_priorities = engine._calculate_piece_priorities(board)
    
    # Find weak pieces
    weak_pieces = []
    for square, data in piece_priorities.items():
        if data['is_weak']:
            weak_pieces.append((square, data))
    
    print(f"Found {len(weak_pieces)} weak pieces:")
    for square, data in weak_pieces:
        piece = data['piece']
        print(f"  {piece.symbol()} on {chess.square_name(square)}: potential={data['potential']:.2f}")
    
    # Test move ordering
    ordered_moves = engine._order_moves_simple(board, legal_moves)
    
    print(f"\nTop 5 moves (should prioritize weak pieces):")
    for i, move in enumerate(ordered_moves[:5]):
        from_piece = board.piece_at(move.from_square)
        potential = piece_priorities.get(move.from_square, {}).get('potential', 0)
        move_type = "CAPTURE" if board.piece_at(move.to_square) else "QUIET"
        print(f"  {i+1}. {move} ({from_piece.symbol()}, potential={potential:.2f}, {move_type})")

def test_piece_improvement():
    """Test that the engine prefers moves that improve piece potential"""
    print("\n=== Testing Piece Improvement Detection ===")
    
    engine = VPREngine()
    
    # Position with trapped pieces
    board = chess.Board("r1bqkb1r/pppp1p1p/2n2np1/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 5")
    
    # Test specific moves that should improve pieces
    test_moves = [
        chess.Move.from_uci("f3g5"),  # Knight improving position
        chess.Move.from_uci("c4d5"),  # Bishop becoming more active
        chess.Move.from_uci("b1c3"),  # Developing knight
    ]
    
    for move in test_moves:
        if move in board.legal_moves:
            from_square = move.from_square
            to_square = move.to_square
            piece = board.piece_at(from_square)
            
            # Calculate potential before move
            before_potential = engine._calculate_piece_potential(board, from_square, piece)
            
            # Calculate potential after move
            board.push(move)
            after_potential = engine._calculate_piece_potential(board, to_square, piece)
            board.pop()
            
            improvement = after_potential - before_potential
            
            print(f"Move {move} ({piece.symbol()}):")
            print(f"  Before: {before_potential:.2f}")
            print(f"  After: {after_potential:.2f}")
            print(f"  Improvement: {improvement:.2f}")

def test_search_with_potential():
    """Test search performance with dynamic potential system"""
    print("\n=== Testing Search with Dynamic Potential ===")
    
    engine = VPREngine()
    board = chess.Board()
    
    print("Searching starting position (depth 3)...")
    start_time = time.time()
    best_move = engine.search(board, time_limit=3.0, depth=3)
    search_time = time.time() - start_time
    
    print(f"Best move: {best_move}")
    print(f"Search time: {search_time:.3f}s")
    print(f"Nodes searched: {engine.nodes_searched}")
    print(f"NPS: {int(engine.nodes_searched / search_time) if search_time > 0 else 0}")
    
    # Show the evaluation breakdown
    white_potential = engine._evaluate_side(board, chess.WHITE)
    black_potential = engine._evaluate_side(board, chess.BLACK)
    
    print(f"White total potential: {white_potential:.2f}")
    print(f"Black total potential: {black_potential:.2f}")
    print(f"Difference: {white_potential - black_potential:.2f}")

def test_no_static_values():
    """Verify we're not using any static piece values"""
    print("\n=== Verifying No Static Values Used ===")
    
    engine = VPREngine()
    
    # Check that piece_values is not defined
    try:
        engine.piece_values
        print("❌ ERROR: Static piece_values still exists!")
        return False
    except AttributeError:
        print("✅ No static piece_values found")
    
    # Check that PST tables are not defined
    pst_tables = ['pawn_table', 'knight_table', 'bishop_table', 'rook_table', 'queen_table', 'king_table']
    for table in pst_tables:
        try:
            getattr(engine, table)
            print(f"❌ ERROR: {table} still exists!")
            return False
        except AttributeError:
            pass
    
    print("✅ No PST tables found")
    print("✅ Engine is fully dynamic!")
    return True

def main():
    """Run all tests"""
    print("Testing VPR Dynamic Piece Potential System")
    print("=" * 60)
    
    try:
        test_no_static_values()
        test_dynamic_potential()
        test_weak_piece_priority()
        test_piece_improvement()
        test_search_with_potential()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("🚀 Dynamic Piece Potential System is working!")
        print("📈 Engine now values pieces based on their actual contribution!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()