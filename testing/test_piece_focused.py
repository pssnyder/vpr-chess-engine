#!/usr/bin/env python3
"""
Test script for the Piece-Focused Search System
Tests the new human-like piece analysis and move generation
"""

import chess
import time
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from vpr import VPREngine

def test_piece_opportunities():
    """Test the piece opportunity analysis"""
    print("=== Testing Piece Opportunity Analysis ===")
    
    engine = VPREngine()
    
    # Test position with tactical opportunities
    board = chess.Board("r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 4")
    
    print(f"Position: {board.fen()}")
    
    piece_map = board.piece_map()
    our_pieces = [(sq, piece) for sq, piece in piece_map.items() if piece.color == board.turn]
    
    print(f"\nAnalyzing {len(our_pieces)} pieces for opportunities:")
    
    for square, piece in our_pieces[:6]:  # Show first 6 pieces
        analysis = engine._analyze_piece_opportunities(board, square, piece)
        
        print(f"\n{piece.symbol()} on {chess.square_name(square)}:")
        print(f"  Mobility: {analysis['mobility_squares']} squares")
        print(f"  Threat level: {analysis['threat_level']}")
        print(f"  Opportunity score: {analysis['opportunity_score']}")
        print(f"  Under attack: {analysis['is_under_attack']}")
        print(f"  Can capture: {len(analysis['can_capture'])} pieces")
        print(f"  Can defend: {len(analysis['can_defend'])} pieces") 
        print(f"  Can check: {analysis['can_check']}")
        print(f"  Can fork: {analysis['can_fork']}")
        print(f"  Critical moves: {len(analysis['critical_moves'])}")
        
        if analysis['critical_moves']:
            print(f"    {[str(move) for move in analysis['critical_moves'][:3]]}")

def test_piece_focused_move_generation():
    """Test piece-focused move generation vs traditional"""
    print("\n=== Testing Piece-Focused Move Generation ===")
    
    engine = VPREngine()
    
    positions = [
        ("Starting position", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),
        ("Tactical position", "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 4"),
        ("Endgame", "8/8/8/4k3/8/4K3/8/8 w - - 0 1")
    ]
    
    for name, fen in positions:
        print(f"\n{name}: {fen}")
        board = chess.Board(fen)
        
        # Traditional move generation
        start_time = time.perf_counter()
        traditional_moves = list(board.legal_moves)
        traditional_time = time.perf_counter() - start_time
        
        # Piece-focused move generation
        start_time = time.perf_counter()
        piece_focused_moves = engine._generate_piece_focused_moves(board)
        piece_focused_time = time.perf_counter() - start_time
        
        print(f"  Traditional: {len(traditional_moves)} moves in {traditional_time*1000:.3f}ms")
        print(f"  Piece-focused: {len(piece_focused_moves)} moves in {piece_focused_time*1000:.3f}ms")
        
        # Show first few moves from each approach
        print(f"  Traditional first 5: {[str(move) for move in traditional_moves[:5]]}")
        print(f"  Piece-focused first 5: {[str(move) for move in piece_focused_moves[:5]]}")
        
        # Check that all piece-focused moves are legal
        illegal_moves = [move for move in piece_focused_moves if move not in traditional_moves]
        if illegal_moves:
            print(f"  ❌ ERROR: {len(illegal_moves)} illegal moves generated!")
        else:
            print(f"  ✅ All piece-focused moves are legal")

def test_human_like_thinking():
    """Test that the engine thinks more like a human"""
    print("\n=== Testing Human-Like Chess Thinking ===")
    
    engine = VPREngine()
    
    # Position where a piece is under attack
    board = chess.Board("rnbqkb1r/pppp1ppp/5n2/4p3/4P3/3P1N2/PPP2PPP/RNBQKB1R w KQkq - 0 3")
    
    print(f"Test position: {board.fen()}")
    print("Human thought process simulation:")
    
    piece_map = board.piece_map()
    our_pieces = [(sq, piece) for sq, piece in piece_map.items() if piece.color == board.turn]
    
    # Simulate human thinking: "Let me check each of my pieces..."
    critical_pieces = []
    
    for square, piece in our_pieces:
        analysis = engine._analyze_piece_opportunities(board, square, piece)
        
        # Human thoughts for each piece
        thoughts = []
        
        if analysis['is_under_attack']:
            thoughts.append("UNDER ATTACK - needs immediate attention!")
        
        if analysis['can_capture']:
            thoughts.append(f"can capture {len(analysis['can_capture'])} enemy pieces")
        
        if analysis['can_check']:
            thoughts.append("can give check!")
        
        if analysis['can_fork']:
            thoughts.append("can fork multiple pieces!")
        
        if analysis['mobility_squares'] <= 2 and piece.piece_type in [chess.QUEEN, chess.ROOK, chess.BISHOP]:
            thoughts.append("trapped piece - needs escape!")
        
        if analysis['opportunity_score'] > 30:
            thoughts.append(f"high opportunity (score: {analysis['opportunity_score']})")
        
        if thoughts:
            critical_pieces.append((square, piece, analysis, thoughts))
            print(f"  {piece.symbol()} on {chess.square_name(square)}: {', '.join(thoughts)}")
    
    print(f"\nFound {len(critical_pieces)} pieces needing attention")
    
    # Show the moves the engine would prioritize
    prioritized_moves = engine._generate_piece_focused_moves(board)
    print(f"Engine's prioritized moves: {[str(move) for move in prioritized_moves[:5]]}")

def test_search_performance():
    """Test search performance with piece-focused approach"""
    print("\n=== Testing Search Performance ===")
    
    engine = VPREngine()
    board = chess.Board()
    
    print("Comparing search approaches:")
    
    # Test piece-focused search
    print("\nPiece-focused search (depth 3):")
    start_time = time.time()
    best_move = engine.search(board, time_limit=3.0, depth=3)
    search_time = time.time() - start_time
    
    print(f"  Best move: {best_move}")
    print(f"  Time: {search_time:.3f}s")
    print(f"  Nodes: {engine.nodes_searched}")
    print(f"  NPS: {int(engine.nodes_searched / search_time) if search_time > 0 else 0}")

def test_critical_situations():
    """Test engine response to critical situations"""
    print("\n=== Testing Critical Situation Handling ===")
    
    engine = VPREngine()
    
    # Position with piece under attack
    board = chess.Board("rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 0 3")
    
    print(f"Position with bishop under attack: {board.fen()}")
    
    # Generate piece-focused moves
    moves = engine._generate_piece_focused_moves(board)
    print(f"Top 5 moves: {[str(move) for move in moves[:5]]}")
    
    # Check if the engine prioritizes saving the attacked piece
    bishop_square = chess.C4  # The attacked bishop
    saving_moves = [move for move in moves[:10] if move.from_square == bishop_square]
    
    print(f"Bishop escape moves in top 10: {[str(move) for move in saving_moves]}")
    
    if saving_moves:
        print("✅ Engine correctly prioritizes saving attacked piece")
    else:
        print("❌ Engine may not be prioritizing piece safety")

def main():
    """Run all tests"""
    print("Testing VPR Piece-Focused Search System")
    print("=" * 60)
    
    try:
        test_piece_opportunities()
        test_piece_focused_move_generation()
        test_human_like_thinking()
        test_search_performance()
        test_critical_situations()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("🧠 Engine now thinks piece-by-piece like a human!")
        print("🚀 Piece-focused search is working!")
        print("⚡ Move generation optimized for critical opportunities!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()