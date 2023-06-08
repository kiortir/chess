from enum import Enum
from dataclasses import dataclass
from typing import Collection, Union, Literal, Type


class Side(Enum):
    WHITE = "white"
    BLACK = "black"


STATE_TYPE = dict["Coordinate", "Piece"]
CASTLE_TYPES = Literal["Castle", "LongCastle"]


# 1. Состояние доступности рокировок
# 2. Пешки, доступные для взятия на проходе
# 3.
@dataclass
class State:
    coordinates: STATE_TYPE
    avaliable_castles: dict[Side, dict[CASTLE_TYPES, bool]]
    en_passante_pawn: None | "Coordinate"


class Game:
    def __init__(self) -> None:
        self.list_of_moves = []
        self.state: State = State(
            coordinates={},
            avaliable_castles={
                Side.BLACK: {"Castle": True, "LongCastle": True},
                Side.WHITE: {"Castle": True, "LongCastle": True},
            },
            en_passante_pawn=None,
        )
        # self.state: STATE_TYPE = {
        #     Coordinate(0, 0): Knight(Side.WHITE),
        #     Coordinate(0, 1): Rook(Side.BLACK),
        #     Coordinate(1, 0): Rook(Side.BLACK),
        # }

    def get_turn(self) -> Side:
        return Side.WHITE if len(self.list_of_moves) % 2 else Side.BLACK

    def make_move(self, start: "Coordinate", end: "Coordinate"):
        move = (start, end)
        self.list_of_moves.append(move)
        piece = self.state.coordinates.get(start)
        
        
        self.state.coordinates[end] = self.state.coordinates.pop(start)

    def check_moves(self, coordinate: "Coordinate") -> set["PossibleMove"]:
        piece = self.state.coordinates.get(coordinate)
        if not piece:
            return set()

        return piece.get_moves(coordinate, self.state, self.list_of_moves[-1])


@dataclass
class Coordinate:
    x: int
    y: int

    def to_A1(self):
        return "ABCDEFGH"[self.x], self.y + 1

    @classmethod
    def from_tuple(
        cls, coordinate_tuple: tuple[int, int]
    ) -> "Coordinate" | None:
        if len(coordinate_tuple) == 2 and all(
            0 <= coordinate <= 7 for coordinate in coordinate_tuple
        ):
            return cls(*coordinate_tuple)

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, __value: "Coordinate") -> bool:
        return self.x == __value.x and self.y == __value.y

    def get_coordinate_from_disposition(
        self, disposition: tuple[int, int]
    ) -> "Coordinate" | None:
        x, y = disposition
        return self.from_tuple((self.x + x, self.y + y))


PossibleMove = Coordinate | CASTLE_TYPES


class PieceType(Enum):
    PAWN = "pawn"
    ROOK = "rook"
    KNIGHT = "knight"
    BISHOP = "bishop"
    KING = "king"
    QUEEN = "queen"


class Piece:
    def __init__(self, side: Side) -> None:
        self.side = side
        self.type = PieceType(self.__class__.__name__.lower())

    def get_moves(
        self,
        coordinate: Coordinate,
        game_state: STATE_TYPE,
        last_move: tuple[Coordinate, Coordinate],
    ) -> set[PossibleMove]:
        ...

    def get_moves_by_fns(
        self,
        functions: Collection,
        game_state: STATE_TYPE,
        radius: int = 7,
    ) -> set[PossibleMove]:
        moves = set()
        for fn in functions:
            moves_direction = set()
            for i in range(1, radius + 1):
                c = fn(i)
                if not c:
                    break
                obstacle = game_state.get(c)
                if not obstacle:
                    moves_direction.add(c)
                else:
                    if obstacle.side != self.side:
                        moves_direction.add(c)
                    break

            moves |= moves_direction

        return moves

    def get_diagonal_moves(
        self, coordinate: Coordinate, game_state: STATE_TYPE, radius: int = 7
    ):
        def next_top_right(i):
            return Coordinate.from_tuple((coordinate.x + i, coordinate.y + i))

        def next_top_left(i):
            return Coordinate.from_tuple((coordinate.x - i, coordinate.y + i))

        def next_bottom_right(i):
            return Coordinate.from_tuple((coordinate.x + i, coordinate.y - i))

        def next_bottom_left(i):
            return Coordinate.from_tuple((coordinate.x - i, coordinate.y - i))

        return self.get_moves_by_fns(
            (
                next_top_right,
                next_top_left,
                next_bottom_right,
                next_bottom_left,
            ),
            game_state,
            radius,
        )

    def get_straight_moves(
        self, coordinate: Coordinate, game_state: STATE_TYPE, radius: int = 7
    ):
        def next_top(i):
            return Coordinate.from_tuple((coordinate.x, coordinate.y + i))

        def next_bottom(i):
            return Coordinate.from_tuple((coordinate.x, coordinate.y - i))

        def next_right(i):
            return Coordinate.from_tuple((coordinate.x + i, coordinate.y))

        def next_left(i):
            return Coordinate.from_tuple((coordinate.x - i, coordinate.y))

        return self.get_moves_by_fns(
            (next_top, next_bottom, next_left, next_right),
            game_state,
            radius,
        )


class Rook(Piece):
    def get_moves(
        self,
        coordinate: Coordinate,
        game_state: STATE_TYPE,
        last_move: tuple[Coordinate, Coordinate],
    ):
        return self.get_straight_moves(coordinate, game_state)


class Bishop(Piece):
    def get_moves(
        self,
        coordinate: Coordinate,
        game_state: STATE_TYPE,
        last_move: tuple[Coordinate, Coordinate],
    ):
        return self.get_diagonal_moves(coordinate, game_state)


class Queen(Piece):
    def get_moves(
        self,
        coordinate: Coordinate,
        game_state: STATE_TYPE,
        last_move: tuple[Coordinate, Coordinate],
    ):
        return self.get_diagonal_moves(
            coordinate, game_state
        ) | self.get_straight_moves(coordinate, game_state)


class King(Piece):
    def get_moves(
        self,
        coordinate: Coordinate,
        game_state: STATE_TYPE,
        last_move: tuple[Coordinate, Coordinate],
    ):
        return self.get_diagonal_moves(
            coordinate, game_state, radius=1
        ) | self.get_straight_moves(coordinate, game_state, radius=1)


class Knight(Piece):
    dispositions = (
        (2, 1),
        (2, -1),
        (-2, -1),
        (-2, 1),
        (1, 2),
        (1, -2),
        (-1, 2),
        (-1, -2),
    )

    def get_moves(
        self, coordinate: Coordinate, game_state: STATE_TYPE
    ) -> set[Coordinate]:
        moves = set()
        for disposition in self.dispositions:
            c = coordinate.get_coordinate_from_disposition(disposition)
            if not c:
                continue
            obstacle = game_state.get(c)
            if not obstacle:
                moves.add(c)
            else:
                if obstacle.side != self.side:
                    moves.add(c)

        return moves


class Pawn(Piece):
    def get_moves(
        self,
        coordinate: Coordinate,
        game_state: STATE_TYPE,
        last_move: tuple[Coordinate, Coordinate],
    ) -> set[PossibleMove]:
        moves = set()

        is_first_rank = (coordinate.y == 1 and self.side == Side.WHITE) or (
            coordinate.y == 6 and self.side == Side.BLACK
        )
        forward = self.get_straight_moves(
            coordinate, game_state, radius=(2 if is_first_rank else 1)
        )
        potential_kills = [
            coordinate.get_coordinate_from_disposition((-1, 1)),
            coordinate.get_coordinate_from_disposition((1, 1)),
        ]
        for square in potential_kills:
            if not square:
                continue
            obstacle = game_state.get(square)
            if obstacle and obstacle.side != self.side:
                moves.add(square)
        if not is_first_rank:
            is_first_enemy_rank = (
                coordinate.y == 4 and self.side == Side.WHITE
            ) or (coordinate.y == 3 and self.side == Side.BLACK)
            if is_first_enemy_rank:
                last = last_move[1]
                n1 = coordinate.get_coordinate_from_disposition((-1, 0))
                if n1 and last == n1:
                    moves.add(n1.get_coordinate_from_disposition((0, 1)))
                else:
                    n2 = coordinate.get_coordinate_from_disposition((1, 0))
                    if n2 and last == n2:
                        moves.add(n2.get_coordinate_from_disposition((0, 1)))
        return moves | forward


game = Game()
print([el for el in game.check_moves(Coordinate(0, 0))])
