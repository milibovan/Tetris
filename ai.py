import math
import pygame
import game

maxUtility = 1e5
minUtility = 1e5

# def evaluate(board, depth, alpha, beta):
#     if depth == 0 or board.GameOver():
#         return utility(board)

#     minEval = maxUtility + 1
#     for tetromino in tetris.Tetrominoes():
#         maxEval = minUtility - 1
#         for rotation in range(tetromino.RotationsCount()):
#             tetrominoWidth = len(ai.matrices[tetromino][rotation][0])
#             for column in range(board.Width() - tetrominoWidth + 1):
#                 newBoard = tetris.NewBoardFromBoard(board)
#                 try:
#                     newBoard.Drop(tetromino, rotation, column)
#                 except:
#                     # newBoard's game has just ended. Ignore.
#                     pass

#                 eval = ai.evaluate(newBoard, depth - 1, alpha, beta)
#                 maxEval = max(maxEval, eval)
#                 alpha = max(alpha, maxEval)
#                 if alpha > beta:
#                     break

#         minEval = min(minEval, maxEval)
#         beta = min(beta, minEval)
#         if alpha > beta:
#             break
#     return minEval


def utility(board):
    if game.game_over == True:
        return minUtility


    #TODO
    #Holes
    #LandingHeight
    #ErodedCells
    #CumulativeWells
    
    columnHeights = board.HeightsByColumn()
    columnHoles = board.HolesByColumn()

    heightsSum = sum(columnHeights)
    heightsDiff = sum(abs(columnHeights[col] - columnHeights[col-1]) for col in range(1, board.Width()))
    holes = sum(columnHoles)

    utility = -0.510066 * heightsSum -0.35663 * holes -0.184483 * heightsDiff

    if utility < minUtility or utility > maxUtility:
        raise ValueError(f"Invalid utility {utility} returned")

    return utility
