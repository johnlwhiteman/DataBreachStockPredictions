from datetime import datetime, timedelta
from fbprophet import Prophet
import json
import matplotlib.dates as mdates
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from pprint import pprint
import re
import sys
import traceback

class Breaches:

    class Breach(object):
        pass

    def __init__(self, modelDays=365, predictDays=100, dataSource="ALPHA_VANTAGE", apiKey=None):
        self.modelDays = modelDays
        self.predictDays = predictDays
        self.dataSource = dataSource
        self.apiKey = apiKey
        self.breaches= None
        self.today = None
        self.meta = None

    @staticmethod
    def exception(e):
        print("SOMETHING HAS GONE AWRY!\n{0}".format(e))
        sys.exit(1)

    @staticmethod
    def getEnv(name):
        if name in os.environ:
            return os.environ[name]
        return None

    def getIDs(self):
        return self.breaches.keys()

    def open(self, path="breaches.json", forceRemote=False):
        self.meta = pd.DataFrame(columns = [])
        with open(path, "r",  encoding="utf-8") as fd:
            try:
                self.breaches = {}
                self.IDs = []
                data = json.load(fd)
                for c in data["companies"]:
                    if "ignore" in c and c["ignore"]:
                        continue
                    if not os.path.exists("data"):
                        os.makedirs("data")
                    b = Breaches.Breach()
                    b.__dict__.update(c)
                    b.path = "data/{0}.csv".format(b.ID)
                    b.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if not hasattr(b, "modelDays"):
                        b.modelDays = self.modelDays
                    if not hasattr(b, "predictDays"):
                        b.predictDays = self.predictDays
                    if not hasattr(b, "predictOnly"):
                        b.predictOnly = False
                    b.startPredictDate = \
                        pd.to_datetime(datetime.strptime(b.date, "%Y-%m-%d"))
                    b.endModelDate = \
                        pd.to_datetime(b.startPredictDate - timedelta(days=1))
                    b.startModelDate = \
                        pd.to_datetime(b.endModelDate - timedelta(days=b.modelDays))
                    b.weekday = b.startPredictDate.strftime("%a")
                    b.today = datetime.today()
                    b.daysSinceBreach = int((b.today - b.startPredictDate).days)
                    if b.daysSinceBreach  < 1:
                        b.sameDayFlag = True
                    else:
                        b.sameDayFlag = False
                    if b.predictDays is None or b.predictDays < 1:
                        if b.sameDayFlag:
                            Breaches.exception("Breach day is same as today. Please manually add predict days")
                        b.endPredictDate = \
                            pd.to_datetime(b.startPredictDate + timedelta(days=b.daysSinceBreach))
                        b.predictDays = b.daysSinceBreach
                    else:
                        b.endPredictDate = \
                            pd.to_datetime(b.startPredictDate + timedelta(days=b.predictDays))
                    print("Get'in {0} [{1}] ... please wait".format(b.name, b.symbol))
                    if forceRemote or not os.path.isfile(b.path):
                        if re.search(self.dataSource, "ALPHA_VANTAGE", re.IGNORECASE):
                            self.__runAlphaVantage(b)
                        elif re.search(self.dataSource, "QUANDL", re.IGNORECASE):
                            self.__runQuantl(b)
                        else:
                            Breaches.exception("Unknown data source: {0}".format(self.dataSource))
                    b.df = pd.read_csv(b.path, parse_dates=["ds"], index_col=None)
                    if b.df.iloc[-1]["ds"] < b.endModelDate:
                        Breaches.exception("Your data is missing the latest breach dates".format(self.dataSource))
                    b.price = None
                    b.latestDate = None
                    b.latestPrice = None
                    b.recoverDf = None
                    b.recoverDays = None
                    b.recoverRollingDays = None
                    b.actualLastDate = None
                    b.actualNextDate = None
                    b.priceDropped = None
                    b.beforePrice = None
                    b.modelDf = \
                        b.df[(b.df.ds >= b.startModelDate) & (b.df.ds <= b.endModelDate)]
                    b.modelMean = b.modelDf.y.mean().round(2)
                    b.idx = b.df.loc[b.df.ds == b.date]
                    if 0 == b.idx.shape[0]:
                        b.idx = list(b.df.loc[b.df.ds == b.startPredictDate].index)[0] - 1
                        b.idx = b.df.iloc[b.idx]
                    b.price = float(b.idx.y)
                    b.beforePrice = b.modelDf.tail(1).iloc[0].y
                    if not b.sameDayFlag:
                        b.actualDf = \
                            b.df[(b.df.ds >= b.startPredictDate) & (b.df.ds <= b.endPredictDate)]
                        b.actualMean = b.actualDf.y.mean().round(2)
                        b.actualLastDate = b.actualDf.tail(1).iloc[0].ds
                        b.actualNextDate = b.actualDf.head(2).iloc[1].ds
                        b.actualNextPrice = b.actualDf.head(2).iloc[1].y
                        cnt = b.actualDf.head().shape[0]
                        if cnt > 3:
                            b.actualNextPriceMean = (b.actualDf.head(4).sum() - b.beforePrice) / 3
                        elif cnt > 1:
                            b.actualNextPriceMean = (b.actualDf.head(cnt).sum() - b.beforePrice) / (cnt - 1)
                        else:
                            b.actualNextPriceMean = b.beforePrice
                        b.actualNextPriceMean = b.actualNextPriceMean.iloc[0].round(2)
                        b.latestPrice = float(b.actualDf.tail(1).iloc[0].y)
                        b.latestDate = b.actualDf.tail(1).iloc[0].ds
                        #b.priceDropped = (b.actualNextPriceMean < b.beforePrice)
                        b.priceDropped = (b.actualNextPrice < b.beforePrice)
                    else:
                        b.actualDf = None
                        b.actualMean = None
                        b.priceDropped = (b.price < b.beforePrice)
                    try:
                        try:
                            y = b.actualDf[b.actualDf.ds >= b.actualNextDate]
                            x = y[y.y >= b.price]
                            if not x.empty:
                                b.recoverDf = x.iloc[0]
                                b.recoverFq = x.shape[0]
                                b.recoverDays = (b.recoverDf.ds - b.endModelDate).days
                                b.recoverMean = x.y.mean().round(2)
                                if b.priceDropped:
                                    b.recoverDays = (b.recoverDf.ds - b.endModelDate).days
                                    b.actualDf = b.actualDf.copy()
                                    b.actualDf["RM"] = b.actualDf.rolling(window=10).mean()
                                    dfRm = b.actualDf[b.actualDf["RM"] >= b.beforePrice]
                                    if dfRm.shape[0] > 0:
                                        b.recoverRollingDays = \
                                            (dfRm.head(1).iloc[0].ds - pd.to_datetime(b.date)).days
                                else:
                                    b.recoverDays = "N/A"
                                    b.recoverRollingDays = "N/A"
                            else:
                                b.recoverDays = "Never"
                                b.recoverRollingDays = "Never"
                        except IndexError as e:
                            pass
                    except TypeError as e:
                        pass
                    self.breaches[b.ID] = b
                    self.IDs.append(b.ID)
                    m = pd.DataFrame.from_dict([{
                        "ID": b.ID,
                        "Date": b.date,
                        "Price Before": b.beforePrice,
                        "Price": b.price,
                        "Price After": b.actualNextPrice,
                        "Latest Price": b.latestPrice,
                        "DOW": b.weekday
                    }])
                    self.meta = self.meta.append(m, ignore_index=True, sort=False)
            except IOError as e:
                Breaches.exception(traceback.format_exc())

    def plot(self, ID):
        pd.plotting.register_matplotlib_converters()
        try:
            b = self.breaches[ID]
            fig, ax = plt.subplots(figsize = (16,8))
            modelDf = b.modelDf.copy(deep=True)
            modelDf = modelDf.set_index("ds")
            if not b.sameDayFlag:
                actualDf = b.actualDf.copy(deep=True)
                actualDf = actualDf.set_index("ds")
            mergedDf = b.mergedDf.copy(deep=True)
            mergedDf = mergedDf.set_index("Date")
            pd.to_datetime(datetime.strptime(b.date, "%Y-%m-%d"))
            plt.xticks(rotation=45)
            plt.title("{0}: {1} ({2})\n{3}".format(b.name, b.ID, b.date, b.timestamp),
                                              fontsize=20, pad=20)
            plt.xlabel("Date", fontsize=16, labelpad=20)
            plt.ylabel("Stock Price ($USD)", fontsize=16, labelpad=20)
            plt.axvline(x=b.startPredictDate, color="red",
                        linewidth=2, label="Breach Date: {0}".format(b.date),
                        ymin=0.0, ymax=1.00)
            if not b.price is None:
                plt.axhline(y=b.price, color="brown",
                            linewidth=2, label="Breach Price: {0}".format(b.price),
                            xmin=0.0, xmax=1.00)
            plt.plot(modelDf, color="gray", label="Before Breach")
            if not b.sameDayFlag and not b.predictOnly:
                plt.plot(mergedDf.Actual, color="black", label="After Breach")
            plt.plot(mergedDf.Predicted, color="blue", label="Predicted")
            plt.grid()
            plt.legend(loc="upper left")
            plt.show()
            print(self.meta[self.meta.ID == b.ID].to_string(index=False))
        except(NameError, TypeError) as e:
            Breaches.exception(traceback.format_exc())

    def predict(self, ID):
        try:
            print("Fit'in and predict'in {0} ... please wait".format(ID))
            b = self.breaches[ID]
            b.model = Prophet(daily_seasonality=True,
                              weekly_seasonality=False,
                              yearly_seasonality=False)
            b.model.add_seasonality("self_define_cycle", period=100,
                                    fourier_order=8, mode="additive")
            b.model.fit(b.modelDf)
            b.futureDf = b.model.make_future_dataframe(periods=b.predictDays)
            b.resultsDf = b.model.predict(b.futureDf)
            df = b.resultsDf[["ds", "yhat"]]
            b.predictDf = \
                df[(df.ds >= b.startPredictDate) & (df.ds <= b.endPredictDate)]
            b.predictDf = Breaches.__round(b.predictDf)
            b.actualDf = Breaches.__round(b.actualDf)
            b.predictDf = b.predictDf.set_index(b.predictDf.ds)
            b.predictMean = b.predictDf.mean().round(2).iloc[0]
            dt = pd.date_range(start=b.startPredictDate, end=b.endPredictDate).date
            b.mergedDf = pd.DataFrame(dt, index=dt, columns=["Date"])
            b.mergedDf = pd.concat([b.mergedDf, b.predictDf], axis=1).rename(
                    columns={"yhat": "Predicted"}).drop(["ds"], axis=1)
            if not b.actualDf.empty:
                b.actualDf = b.actualDf.set_index(b.actualDf.ds)
                b.mergedDf = pd.concat([b.mergedDf, b.actualDf], axis=1).rename(
                    columns={"y": "Actual"}).drop(["ds"], axis=1)
                b.mergedDf.Actual = \
                    b.mergedDf.Actual[b.mergedDf.Actual.index <= b.actualLastDate].fillna(method="ffill")
            self.meta.loc[self.meta.ID == b.ID, "Dropped?"] = b.priceDropped
            self.meta.loc[self.meta.ID == b.ID, "RecovDays"] = b.recoverDays
            self.meta.loc[self.meta.ID == b.ID, "RecovMean"] = b.recoverRollingDays

        except(NameError, TypeError) as e:
            Breaches.exception(traceback.format_exc())

    def __round(df):
        try:
            return df.round(2)
        except Exception as e:
            pass
        return df

    def __runAlphaVantage(self, b):
        from alpha_vantage.timeseries import TimeSeries
        try:
            ts = TimeSeries(key=self.apiKey,
                            output_format="pandas",
                            indexing_type="integer")
            b.df, meta_data = ts.get_daily_adjusted(b.symbol, outputsize="full")
            b.df = b.df[["date", "5. adjusted close"]]
            b.df = b.df.round(2).rename(columns={"date": "ds", "5. adjusted close": "y"})
            b.df.ds = pd.to_datetime(b.df.ds, format="%Y-%m-%d")
            b.df = b.df.reindex(index=b.df.index[::-1])
            #b.df = \
            #    b.df[(b.df.ds >= b.startModelDate) & (b.df.ds <= b.endPredictDate)]
            b.df[["ds", "y"]].to_csv(b.path, index=False)
        except Exception as e:
            Breaches.exception(traceback.format_exc())

    def __runQuandl(self, b):
        import quandl
        try:
            if self.apiKey is None:
                b.df = quandl.get("WIKI/{0}".format(b.symbol),
                    start_date="{0}".format(b.startModelDate.strftime("%Y-%m-%d")),
                    end_date="{0}".format(b.endPredictDate.strftime("%Y-%m-%d")))
            else:
                print("... and with an API key")
                b.df = quandl.get("WIKI/{0}".format(b.symbol),
                    start_date="{0}".format(b.startModelDate.strftime("%Y-%m-%d")),
                    end_date="{0}".format(b.endPredictDate.strftime("%Y-%m-%d")),
                    api_key="{0}".format(self.apiKey))
            b.df["ds"] = b.df.index.strftime("%Y-%m-%d")
            b.df = b.df.round(2).rename(columns={"Close": "y"})
            b.df[["ds", "y"]].to_csv(b.path, index=False)
        except Exception as e:
            Breaches.exception(traceback.format_exc())

    def showMeta(self):
        print(self.meta.to_string(index=False))
