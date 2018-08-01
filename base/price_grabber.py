from poloniex import Poloniex
import pandas as pd


def get_poloniex_data(cryptocurrency, period, start_time):
    polo = Poloniex()
    data = polo.returnChartData(cryptocurrency, period=period, start=start_time)
    dataframe = pd.DataFrame(data)
    return dataframe



