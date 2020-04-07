import numpy as np
from jesse import utils
import talib

from collections import namedtuple

SuperTrend = namedtuple('SuperTrend', ['trend', 'changed'])

def supertrend(candles: np.ndarray, period=10, factor=3, sequential=False) -> SuperTrend:

    if len(candles) > 240:
        candles = candles[-240:]

    # calculation of ATR using TALIB function
    atr= talib.ATR(candles[:, 3], candles[:, 4], candles[:, 2], timeperiod=period)

    # Calculation of SuperTrend
    upper_basic = (candles[:, 3] + candles[:, 4]) / 2 + (factor * atr)
    lower_basic = (candles[:, 3] + candles[:, 4]) / 2 - (factor * atr)
    upper_band = upper_basic
    lower_band = lower_basic
    super_trend = np.zeros(len(candles))
    changed = np.zeros(len(candles))

    # calculate the bands:
    # in an UPTREND, lower band does not decrease
    # in a DOWNTREND, upper band does not increase
    for i in range(period, len(candles)):
        # if currently in DOWNTREND (i.e. price is below upper band)
        prevClose = candles[:, 2][i - 1]
        prevUpperBand = upper_band[i - 1]
        currUpperBasic = upper_basic[i]
        if prevClose <= prevUpperBand:
            # upper band will DECREASE in value only
            upper_band[i] = min(currUpperBasic, prevUpperBand)

        # if currently in UPTREND (i.e. price is above lower band)
        prevLowerBand = lower_band[i - 1]
        currLowerBasic = lower_basic[i]
        if prevClose >= prevLowerBand:
            # lower band will INCREASE in value only
            lower_band[i] = max(currLowerBasic, prevLowerBand)

        # >>>>>>>> previous period SuperTrend <<<<<<<<
        if prevClose <= prevUpperBand:
            super_trend[i - 1] = prevUpperBand
        else:
            super_trend[i - 1] = prevLowerBand
        prevSuperTrend = super_trend[i - 1]

    for i in range(period, len(candles)):
        prevClose = candles[:, 2][i - 1]
        prevUpperBand =upper_band[i - 1]
        currUpperBand = upper_band[i]
        prevLowerBand = lower_band[i - 1]
        currLowerBand = lower_band[i]
        prevSuperTrend = super_trend[i - 1]

        # >>>>>>>>> current period SuperTrend <<<<<<<<<
        if prevSuperTrend == prevUpperBand:  # if currently in DOWNTREND
            if candles[:, 2][i] <= currUpperBand:
                super_trend[i] = currUpperBand  # remain in DOWNTREND
                changed[i] = False
            else:
                super_trend[i] = currLowerBand  # switch to UPTREND
                changed[i] = True
        elif prevSuperTrend == prevLowerBand:  # if currently in UPTREND
            if candles[:, 2][i] >= currLowerBand:
                super_trend[i] = currLowerBand  # remain in UPTREND
                changed[i] = False
            else:
                super_trend[i] = currUpperBand  # switch to DOWNTREND
                changed[i] = True

    if sequential:
        return SuperTrend(super_trend, changed)
    else:
        return SuperTrend(super_trend[-1], changed[-1])