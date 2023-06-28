from ctypes import util

import sympy
import game
import board

maxUtility = 1e5
minUtility = 1e5


def evaluate(game, board, depth, alpha, beta):
    if depth == 0 or game.game_over:
        return utility(game, board)

    min_evaluation = maxUtility + 1

    for tetrimino in game.tetriminos:
        max_evaluation = minUtility - 1
        for rotation in range(tetrimino.cells):
            tetrimino_width = tetrimino.get_tetrimino_width()
            for column in range(board.num_cols - tetrimino_width):
                new_board = board.Board(board)
                evaluation = evaluate(game, new_board, depth - 1, alpha, beta)
                max_evaluation = sympy.Max(max_evaluation, evaluation)
                alpha = sympy.Max(alpha, max_evaluation)
                if alpha > beta:
                    break

        min_evaluation = sympy.Min(min_evaluation, max_evaluation)
        beta = sympy.Min(beta, min_evaluation)
        if alpha > beta:
            break

    return min_evaluation


def evaluate_minimax(game, board, tetramino, utility_function, depth, alpha, beta):
    if depth == 0 or board.game_over:
        return utility_function(board)

    if tetramino is None:
        return 0

    if tetramino.id % 2 == 0: 
        best_score = float('-inf')
        for move in game.get_valid_moves(board, tetramino):
            board_copy = board.Board()
            board_copy.grid = [row[:] for row in board.grid]
            board_copy.apply_move(tetramino, move)

            next_tetramino = game.get_random_tetramino() 

            score = evaluate(game, board_copy, next_tetramino, utility_function, depth - 1, alpha, beta)
            best_score = max(best_score, score)
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break

        return best_score

    else: 
        best_score = float('inf')
        for move in game.get_valid_moves(board, tetramino):
            board_copy = board.Board()
            board_copy.grid = [row[:] for row in board.grid]
            board_copy.apply_move(tetramino, move)

            next_tetramino = game.get_random_tetramino()

            score = evaluate(game, board_copy, next_tetramino, utility_function, depth - 1, alpha, beta)
            best_score = min(best_score, score)
            beta = min(beta, best_score)
            if beta <= alpha:
                break

        return best_score


def utility(game, board):
    if game.game_over:
        return minUtility

    holes = board.count_holes()
    landing_height = board.get_landing_height()
    eroded_cells = board.count_erroded_cells()
    cumulative_wells = board.calculate_cumulative_wells()
    row_transitions = board.count_row_transitions()
    column_transitions = board.count_column_transitions()

    utility_value = -4 * holes - cumulative_wells - row_transitions - column_transitions - landing_height + eroded_cells

    if utility_value < minUtility or utility_value > maxUtility:
        raise ValueError(f"Invalid utility {utility_value} returned")

    print(utility_value)
    return utility_value
