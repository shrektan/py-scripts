"""The Brinson attribution model
It decomposes the excess return into both asset allocation and security selection
parts. Each part aggregates individual assets, meaning that different category
assets can customize the results.
"""
from dataclasses import dataclass
from typing import NewType, Iterator
from math import isclose, isnan


@dataclass
class Pos_Info:
    weight: float
    rtn: float


Asset = NewType("Asset", str)


@dataclass
class Position:
    assets: list[Pos_Info]
    real_rtn: float = float("nan")

    def sum_weight(self) -> float:
        out: float = 0.0
        for info in self.assets:
            out += info.weight
        return out

    def sum_rtn(self) -> float:
        out: float = 0.0
        for info in self.assets:
            out += info.rtn * info.weight
        return out

    def __iter__(self) -> Iterator[Pos_Info]:
        return iter(self.assets)

    def __len__(self) -> int:
        return len(self.assets)

    def __post_init__(self) -> None:
        # isclose() returns false for NA so no need to check NA
        if not isclose(self.sum_weight(), 1.0):
            raise ValueError(
                f"the sum weight is {self.sum_weight()} but should be 1.0")
        if isnan(self.real_rtn):
            self.real_rtn = self.sum_rtn()


@dataclass
class Brinson_Res:
    alloc: list[float]
    sel: list[float]
    other: float


def breakdown(ptf: Position, bmk: Position) -> Brinson_Res:
    """The brinson attribution for a single point

    Args:
        ptf (Position): the position of the portfolio
        bmk (Position): the position of the benchmark. It must have
          the same asset order as of `ptf`.

    Raises:
        ValueError: the length of `ptf` and `bmk` must be the same

    Returns:
        Brinson_Res: the difference from the real rtn and the weighted
          sum of the positions will be attributed to "other" effect.
          In addition, all the cross effect will be added back to the
          "selection" effect.
    """
    if (len(ptf) != len(bmk)):
        raise ValueError(
            f"the length of ptf ({len(ptf)}) and bmk ({len(bmk)}) must be equal")
    alloc: list[float] = []
    sel: list[float] = []
    for (p, b) in zip(ptf, bmk):
        alloc.append(
            (p.weight - b.weight) * b.rtn
        )
        sel.append(
            (p.rtn - b.rtn) * p.weight
        )
    other = (ptf.real_rtn - bmk.real_rtn) - (ptf.sum_rtn() - bmk.sum_rtn())
    return Brinson_Res(alloc, sel, other)
