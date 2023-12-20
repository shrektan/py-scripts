import brinson as b
import pytest
import re


def test_breakdown() -> None:
    msg = re.escape(r"the sum weight is 1.1 but should be 1.0")
    with pytest.raises(ValueError, match=msg):
        b.Position(
            [b.Pos_Info(0.1, 0.02), b.Pos_Info(0.5, -0.08), b.Pos_Info(0.5, 0.04)]
        )

    ptf = b.Position(
        [b.Pos_Info(0.1, 0.02), b.Pos_Info(0.5, -0.08), b.Pos_Info(0.4, 0.04)]
    )
    bmk = b.Position(
        [b.Pos_Info(0.1, 0.01), b.Pos_Info(0.4, -0.15), b.Pos_Info(0.5, 0.03)]
    )
    out = b.Brinson_Res(
        alloc=[0.0, -0.014999999999999996, -0.002999999999999999],
        sel=[0.001, 0.034999999999999996, 0.004000000000000001],
        other=0.0,
    )
    assert b.breakdown(ptf, bmk) == out

    ptf.real_rtn = 0.05
    bmk.real_rtn = 0.03
    out = b.Brinson_Res(
        alloc=[0.0, -0.014999999999999996, -0.002999999999999999],
        sel=[0.001, 0.034999999999999996, 0.004000000000000001],
        other=-0.001999999999999995,
    )
    assert b.breakdown(ptf, bmk) == out

    msg = re.escape(r"the length of ptf (3) and bmk (1) must be equal")
    bmk2 = b.Position([b.Pos_Info(1.0, 0.01)])
    with pytest.raises(ValueError, match=msg):
        b.breakdown(ptf, bmk2)
