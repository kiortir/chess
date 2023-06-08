from typing import Literal, Self
from enum import Enum
import math


class Side(Enum):
    WHITE = "white"
    BLACK = "black"


class PieceType(Enum):
    PAWN = "pawn"
    ROOK = "rook"
    KNIGHT = "knight"
    BISHOP = "bishop"
    KING = "king"
    QUEEN = "queen"


class Board:
    def __init__(self):
        self.pieces: list[ChessPiece] = [
            Rook(side=Side.WHITE, coordinates=Coordinate("A", 1))
        ]

    def map_coordinates(self):
        """
        {
            "A1": {
                "type": # rook
                "side": # white
            }
        }
        """
        piece_map = {}
        for piece in self.pieces:
            piece_map[str(piece.coordinates)] = {
                "type": piece.type.value,
                "side": piece.side.value,
            }
        return piece_map


class Coordinate:
    def __init__(
        self,
        column: Literal["A", "B", "C", "D", "E", "F", "G", "H"],
        row: Literal[1, 2, 3, 4, 5, 6, 7, 8],
    ) -> None:
        self.column = column
        self.row = row

        if self.column not in {"A", "B", "C", "D", "E", "F", "G", "H"}:
            raise ValueError("Такого столбца не существует")
        if not (1 <= self.row <= 8):
            raise ValueError("Такой строки не существует")

    def is_same_line(self, other: Self):
        return self.column == other.column or self.row == other.row

    def is_same_diagonal(self, other: Self):
        row_offset = other.row - self.row
        column_offset = int(other.column, 18) - int(self.column, 18)
        return row_offset == column_offset

    def __str__(self):
        return f"{self.column}{self.row}"


class ChessPiece:
    def __init__(self, side: Side, coordinates: Coordinate):
        self.coordinates = coordinates
        self.side = side
        self.type = PieceType(self.__class__.__name__.lower())

    # def __eq__(self, __value: Self) -> bool:
    #     return self.type == __value.type and self.co

    def move(self, destination: Coordinate):
        self.coordinates = destination
        print(f"Передвинули фигуру на {destination}")


class Rook(ChessPiece):
    def move(self, destination: Coordinate):
        start = self.coordinates
        end = destination

        if start.is_same_line(end):
            super().move(destination)
        else:
            raise ValueError("Ладья так не ходит")


class Bishop(ChessPiece):
    def move(self, destination: Coordinate):
        start = self.coordinates
        end = destination

        if start.is_same_diagonal(end):
            super().move(destination)
        else:
            raise ValueError("Слон так не ходит")
