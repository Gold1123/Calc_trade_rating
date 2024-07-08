import shutil
import yfinance as yf
import pandas as pd
from Utility import MovingAverageModel, RSIModel, CRSModel, StochasticModel, MACDModel, Check_Crossover_Crossdown


File_Name = "test list.csv"


TimeFrame = '1D'
Time = "2024-03-01"

MA_1_Active = "Yes"
MA_1_Period = 20


MA_2_Active = "Yes"
MA_2_Period = 50

MA_3_Active = "Yes"
MA_3_Period = 100

MA_4_Active = "Yes"
MA_4_Period = 150

MA_5_Active = "Yes"
MA_5_Period = 200

MA_Threshold = 1


RSI_1_Active = "Yes"
RSI_1_Period = 7
RSI_1_MA_LP = 9
RSI_1_MA_HP = 25


RSI_2_Active = "Yes"
RSI_2_Period = 14
RSI_2_MA_LP = 9
RSI_2_MA_HP = 25


RSI_3_Active = "Yes"
RSI_3_Period = 21
RSI_3_MA_LP = 9
RSI_3_MA_HP = 25

RSI_Threshold = 1


CRS_Active = "Yes"
CRS_Period = 14
CRS_Compare = "SPY"
CRS_MA_LP = 9
CRS_MA_HP = 25
CRS_Threshold = 1

Stochastic_Active = "Yes"
Stochastic_K_Period = 14
Stochastic_D_Period = 3
Stochastic_Threshold = 0.5

MACD_Active = "Yes"
MACD_Period1 = 12
MACD_Period2 = 26
MACD_Period3 = 9
MACD_Threshold = 2

Score = 0
Count = 0

def Update_Score_Count(Value_1, Value_2, Th):
    result = Check_Crossover_Crossdown(Value_1, Value_2, Th)
    Score += result if result != None else 0
    Count += 1 if result != None else 0

def Calc_Rating(Symbol):
    DataFrame = yf.download(Symbol, start="2023-01-01", end=Time, interval=TimeFrame)
    
    MA_1 = MovingAverageModel(MA_1_Active, MA_1_Period)
    ma_1 = MA_1.Calc_MA(DataFrame)
    
    MA_2 = MovingAverageModel(MA_2_Active, MA_2_Period)
    ma_2 = MA_2.Calc_MA(DataFrame)
    
    MA_3 = MovingAverageModel(MA_3_Active, MA_3_Period)
    ma_3 = MA_3.Calc_MA(DataFrame)
    
    MA_4 = MovingAverageModel(MA_4_Active, MA_4_Period)
    ma_4 = MA_4.Calc_MA(DataFrame)
    
    MA_5 = MovingAverageModel(MA_5_Active, MA_5_Period)
    ma_5 = MA_5.Calc_MA(DataFrame)
    
    Update_Score_Count(ma_1, ma_2, MA_Threshold)
    Update_Score_Count(ma_1, ma_3, MA_Threshold)
    Update_Score_Count(ma_1, ma_4, MA_Threshold)
    Update_Score_Count(ma_1, ma_5, MA_Threshold)
    Update_Score_Count(ma_2, ma_3, MA_Threshold)
    Update_Score_Count(ma_2, ma_4, MA_Threshold)
    Update_Score_Count(ma_2, ma_5, MA_Threshold)
    Update_Score_Count(ma_3, ma_4, MA_Threshold)
    Update_Score_Count(ma_3, ma_5, MA_Threshold)
    Update_Score_Count(ma_4, ma_5, MA_Threshold)
    
    
    RSI_1 = RSIModel(RSI_1_Active, RSI_1_Period, RSI_1_MA_LP, RSI_1_MA_HP)
    rsi_1 = RSI_1.Calc_RSI(DataFrame)
    Update_Score_Count(rsi_1['RSIMAL'], rsi_1['RSIMAH'], RSI_Threshold)
    
    
    RSI_2 = RSIModel(RSI_2_Active, RSI_2_Period, RSI_2_MA_LP, RSI_2_MA_HP)
    rsi_2 = RSI_2.Calc_RSI(DataFrame)
    Update_Score_Count(rsi_2['RSIMAL'], rsi_2['RSIMAH'], RSI_Threshold)
    
    
    RSI_3 = RSIModel(RSI_3_Active, RSI_3_Period, RSI_3_MA_LP, RSI_3_MA_HP)
    rsi_3 = RSI_3.Calc_RSI(DataFrame)
    Update_Score_Count(rsi_3['RSIMAL'], rsi_3['RSIMAH'], RSI_Threshold)

    
    CRS = CRSModel(CRS_Active, CRS_Period, CRS_Compare, CRS_MA_LP, CRS_MA_HP, TimeFrame)
    crs = CRS.Calc_CRS(DataFrame)['CRSMAH']
    Update_Score_Count(crs['CRSMAL'], crs['CRSMAH'], CRS_Threshold)
    
    
    Stochastic = StochasticModel(Stochastic_Active, Stochastic_K_Period, Stochastic_D_Period)
    stochastic = Stochastic.Calc_Stochastic(DataFrame)
    Update_Score_Count(stochastic['Sto_main'], stochastic['Sto_signal'], Stochastic_Threshold)
    
    
    MACD = MACDModel(MACD_Active, MACD_Period1, MACD_Period2, MACD_Period3)
    macd = MACD.Calc_MACD(DataFrame)
    Update_Score_Count(macd['MACD'], macd['MACD_signal'], MACD_Threshold)
    
    return Score / Count


Input_Data_Path = f'./data/{File_Name}'

stock_csv = pd.read_csv(Input_Data_Path)
stock_list = stock_csv["Symbol"].tolist()
rating_list = []

for stock in stock_list:
    rating_list.append(Calc_Rating(stock))
stock_csv[Time] = rating_list
stock_csv.to_csv(Input_Data_Path, index=False)

