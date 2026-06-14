import math
from game_state import State, PlayerColor
from game_engine import GameEngine
from copy import deepcopy

class ExpectiMinimaxPlayer:
    def __init__(self, player_color: PlayerColor, max_depth: int = 3):
        self.player_color = player_color
        self.max_depth = max_depth
        self.game_engine = GameEngine()
        self.probabilities = {1: 4/16, 2: 6/16, 3: 4/16, 4: 1/16, 5: 1/16}
        self.visited_states=0
        
    def find_best_move(self, state:State) -> int:
        if state.current_player != self.player_color:
            raise ValueError("find_best_move should be called when it's the Algorithem's turn")
        self.visited_states=0
        possible_moves = self.game_engine.actions(state)
        if not possible_moves:
            return -1, self.evaluate(state)
        best_move = -1
        best_value = -math.inf  
        # if state.current_player == self.player_color:
        for move in possible_moves:                
            next_state = self.game_engine.transition_model(state, move)
            if next_state is None:
                continue
            # get expected value of the stat  e after move
            value = self.expected_value(next_state, self.max_depth)
            if value > best_value:
                best_value = value
                best_move = move
        return best_move,best_value
        # else:
        #     best_value = math.inf
        #     for move in possible_moves:
        #         next_state = self.game_engine.transition_model(state, move)
        #         if next_state is None:
        #             continue
        #         value = self.expected_value(next_state, self.max_depth)
        #         if value< best_value:
        #             best_value= value
        #             best_move = move
        #     return best_move,best_value
        

    def _is_game_over(self, state: State) -> bool:
        return not state.white_positions or not state.black_positions

    def _get_player_score(self, positions: frozenset) -> float:
        score = 0.0
        House_of_Happiness = 26
        House_of_Water = 27
        House_of_Three = 28 # square you can get stuck in
        House_of_Atom = 29 # square you can get stuck in
        Total_Pawns = 7

        for pawn_pos in positions:
            if pawn_pos == House_of_Water:
                score -= 50

            elif pawn_pos == House_of_Happiness:
                score += 40

            elif pawn_pos == House_of_Three:
                score -= 25
            elif pawn_pos == House_of_Atom:
                score -= 30
            else:
                score += pawn_pos

        pawns_off_board = Total_Pawns - len(positions)
        score += pawns_off_board * 100

        return score
    
    def evaluate(self, state: State) -> float:
        if self._is_game_over(state):
            if not state.black_positions:
                return math.inf if self.player_color == PlayerColor.BLACK else -math.inf
            if not state.white_positions:
                return math.inf if self.player_color == PlayerColor.WHITE else -math.inf
        black_score = self._get_player_score(state.black_positions)
        white_score = self._get_player_score(state.white_positions)
        if self.player_color == PlayerColor.BLACK:
            return black_score - white_score
        else:
            return white_score - black_score
    
    def expected_value(self,state :State, depth :int) ->float:
        total_expected_value = 0.0

        for sticks_roll, probability in self.probabilities.items():
            roll_state = State( 
                white_positions = deepcopy(state.white_positions),
                black_positions = deepcopy(state.black_positions),
                current_player = state.current_player,
                sticks = sticks_roll,
                parent = state.parent

            )

            total_expected_value += self.get_value(roll_state, depth)* probability

        return total_expected_value

    def get_value(self, state: State, depth: int) -> float:
        self.visited_states+=1
        # if depth>0:
            # print("DEPTH:", depth, "PLAYER:", state.current_player)
        if depth <= 0 or self._is_game_over(state):
            # print("LEAF/EVAL depth", depth, "player", state.current_player)
            return self.evaluate(state)
        
        possible_moves = self.game_engine.actions(state)
        
        if not possible_moves:
            next_Player = PlayerColor.WHITE if state.current_player == PlayerColor.BLACK else PlayerColor.BLACK
            skipped_state = State(state.white_positions, state.black_positions, next_Player, 0, state)
            return self.expected_value(skipped_state, depth-1)
        
        # max player's turn
        if state.current_player == self.player_color:
            # print(f"max")
            max_value = -math.inf
            for move in possible_moves:
                next_state = self.game_engine.transition_model(state, move)
                if next_state is None:
                    continue
                value = self.expected_value(next_state, depth-1)
                max_value = max(max_value,value)

            return max_value

        #min player's turn
        else:
            # print(f"min")
            min_value = math.inf
            for move in possible_moves:
                next_state = self.game_engine.transition_model(state, move)
                if next_state is None:
                    continue
                value = self.expected_value(next_state, depth-1)
                min_value = min(min_value, value)

            return min_value
     
    def analysis_inf(self,state:State):
        self.visited_states=0
        best_move,score =self.find_best_move(state)
        if best_move==-1:
            return None
        next_state=self.game_engine.transition_model(state,best_move)
        moved_set = (
        next_state.black_positions - state.black_positions
         if self.player_color == PlayerColor.BLACK
         else next_state.white_positions - state.white_positions
         )
        destenation=moved_set.pop() if moved_set else None
        return{
            "pawn":best_move,
            "score":score,
            "visited":self.visited_states,
            "whereToGo":destenation
        }


def run_ai_tests():
    """
    This function will test the AI's decision-making in various scenarios.
    """
    print("--- RUNNING AI TESTS ---")
    
    # Let's create an AI player for the BLACK pieces
    # We use max_depth=2 for faster testing
    ai_player = ExpectiMinimaxPlayer(player_color=PlayerColor.BLACK, max_depth=2)

    # --- Test Case 1: Obvious Winning Move ---
    # Black has a pawn on square 29. A roll of 2 will move it to 31 (off the board).
    # The other move (25 -> 27) leads to the House of Water (very bad).
    # The AI MUST choose to move pawn 29.
    print("\n--- Test 1: Obvious Winning Move ---")
    state1 = State(
        white_positions={1, 3, 5,7,9,11,13},
        black_positions={25},
        current_player=PlayerColor.WHITE,
        sticks=1 
    )
    best_move1 = ai_player.find_best_move(state1)
    print(f"Board: Black has pawns at {state1.black_positions}. Sticks roll is 2.")
    print(f"AI chose to move pawn: {best_move1}")
    print(f"Expected move: 29. -> {'PASS' if best_move1 == 29 else 'FAIL'}")

    # # --- Test Case 2: Avoid Obvious Trap ---
    # # Black can move pawn 24 to 27 (House of Water) or pawn 10 to 13.
    # # The AI MUST avoid the trap and choose to move pawn 10.
    print("\n--- Test 2: Avoid Obvious Trap ---")
    state2 = State(
        white_positions={1, 2, 3},
        black_positions={10, 24},
        current_player=PlayerColor.BLACK,
        sticks=3
    )
    best_move2 = ai_player.find_best_move(state2)
    print(f"Board: Black has pawns at {state2.black_positions}. Sticks roll is 3.")
    print(f"AI chose to move pawn: {best_move2}")
    print(f"Expected move: 10. -> {'PASS' if best_move2 == 10 else 'FAIL'}")

    # --- Test Case 3: Strategic Choice ---
    # Black can move pawn 23 to 26 (House of Happiness - good bonus)
    # or move pawn 12 to 15 (less optimal).
    # The AI should prefer the strategic bonus and move pawn 23.
    print("\n--- Test 3: Strategic Choice ---")
    state3 = State(
        white_positions={1, 2, 3},
        black_positions={12, 23},
        current_player=PlayerColor.BLACK,
        sticks=3
    )
    best_move3 = ai_player.find_best_move(state3)
    print(f"Board: Black has pawns at {state3.black_positions}. Sticks roll is 3.")
    print(f"AI chose to move pawn: {best_move3}")
    print(f"Expected move: 23. -> {'PASS' if best_move3 == 23 else 'FAIL'}")

# To run the tests, add this line at the very end of the file
if __name__ == "__main__":
    run_ai_tests()
