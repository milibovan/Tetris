maxUtility = 1e5
minUtility = 1e5
maxDepth = 3


def evaluate(tetris, depth):
    if tetris.is_game_over() or depth == maxDepth:
        return utility(tetris), None

    if tetris.tetromino is None:
        return 0, None

    best_score = -float('inf')
    best_move = None
    for move in tetris.get_legal_moves():
        updated_board = tetris.copy()
        updated_board.tetromino.move_to_position(move)
        updated_board.update()
        score, _ = evaluate(updated_board, depth+1)
        if score > best_score:
            best_score = score
            best_move = move
    return best_score, best_move


def utility(tetris):
    if tetris.is_game_over():
        return minUtility

    holes = tetris.count_holes()
    landing_height = tetris.get_landing_height()
    eroded_cells = tetris.count_erroded_cells()
    cumulative_wells = tetris.calculate_cumulative_wells()
    row_transitions = tetris.count_row_transitions()
    column_transitions = tetris.count_column_transitions()

    utility_value = -4 * holes - cumulative_wells - row_transitions - column_transitions - landing_height + eroded_cells

    if utility_value < minUtility or utility_value > maxUtility:
        raise ValueError(f"Invalid utility {utility_value} returned")

    print(utility_value)
    return utility_value
