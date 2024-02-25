import talib
import yfinance as yf
import pandas as pd

df = []
# rsi_period_1 = 7  # Example RSI period
# rsi_period_2 = 14  # Example RSI period
# rsi_period_3 = 21  # Example RSI period

# ma_lower_period = 14  # Example MA Lower period
# ma_higher_period = 21  # Example MA Higher period
# compare_symbol = "^GSPC"

input = {}


def calc_MA(key, value):
    if value["Active"] == "No":
        return
    df[key] = df['Close'].rolling(window=value["Period"]).mean()

def calc_RSI(key, value):
    # Calculate the RSI for the given period
    
    if value["Active"] == "No":
        return
    
    df[key] = talib.RSI(df['Close'], timeperiod=value["Period"])
    df[f'{key}MAL'] = df[key].rolling(window=value["MA Lower Period"]).mean()
    df[f'{key}MAH'] = df[key].rolling(window=value["MA Higher Period"]).mean()
    

def calc_CRS(key, value):
    if value["Active"] == "No":
        return
    compare_df = yf.download(value["Compare Symbol"], start="2023-01-01", end="2024-02-23", interval=input["Timeframe"])
    df['Compare_Close'] = compare_df['Close']
    df["CRS"] = df['Close'] / df['Compare_Close']
    
    df["CRSMAL"] = df["CRS"].rolling(window=value["MA Lower Period"]).mean()
    df["CRSMAH"] = df["CRS"].rolling(window=value["MA Higher Period"]).mean()
    
def calc_Stochastic(key, value):
    if value["Active"] == "No":
        return
    # Define the Stochastic Oscillator parameters
    k_period = value["K%"]  # The time period for %K
    # k_slowing_period = 3  # The slowing period for the %K line
    d_period = value["D%"]   # The time period for %D (usually a simple moving average of %K)

    # Calculate the Stochastic Oscillator
    df['Sto_main'], df['Sto_signal'] = talib.STOCH(df['High'], df['Low'], df['Close'], 
                                                fastk_period=k_period, # the time period for the fast %K line.
                                                slowk_period=d_period, # the time period for the slow %K line, which is a smoothed version of the fast %K.
                                                slowk_matype=0, # the type of moving average for the slow %K line. A value of 0 specifies a simple moving average. 
                                                slowd_period=d_period, # the time period for the slow %D line, which is a moving average of the slow %K line.
                                                slowd_matype=0 # the type of moving average for the slow %D line. A value of 0 specifies a simple moving average.
                                            )

def calc_MACD(key, value):
    if value["Active"] == "No":
        return
    period1 = value["Period1"]  # Short-term EMA period
    period2 = value["Period2"]  # Long-term EMA period
    period3 = value["Period3"]  # Signal line EMA period

    # Calculate the MACD and the signal line
    df["MACD"], df['MACD_signal'], _ = talib.MACD(df['Close'], 
                                                fastperiod=period1, 
                                                slowperiod=period2, 
                                                signalperiod=period3
                                            )

def calc_output(last_row):
    active_count = 0
    score = 0;
    print("last_row: ", type(last_row))
    #------------------------ MA Score ---------------------------
    for i in range(1, 6):
        for j in range(i+1, 6):
            if input[f"Moving Average {i}"]["Active"] == "Yes" and input[f"Moving Average {j}"]["Active"] == "Yes":
                active_count += 1
                MA_diff = last_row[f"MA_{i}"].iloc[-1] - last_row[f"MA_{j}"].iloc[-1] # difference between MA_i and MA_j
                print(type(MA_diff))
                MA_threshold = input["MA Threshold"] # MA Threshold
                if MA_diff > MA_threshold:
                    score += 1
                elif MA_diff <= MA_threshold and MA_diff >= 0:
                    pass
                else:
                    score -= 1
                    
    # ----------------------- CRS Score ---------------------------
    if input["Comparative Relative Strength"]["Active"] == "Yes":
        active_count += 1
        CRS_diff = last_row["CRSMAL"].iloc[-1] - last_row["CRSMAH"].iloc[-1]
        CRS_threshold = 0 # CRS Threshold
        if CRS_diff > CRS_threshold:
            score += 1
        elif CRS_diff <= CRS_threshold and CRS_diff >= 0:
            pass
        else:
            score -= 1
        
    #---------------------- RSI Score ----------------------------
    for i in range(1, 4):
        if input[f"Relative Strength Index {i}"]["Active"] == "Yes":
            active_count += 1
            RSI_diff = last_row[f"RSI{i}MAL"].iloc[-1] - last_row[f"RSI{i}MAH"].iloc[-1]
            RSI_threshold = 0 # RSI Threshold
            if RSI_diff > RSI_threshold:
                score += 1
            elif RSI_diff <= RSI_threshold and RSI_diff >= 0:
                pass
            else:
                score -= 1
            
    #---------------------- Stochastic Score ----------------------------
    if input["Stochastic"]["Active"] == "Yes":
        active_count += 1
        Sto_diff = last_row["Sto_signal"].iloc[-1] - last_row["Sto_main"].iloc[-1]
        Sto_threshold = input["Stochastic Threshold"] # Sto Threshold
        if Sto_diff > Sto_threshold:
            score += 1
        elif Sto_diff <= Sto_threshold and Sto_diff >= 0:
            pass
        else:
            score -= 1
              
    #---------------------- MACD Score ----------------------------
    if input["MACD"]["Active"] == "Yes":
        active_count += 1
        MACD_diff = last_row["MACD_signal"].iloc[-1] - last_row["MACD"].iloc[-1]
        MACD_threshold = input["MACD Threshold"] # Sto Threshold
        if MACD_diff > MACD_threshold:
            score += 1
        elif MACD_diff <= MACD_threshold and MACD_diff >= 0:
            pass
        else:
            score -= 1
    
    print(active_count, " ", score)
    return score
    
    
def main(_input):
    global df, input
    input = _input
    # Download historical stock price data
    df = yf.download("MSFT", start="2023-01-01", end="2024-02-23", interval=input["Timeframe"])

    calc_MA("MA_1", input["Moving Average 1"])
    calc_MA("MA_2", input["Moving Average 2"])
    calc_MA("MA_3", input["Moving Average 3"])
    calc_MA("MA_4", input["Moving Average 4"])
    calc_MA("MA_5", input["Moving Average 5"])
    calc_RSI("RSI1", input["Relative Strength Index 1"])
    calc_RSI("RSI2", input["Relative Strength Index 1"])
    calc_RSI("RSI3", input["Relative Strength Index 1"])
    calc_CRS("CRS", input["Comparative Relative Strength"])
    calc_Stochastic("Stochastic", input["Stochastic"])
    calc_MACD("MACD", input["MACD"])
    
    last_row = df.tail(1)
    
    return calc_output(last_row)
    
    
    print(last_row)

_input = {
  "Timeframe": "1D",
  "Moving Average 1": {"Active": "Yes", "Period": 20},
  "Moving Average 2": {"Active": "Yes", "Period": 50},
  "Moving Average 3": {"Active": "Yes", "Period": 100},
  "Moving Average 4": {"Active": "Yes", "Period": 150},
  "Moving Average 5": {"Active": "Yes", "Period": 200},
  "Comparative Relative Strength": {"Active": "Yes", "Period": 14, "Compare Symbol": "SPY", "MA Lower Period": 50, "MA Higher Period": 200},
  "Relative Strength Index 1": {"Active": "Yes", "Period": 14, "MA Lower Period": 9, "MA Higher Period": 25},
  "Relative Strength Index 2": {"Active": "Yes", "Period": 14, "MA Lower Period": 9, "MA Higher Period": 25},
  "Relative Strength Index 3": {"Active": "Yes", "Period": 14, "MA Lower Period": 9, "MA Higher Period": 25},
  "Stochastic": {"Active": "Yes", "K%": 14, "D%": 3},
  "MACD": {"Active": "Yes", "Period1": 12, "Period2": 25, "Period3": 9},
  "MA Threshold": 0.5,
  "Stochastic Threshold": 0.4,
  "MACD Threshold": 0.5
  
}

main(_input)