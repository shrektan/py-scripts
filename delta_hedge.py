"""Demonstrate the effectiveness of delta hedging
for call options with different hedging frequency
"""

from dataclasses import dataclass, field
from math import sqrt, log, exp, isclose
import scipy.stats
import numpy as np
import pandas as pd
import writexlsx


def norm(x: float) -> float:
    return scipy.stats.norm.cdf(x)  # type: ignore


@dataclass
class CallOption:
    spot: float
    strike: float
    sigma: float
    rf: float
    mty: float

    def __post_int__(self) -> None:
        if not isclose(self.mty, int(self.mty)):
            raise ValueError(
                f"the option's init mty must be an integer, now it's {self.mty}")

    @property
    def d1(self) -> float:
        if self.expired:
            return float("nan")
        return 1.0 / (self.sigma * sqrt(self.mty)) * (
            log(self.spot / self.strike) +
            (self.rf + self.sigma ** 2.0 / 2.0 * self.mty)
        )

    @property
    def d2(self) -> float:
        return self.d1 - self.sigma * sqrt(self.mty)

    @property
    def delta(self) -> float:
        if self.expired:
            return 0.0
        return norm(self.d1)

    @property
    def payoff(self) -> float:
        return max(self.spot - self.strike, 0.0)

    @property
    def price(self) -> float:
        if self.expired:
            return self.payoff
        return norm(self.d1) - norm(self.d2) *\
            self.strike * exp(-self.rf * self.mty)

    def expire(self, time: float) -> None:
        self.mty -= time

    @property
    def expired(self) -> bool:
        return self.mty <= 0.0


@dataclass
class PriceTS():
    points: np.ndarray
    prices: np.ndarray


def price_ts(p0: float, er: float, evol: float,
             days: int, times_per_day: int) -> PriceTS:
    trading_days_per_year = 252
    total_points = days * times_per_day
    er_daily = er / trading_days_per_year
    evol_daily = evol / sqrt(trading_days_per_year)
    rtn_daily = np.random.normal(er_daily, evol_daily, total_points)
    points0 = np.array(range(1, days + 1)) / times_per_day
    prices0 = p0 * (np.cumprod(1 + rtn_daily) - 1)
    points = np.insert(points0, 0, 0.0)
    prices = np.insert(prices0, 0, p0)
    return PriceTS(points=points, prices=prices)


@dataclass
class AccountBook:
    timepoint: list[float] = field(init=False, default_factory=list)
    asset_qty: list[float] = field(init=False, default_factory=list)
    asset_price: list[float] = field(init=False, default_factory=list)
    cash: list[float] = field(init=False, default_factory=list)
    mv: list[float] = field(init=False, default_factory=list)
    call_delta: list[float] = field(init=False, default_factory=list)
    call_price: list[float] = field(init=False, default_factory=list)

    def add(self, t: float, q: float, cash: float, assetp: float,
            mv: float, delta: float, callp: float) -> None:
        self.timepoint.append(t)
        self.asset_qty.append(q)
        self.cash.append(cash)
        self.mv.append(mv)
        self.call_delta.append(delta)
        self.call_price.append(callp)
        self.asset_price.append(assetp)

    def export(self) -> pd.DataFrame:
        out = pd.DataFrame({
            "TimePoint": self.timepoint,
            "AssetQty": self.asset_qty,
            "AssetPrice": self.asset_price,
            "Cash": self.cash,
            "MV": self.mv,
            "CallDelta": self.call_delta,
            "CallPrice": self.call_price,
        })
        return out


@dataclass
class CallOptionReplicaPtf():
    cash: float
    reb_times_per_day: int
    call_option: CallOption
    rep_asset_qty: float = 200.0
    asset_p0: float = 100.0
    asset_er: float = 0.073
    total_days: int = field(init=False)
    total_steps: int = field(init=False)
    asset_prices: PriceTS = field(init=False)
    asset_qty: float = field(init=False, default=0)
    timepoint: int = field(init=False, default=0)
    booking: AccountBook = field(init=False, default_factory=AccountBook)

    @property
    def step(self) -> float:
        return 1 / self.reb_times_per_day

    @property
    def mty(self) -> float:
        return self.total_days - self.timepoint / self.reb_times_per_day

    @property
    def asset_price(self) -> float:
        return self.asset_prices.prices[self.timepoint]

    def __post_init__(self) -> None:
        self.total_days = int(self.call_option.mty)
        self.total_steps = self.reb_times_per_day * self.total_days
        self.asset_prices = price_ts(
            p0=self.asset_p0, er=self.asset_er, evol=self.call_option.sigma,
            days=self.total_days, times_per_day=self.reb_times_per_day
        )
        self.record()

    @property
    def mv(self) -> float:
        return self.asset_qty * self.asset_price + self.cash

    @property
    def expired(self) -> bool:
        return self.mty <= 0.0

    def simulate(self) -> None:
        while not self.expired:
            self.rebalance()

    def rebalance(self) -> None:
        if self.expired:
            return None
        delta = self.call_option.delta
        trade_qty = delta * self.rep_asset_qty - self.asset_qty
        cash_use = trade_qty * self.asset_price
        self.cash -= cash_use
        self.asset_qty += trade_qty

        self.timepoint += 1
        self.call_option.expire(self.step)
        self.record()

    def record(self) -> None:
        self.booking.add(
            t=self.timepoint, q=self.asset_qty,  assetp=self.asset_price,
            cash=self.cash, mv=self.mv,
            delta=self.call_option.delta, callp=self.call_option.price
        )

    def export(self) -> pd.DataFrame:
        return self.booking.export()


def main() -> None:
    callopt = CallOption(spot=100, strike=100, sigma=0.22, rf=0.03, mty=252)
    ptf = CallOptionReplicaPtf(
        cash=1e5, reb_times_per_day=1, call_option=callopt, rep_asset_qty=500)
    ptf.simulate()
    df = ptf.export()
    writexlsx.write(df, "~/Downloads/test.xlsx", overwrite=True, open=True)


if __name__ == "__main__":
    main()
