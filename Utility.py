from pydantic import BaseModel
from typing import Optional
import talib
import yfinance as yf
import pandas as pd

class MovingAverageModel:
    Active: Optional[str] = "No"
    Period: int = 20
    
    def __init__(self, Active, Period):
        self.Active = Active
        self.Period = Period
        
    def Calc_MA(self, DataFrame):
        if self.Active == "No":
            return pd.DataFrame()
        return DataFrame['Close'].rolling(window=self.Period).mean()
    

class RSIModel:
    Active: Optional[str] = "No"
    Period: int = 20
    MA_Lower_Period: int = 9
    MA_Higher_Period: int = 25
    
    def __init__(self, Active, Period, MA_Lower_Period, MA_Higher_Period):
        self.Active = Active
        self.Period = Period
        self.MA_Lower_Period = MA_Lower_Period
        self.MA_Higher_Period = MA_Higher_Period
        
    def Calc_RSI(self, DataFrame):
        if self.Active == "No":
            return pd.DataFrame()
        
        RSI = talib.RSI(DataFrame['Close'], timeperiod=self.Period)
        RSIMAL = RSI.rolling(window=self.MA_Lower_Period).mean()
        RSIMAH = RSI.rolling(window=self.MA_Higher_Period).mean()
        
        return {"RSIMAL": RSIMAL, "RSIMAH": RSIMAH}


class CRSModel:
    Active: Optional[str] = "No"
    Period: int = 20
    Compare_Symbol: str = None
    MA_Lower_Period: int = 9
    MA_Higher_Period: int = 25
    Compare_DF: dict = None
    Time: str = None
    
    def __init__(self, Active, Period, Compare_Symbol, MA_Lower_Period, MA_Higher_Period, Time, TimeFrame):
        self.Active = Active
        self.Period = Period
        self.Compare_Symbol = Compare_Symbol
        self.MA_Lower_Period = MA_Lower_Period
        self.MA_Higher_Period = MA_Higher_Period
        self.Compare_DF = yf.download(Compare_Symbol, start="2023-01-01", end=Time, interval=TimeFrame)
        self.Time = Time
        
    def Calc_CRS(self, DataFrame):
        if self.Active == "No":
            return pd.DataFrame()
        
        Compare_Close = self.Compare_DF['Close']
        CRS = DataFrame['Close'] / Compare_Close
        CRSMAL = CRS.rolling(window=self.MA_Lower_Period).mean()
        CRSMAH = CRS.rolling(window=self.MA_Higher_Period).mean()
        
        return {"CRSMAL": CRSMAL, "CRSMAH": CRSMAH}
    
    
class StochasticModel:
    Active: Optional[str] = "No"
    K_Period: int = 14
    D_Period: int = 3
    
    def __init__(self, Active, K_Period, D_Period):
        self.Active = Active
        self.K_Period = K_Period
        self.D_Period = D_Period
        
    def Calc_Stochastic(self, DataFrame):
        if self.Active == "No":
            return pd.DataFrame()
        
        # Calculate the Stochastic Oscillator
        try:
            Sto_main, Sto_signal = talib.STOCH(
                DataFrame['High'],
                DataFrame['Low'],
                DataFrame['Close'], 
                fastk_period=self.K_Period, # the time period for the fast %K line.
                slowk_period=self.D_Period, # the time period for the slow %K line, which is a smoothed version of the fast %K.
                slowk_matype=0, # the type of moving average for the slow %K line. A value of 0 specifies a simple moving average. 
                slowd_period=self.D_Period, # the time period for the slow %D line, which is a moving average of the slow %K line.
                slowd_matype=0 # the type of moving average for the slow %D line. A value of 0 specifies a simple moving average.
            )
            return {"Sto_main": Sto_main, "Sto_signal": Sto_signal}
        except Exception as e:
            print(DataFrame[['High', 'Low', 'Close']])
            print(e)
    
class MACDModel:
    Active: Optional[str] = "No"
    Period1: int = 12
    Period2: int = 26
    Period3: int = 9
    
    def __init__(self, Active, Period1, Period2, Period3):
        self.Active = Active
        self.Period1 = Period1
        self.Period2 = Period2
        self.Period3 = Period3
        
    def Calc_MACD(self, DataFrame):
        if self.Active == "No":
            return pd.DataFrame()
        
        # Calculate the MACD and the signal line
        MACD, MACD_signal, _ = talib.MACD(
            DataFrame['Close'], 
            fastperiod=self.Period1, 
            slowperiod=self.Period2, 
            signalperiod=self.Period3
        )
        return {"MACD": MACD, "MACD_signal": MACD_signal}


def Check_Crossover_Crossdown(Values_1, Values_2, Th):
    if Values_1.empty or Values_2.empty:
        return None
    
    if Values_1[-2] < Values_2[-2] and Values_1[-1] > Values_2[-1] and (Values_1[-1] - Values_2[-1]) > Th:
        return 1
    elif Values_1[-2] > Values_2[-2] and Values_1[-1] < Values_2[-1] and (Values_1[-1] - Values_2[-1]) < -Th:
        return -1
    else:
        return 0