#!/usr/bin/env python3
"""
Engine Comparison Test Suite
Compare VPR (piece-focused, dynamic potential) vs V7P3R v12.6 (full engine)
"""

import chess
import chess.engine
import time
import sys
import os
import subprocess
import threading
from typing import Optional, Dict, List, Tuple

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from vpr import VPREngine

class EngineComparison:
    def __init__(self, v7p3r_path: str):
        """
        Initialize engine comparison
        
        Args:
            v7p3r_path: Path to V7P3R_v12.6.exe
        """
        self.v7p3r_path = v7p3r_path
        self.vpr_engine = VPREngine()
        self.results = {
            'vpr': {'wins': 0, 'losses': 0, 'draws': 0, 'total_time': 0, 'total_nodes': 0},
            'v7p3r': {'wins': 0, 'losses': 0, 'draws': 0, 'total_time': 0, 'total_nodes': 0}
        }
    
    def test_engine_communication(self):
        """Test that we can communicate with V7P3R"""
        print("=== Testing Engine Communication ===")
        
        try:
            # Test VPR
            board = chess.Board()
            start_time = time.time()
            vpr_move = self.vpr_engine.search(board, time_limit=1.0, depth=3)
            vpr_time = time.time() - start_time
            
            print(f"✅ VPR: Move {vpr_move} in {vpr_time:.3f}s")
            
            # Test V7P3R
            with chess.engine.SimpleEngine.popen_uci(self.v7p3r_path) as v7p3r:
                start_time = time.time()
                result = v7p3r.play(board, chess.engine.Limit(time=1.0))
                v7p3r_time = time.time() - start_time
                
                print(f"✅ V7P3R: Move {result.move} in {v7p3r_time:.3f}s")
                print(f"  Info: {v7p3r.id}")
                
                return True
                
        except Exception as e:
            print(f"❌ Engine communication failed: {e}")
            return False
    
    def analyze_position(self, fen: str, time_limit: float = 2.0) -> Dict:
        """
        Analyze a position with both engines
        
        Args:
            fen: Position to analyze
            time_limit: Time limit for analysis
            
        Returns:
            Analysis results from both engines
        """
        board = chess.Board(fen)
        results = {}
        
        # Analyze with VPR
        print(f"\nAnalyzing: {fen}")
        print("VPR Analysis:")
        
        start_time = time.time()
        vpr_move = self.vpr_engine.search(board, time_limit=time_limit)
        vpr_time = time.time() - start_time
        
        # Get VPR's piece analysis
        piece_priorities = self.vpr_engine._calculate_piece_priorities(board)
        vpr_eval = self.vpr_engine._evaluate_position(board)
        
        results['vpr'] = {
            'move': vpr_move,
            'time': vpr_time,
            'nodes': self.vpr_engine.nodes_searched,
            'eval': vpr_eval,
            'nps': int(self.vpr_engine.nodes_searched / vpr_time) if vpr_time > 0 else 0
        }
        
        print(f"  Best move: {vpr_move}")
        print(f"  Evaluation: {vpr_eval:.2f}")
        print(f"  Time: {vpr_time:.3f}s")
        print(f"  Nodes: {self.vpr_engine.nodes_searched}")
        print(f"  NPS: {results['vpr']['nps']}")
        
        # Show top priority pieces
        sorted_pieces = sorted(piece_priorities.items(), key=lambda x: x[1]['priority'], reverse=True)
        print("  Top priority pieces:")
        for square, data in sorted_pieces[:3]:
            piece = data['piece']
            print(f"    {piece.symbol()} on {chess.square_name(square)}: priority={data['priority']:.0f}")
        
        # Analyze with V7P3R
        print("\nV7P3R Analysis:")
        try:
            with chess.engine.SimpleEngine.popen_uci(self.v7p3r_path) as v7p3r:
                start_time = time.time()
                info = v7p3r.analyse(board, chess.engine.Limit(time=time_limit))
                v7p3r_time = time.time() - start_time
                
                results['v7p3r'] = {
                    'move': info['pv'][0] if 'pv' in info and info['pv'] else None,
                    'time': v7p3r_time,
                    'nodes': info.get('nodes', 0),
                    'eval': info.get('score', chess.engine.PovScore(chess.engine.Cp(0), chess.WHITE)).relative.score(mate_score=10000),
                    'depth': info.get('depth', 0),
                    'pv': info.get('pv', [])[:5]  # First 5 moves of PV
                }
                
                print(f"  Best move: {results['v7p3r']['move']}")
                print(f"  Evaluation: {results['v7p3r']['eval']}")
                print(f"  Depth: {results['v7p3r']['depth']}")
                print(f"  Time: {v7p3r_time:.3f}s")
                print(f"  Nodes: {results['v7p3r']['nodes']}")
                print(f"  NPS: {int(results['v7p3r']['nodes'] / v7p3r_time) if v7p3r_time > 0 else 0}")
                print(f"  PV: {' '.join(str(move) for move in results['v7p3r']['pv'])}")
                
        except Exception as e:
            print(f"❌ V7P3R analysis failed: {e}")
            results['v7p3r'] = None
        
        return results
    
    def play_game(self, time_per_move: float = 3.0, max_moves: int = 100) -> str:
        """
        Play a game between VPR and V7P3R
        
        Args:
            time_per_move: Time limit per move
            max_moves: Maximum number of moves
            
        Returns:
            Game result ('vpr', 'v7p3r', 'draw')
        """
        board = chess.Board()
        moves_played = 0
        
        print(f"\n=== Playing Game (VPR as White vs V7P3R as Black) ===")
        print(f"Time per move: {time_per_move}s, Max moves: {max_moves}")
        
        try:
            with chess.engine.SimpleEngine.popen_uci(self.v7p3r_path) as v7p3r:
                while not board.is_game_over() and moves_played < max_moves:
                    move_start = time.time()
                    
                    if board.turn == chess.WHITE:
                        # VPR's turn (White)
                        move = self.vpr_engine.search(board, time_limit=time_per_move)
                        move_time = time.time() - move_start
                        
                        print(f"{moves_played//2 + 1}. {move} (VPR, {move_time:.2f}s)")
                        self.results['vpr']['total_time'] += move_time
                        self.results['vpr']['total_nodes'] += self.vpr_engine.nodes_searched
                        
                    else:
                        # V7P3R's turn (Black)
                        result = v7p3r.play(board, chess.engine.Limit(time=time_per_move))
                        move = result.move
                        move_time = time.time() - move_start
                        
                        print(f"{moves_played//2 + 1}... {move} (V7P3R, {move_time:.2f}s)")
                        self.results['v7p3r']['total_time'] += move_time
                    
                    if move in board.legal_moves:
                        board.push(move)
                        moves_played += 1
                    else:
                        print(f"❌ Illegal move: {move}")
                        return 'error'
                    
                    # Print position every 10 moves
                    if moves_played % 10 == 0:
                        print(f"Position after {moves_played} moves: {board.fen()}")
        
        except Exception as e:
            print(f"❌ Game error: {e}")
            return 'error'
        
        # Determine result
        if board.is_checkmate():
            winner = 'v7p3r' if board.turn == chess.WHITE else 'vpr'
            print(f"🏆 {winner.upper()} wins by checkmate!")
            return winner
        elif board.is_stalemate() or board.is_insufficient_material():
            print("🤝 Draw!")
            return 'draw'
        elif moves_played >= max_moves:
            print("🕐 Draw by move limit!")
            return 'draw'
        else:
            print("🤷 Game ended unexpectedly")
            return 'draw'
    
    def tactical_test_suite(self):
        """Test both engines on tactical positions"""
        print("\n=== Tactical Test Suite ===")
        
        # Famous tactical positions
        tactical_positions = [
            {
                "name": "Fork opportunity",
                "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p3/4P3/3P1N2/PPP2PPP/RNBQKB1R w KQkq - 0 4",
                "best_moves": ["Ng5", "Nh4"],  # Knight moves creating threats
                "description": "Knight can create tactical threats"
            },
            {
                "name": "Pin tactic",
                "fen": "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 4",
                "best_moves": ["Bxf7+", "Ng5"],  # Tactical shots
                "description": "Bishop can give check, knight can attack"
            },
            {
                "name": "Piece under attack",
                "fen": "rnbqkb1r/pp3ppp/2p2n2/3pp3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 5",
                "best_moves": ["Bb3", "Bd5", "Ba6", "Bb5"],  # Bishop escapes
                "description": "Bishop must escape from pawn attack"
            }
        ]
        
        for test in tactical_positions:
            print(f"\n--- {test['name']} ---")
            print(f"Description: {test['description']}")
            
            results = self.analyze_position(test['fen'], time_limit=3.0)
            
            # Check if engines found good moves
            print(f"\nExpected good moves: {test['best_moves']}")
            
            if 'vpr' in results:
                vpr_move_str = str(results['vpr']['move'])
                vpr_found_good = any(vpr_move_str.startswith(move.lower()) for move in test['best_moves'])
                print(f"VPR found good move: {'✅' if vpr_found_good else '❌'}")
            
            if 'v7p3r' in results and results['v7p3r']:
                v7p3r_move_str = str(results['v7p3r']['move'])
                v7p3r_found_good = any(v7p3r_move_str.startswith(move.lower()) for move in test['best_moves'])
                print(f"V7P3R found good move: {'✅' if v7p3r_found_good else '❌'}")
    
    def performance_comparison(self):
        """Compare performance metrics"""
        print("\n=== Performance Comparison ===")
        
        test_positions = [
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",  # Starting position
            "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 4",  # Middlegame
            "8/8/8/4k3/8/4K3/8/8 w - - 0 1"  # Endgame
        ]
        
        position_names = ["Opening", "Middlegame", "Endgame"]
        time_controls = [1.0, 2.0, 5.0]  # Different time controls
        
        for i, fen in enumerate(test_positions):
            print(f"\n--- {position_names[i]} Performance ---")
            
            for time_limit in time_controls:
                print(f"\nTime limit: {time_limit}s")
                results = self.analyze_position(fen, time_limit)
                
                if 'vpr' in results and 'v7p3r' in results and results['v7p3r']:
                    vpr_nps = results['vpr']['nps']
                    v7p3r_nps = int(results['v7p3r']['nodes'] / results['v7p3r']['time']) if results['v7p3r']['time'] > 0 else 0
                    
                    print(f"  NPS Comparison: VPR={vpr_nps}, V7P3R={v7p3r_nps}")
                    print(f"  Nodes: VPR={results['vpr']['nodes']}, V7P3R={results['v7p3r']['nodes']}")
                    print(f"  Depth: VPR=?, V7P3R={results['v7p3r']['depth']}")
    
    def print_final_summary(self):
        """Print final comparison summary"""
        print("\n" + "="*60)
        print("FINAL ENGINE COMPARISON SUMMARY")
        print("="*60)
        
        print("\n🏆 Game Results:")
        total_games = sum(self.results['vpr'].values()) - self.results['vpr']['total_time'] - self.results['vpr']['total_nodes']
        if total_games > 0:
            print(f"  VPR: {self.results['vpr']['wins']} wins, {self.results['vpr']['losses']} losses, {self.results['vpr']['draws']} draws")
            print(f"  V7P3R: {self.results['v7p3r']['wins']} wins, {self.results['v7p3r']['losses']} losses, {self.results['v7p3r']['draws']} draws")
        else:
            print("  No completed games")
        
        print("\n⚡ Performance Metrics:")
        if self.results['vpr']['total_time'] > 0:
            avg_vpr_nps = int(self.results['vpr']['total_nodes'] / self.results['vpr']['total_time'])
            print(f"  VPR average NPS: {avg_vpr_nps}")
        
        print("\n🧠 Engine Characteristics:")
        print("  VPR (Your Engine):")
        print("    + Piece-focused, human-like thinking")
        print("    + Dynamic piece potential evaluation")
        print("    + Tactical threat prioritization")
        print("    + Lightweight and fast move generation")
        
        print("  V7P3R v12.6 (Full Engine):")
        print("    + Mature, optimized engine")
        print("    + Deep search capabilities")
        print("    + Advanced pruning and evaluation")
        print("    + Years of development and tuning")

def main():
    """Run engine comparison"""
    v7p3r_path = "V7P3R_v12.6.exe"
    
    # Check if V7P3R exists
    if not os.path.exists(v7p3r_path):
        print(f"❌ Could not find {v7p3r_path}")
        print("Please make sure V7P3R_v12.6.exe is in the current directory")
        return
    
    comparison = EngineComparison(v7p3r_path)
    
    print("VPR vs V7P3R Engine Comparison")
    print("=" * 50)
    
    # Test communication
    if not comparison.test_engine_communication():
        return
    
    # Run tactical tests
    comparison.tactical_test_suite()
    
    # Run performance comparison
    comparison.performance_comparison()
    
    # Optional: Play a game (uncomment if you want to play full games)
    # print("\nWould you like to play a game between the engines? (y/n)")
    # if input().lower().startswith('y'):
    #     result = comparison.play_game(time_per_move=2.0, max_moves=80)
    #     if result in ['vpr', 'v7p3r']:
    #         comparison.results[result]['wins'] += 1
    #         comparison.results['vpr' if result == 'v7p3r' else 'v7p3r']['losses'] += 1
    #     elif result == 'draw':
    #         comparison.results['vpr']['draws'] += 1
    #         comparison.results['v7p3r']['draws'] += 1
    
    # Print final summary
    comparison.print_final_summary()

if __name__ == "__main__":
    main()