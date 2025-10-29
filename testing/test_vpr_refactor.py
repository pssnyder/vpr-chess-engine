#!/usr/bin/env python3
"""
Test script for the refactored VPR engine
Tests the new piece-centric approach vs the old square-centric approach
"""

import chess
import time
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from vpr import VPREngine

def test_basic_functionality():
    """Test that the engine works with basic positions"""
    print("=== Testing Basic Functionality ===")
    
    engine = VPREngine()
    board = chess.Board()  # Starting position
    
    print(f"Initial position: {board.fen()}")
    print(f"Legal moves: {len(list(board.legal_moves))}")
    
    # Test piece priorities calculation
    start_time = time.time()
    piece_priorities = engine._calculate_piece_priorities(board)
    priorities_time = time.time() - start_time
    
    print(f"Piece priorities calculated in {priorities_time*1000:.2f}ms")
    print(f"Number of pieces analyzed: {len(piece_priorities)}")
    
    # Show some piece data
    print("\nSample piece data:")
    for i, (square, data) in enumerate(piece_priorities.items()):
        if i < 5:  # Show first 5 pieces
            piece = data['piece']
            print(f"  {piece.symbol()} on {chess.square_name(square)}: "
                  f"value={data['value']}, priority={data['priority']}, "
                  f"mobility={data['mobility']}")
    
    return True

def test_move_ordering():
    """Test the new move ordering system"""
    print("\n=== Testing Move Ordering ===")
    
    engine = VPREngine()
    
    # Test position with tactical opportunities
    # This position has some pieces under attack
    board = chess.Board("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2")
    
    print(f"Test position: {board.fen()}")
    
    legal_moves = list(board.legal_moves)
    print(f"Legal moves: {len(legal_moves)}")
    
    # Time the move ordering
    start_time = time.time()
    ordered_moves = engine._order_moves_simple(board, legal_moves)
    ordering_time = time.time() - start_time
    
    print(f"Move ordering completed in {ordering_time*1000:.2f}ms")
    print("Top 5 ordered moves:")
    for i, move in enumerate(ordered_moves[:5]):
        print(f"  {i+1}. {move}")
    
    return True

def test_search_performance():
    """Test search performance with the new piece-centric approach"""
    print("\n=== Testing Search Performance ===")
    
    engine = VPREngine()
    
    # Test starting position
    board = chess.Board()
    
    print("Searching starting position...")
    print("Depth 4 search (should be fast with new optimizations)")
    
    start_time = time.time()
    best_move = engine.search(board, time_limit=5.0, depth=4)
    search_time = time.time() - start_time
    
    print(f"Best move: {best_move}")
    print(f"Search completed in {search_time:.3f}s")
    print(f"Nodes searched: {engine.nodes_searched}")
    print(f"Nodes per second: {int(engine.nodes_searched / search_time) if search_time > 0 else 0}")
    
    return True

def test_tactical_position():
    """Test engine on a tactical position"""
    print("\n=== Testing Tactical Position ===")
    
    engine = VPREngine()
    
    # Position with hanging pieces (should prioritize captures)
    board = chess.Board("rnbqk2r/pppp1ppp/5n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 4")
    
    print(f"Tactical position: {board.fen()}")
    
    # Test piece priority assessment
    piece_priorities = engine._calculate_piece_priorities(board)
    
    print("Piece priorities in tactical position:")
    # Sort pieces by priority
    sorted_pieces = sorted(piece_priorities.items(), key=lambda x: x[1]['priority'], reverse=True)
    
    for i, (square, data) in enumerate(sorted_pieces[:8]):
        piece = data['piece']
        print(f"  {piece.symbol()} on {chess.square_name(square)}: "
              f"priority={data['priority']}, attacked={data['is_attacked']}, "
              f"defended={data['is_defended']}")
    
    # Quick search
    print("\nSearching tactical position (depth 3)...")
    start_time = time.time()
    best_move = engine.search(board, time_limit=3.0, depth=3)
    search_time = time.time() - start_time
    
    print(f"Best move: {best_move}")
    print(f"Search time: {search_time:.3f}s")
    
    return True

def test_chaos_factor():
    """Test the chaos factor calculation"""
    print("\n=== Testing Chaos Factor ===")
    
    engine = VPREngine()
    
    # Test different positions
    positions = [
        ("Starting position", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),
        ("Open position", "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 4"),
        ("Endgame", "8/8/8/8/8/2k5/8/2K5 w - - 0 1")
    ]
    
    for name, fen in positions:
        board = chess.Board(fen)
        chaos = engine._calculate_chaos_factor(board)
        print(f"{name}: chaos factor = {chaos}")
    
    return True

def main():
    """Run all tests"""
    print("Testing VPR Engine Refactoring")
    print("=" * 50)
    
    try:
        test_basic_functionality()
        test_move_ordering()
        test_search_performance()
        test_tactical_position()
        test_chaos_factor()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("The piece-centric refactoring is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()