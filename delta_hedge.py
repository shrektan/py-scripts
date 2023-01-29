"""Demonstrate the effectiveness of delta hedging
for call options with different hedging frequency
"""

from dataclasses import dataclass, field, asdict
from math import sqrt, log, exp, isclose
import argparse
import scipy.stats
import numpy as np
import pandas as pd
import writexlsx

TRADING_DAYS_PER_YEAR = 252


def norm(x: float) -> float:
    return scipy.stats.norm.cdf(x)  # type: ignore


@dataclass
class CallOption:
    spot: float
    strike: float
    sigma: float
    rf: float
    mty_in_days: float

    def __post_int__(self) -> None:
        if not isclose(self.mty_in_days, int(self.mty_in_days)):
            raise ValueError(
                f"the option's init mty must be an integer, now it's {self.mty_in_days}"
            )

    @property
    def mty_in_years(self) -> float:
        return self.mty_in_days / TRADING_DAYS_PER_YEAR

    @property
    def d1(self) -> float:
        if self.expired:
            return float("nan")
        return 1.0 / (self.sigma * sqrt(self.mty_in_years)) * (
            log(self.spot / self.strike) +
            (self.rf + self.sigma ** 2.0 / 2.0 * self.mty_in_years)
        )

    @property
    def d2(self) -> float:
        return self.d1 - self.sigma * sqrt(self.mty_in_years)

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
        return norm(self.d1) * self.spot - \
            norm(self.d2) * self.strike * exp(-self.rf * self.mty_in_years)

    def expire(self, time: float) -> None:
        self.mty_in_days -= time

    @property
    def expired(self) -> bool:
        return self.mty_in_days <= 0.0


@dataclass
class PriceTS():
    points: list[float]
    prices: list[float]

    def __post_init__(self) -> None:
        if len(self.points) != len(self.prices):
            raise ValueError("points and prices must have the same length")

    def __len__(self) -> int:
        return len(self.points)


def price_ts(p0: float, er: float, evol: float,
             days: int, times_per_day: int) -> PriceTS:
    total_points = days * times_per_day
    er_daily = er / TRADING_DAYS_PER_YEAR
    evol_daily = evol / sqrt(TRADING_DAYS_PER_YEAR)
    rtn_daily = np.random.normal(er_daily, evol_daily, total_points)
    points0 = np.array(range(1, days + 1)) / times_per_day
    prices0 = p0 * np.cumprod(1 + rtn_daily)
    points = np.insert(points0, 0, 0.0)
    prices = np.insert(prices0, 0, p0)
    return PriceTS(points=list(points), prices=list(prices))


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
        out = pd.DataFrame(asdict(self))
        return out


@dataclass
class CallOptionReplicaPtf():
    cash: float
    reb_times_per_day: int
    call_option: CallOption
    rep_asset_qty: float
    asset_er: float
    asset_p0: float = field(init=False)
    total_days: int = field(init=False)
    total_steps: int = field(init=False)
    asset_prices: PriceTS = field(init=False)
    asset_qty: float = field(init=False, default=0)
    reb_count: int = field(init=False, default=0)
    booking: AccountBook = field(init=False, default_factory=AccountBook)

    @property
    def step(self) -> float:
        return 1 / self.reb_times_per_day

    @property
    def timepoint(self) -> float:
        return self.reb_count / self.reb_times_per_day

    @property
    def mty(self) -> float:
        return self.total_days - self.timepoint

    @property
    def asset_price(self) -> float:
        return self.asset_prices.prices[self.reb_count]

    def __post_init__(self) -> None:
        self.total_days = int(self.call_option.mty_in_days)
        self.total_steps = self.reb_times_per_day * self.total_days
        self.asset_p0 = self.call_option.spot
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
        self.reb_count += 1
        if self.expired:
            return None
        self.call_option.spot = self.asset_price
        self.call_option.expire(self.step)
        delta = self.call_option.delta
        trade_qty = delta * self.rep_asset_qty - self.asset_qty
        cash_use = trade_qty * self.asset_price
        self.cash -= cash_use
        self.asset_qty += trade_qty
        self.record()

    def record(self) -> None:
        self.booking.add(
            t=self.timepoint, q=self.asset_qty, assetp=self.asset_price,
            cash=self.cash, mv=self.mv,
            delta=self.call_option.delta, callp=self.call_option.price
        )

    def export(self) -> pd.DataFrame:
        return self.booking.export()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simulate Call Option using ETFs via delta hedging")
    parser.add_argument("excel", type=str, help="the output excel path")
    parser.add_argument(
        "--overwrite", help="overwrite the excel if it exists",
        action="store_true", default=False)
    parser.add_argument(
        "-o", "--open", help="open the output excel file when job is over",
        action="store_true", default=False)
    parser.add_argument(
        "--spot", type=float, default=100.0,
        help="the init spot price of the underlying asset (default 100.0)"
    )
    parser.add_argument(
        "--strike", type=float, default=100.0,
        help="the strike price of the call option (default 100.0)"
    )
    parser.add_argument(
        "--sigma", type=float, default=0.30,
        help="the volatility of the underlying asset (default 0.30)"
    )
    parser.add_argument(
        "--rf", type=float, default=0.03,
        help="the risk free rate (default 0.03)"
    )
    parser.add_argument(
        "--mty", type=int, default=252,
        help="the call option's maturity days (default 252)"
    )
    parser.add_argument(
        "--cash", type=float, default=10_000.0,
        help="the init cash in the portfolio (default 10000)"
    )
    parser.add_argument(
        "--er", type=float, default=0.10,
        help="the expected return of the underlying asset (default 0.10)"
    )
    parser.add_argument(
        "--freq", type=int, default=1,
        help="the rebalance frequency per day (default 1)"
    )
    parser.add_argument(
        "--qty", type=int, default=100.0,
        help="the target quantity of the call option (default 100.0)"
    )
    opt = parser.parse_args()
    callopt = CallOption(
        spot=opt.spot, strike=opt.strike, sigma=opt.sigma,
        rf=opt.rf, mty_in_days=opt.mty)
    ptf = CallOptionReplicaPtf(
        cash=opt.cash, asset_er=opt.er,
        reb_times_per_day=opt.freq,
        call_option=callopt, rep_asset_qty=opt.qty)
    ptf.simulate()
    df = ptf.export()
    writexlsx.write(df, opt.excel, overwrite=opt.overwrite, open=opt.open)


if __name__ == "__main__":
    main()