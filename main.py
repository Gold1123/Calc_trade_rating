from fastapi import FastAPI, UploadFile, Form
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import talib
import yfinance as yf
import pandas as pd
from model import InputModel
import shutil
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

output_file = ""
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
    try:
        df['Sto_main'], df['Sto_signal'] = talib.STOCH(df['High'], df['Low'], df['Close'], 
                                                    fastk_period=k_period, # the time period for the fast %K line.
                                                    slowk_period=d_period, # the time period for the slow %K line, which is a smoothed version of the fast %K.
                                                    slowk_matype=0, # the type of moving average for the slow %K line. A value of 0 specifies a simple moving average. 
                                                    slowd_period=d_period, # the time period for the slow %D line, which is a moving average of the slow %K line.
                                                    slowd_matype=0 # the type of moving average for the slow %D line. A value of 0 specifies a simple moving average.
                                                )
    except Exception as e:
        print(df[['High', 'Low', 'Close']])
        print(e)
        

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
            if input[f"Moving_Average_{i}"]["Active"] == "Yes" and input[f"Moving_Average_{j}"]["Active"] == "Yes":
                active_count += 1
                MA_diff = last_row[f"MA_{i}"].iloc[-1] - last_row[f"MA_{j}"].iloc[-1] # difference between MA_i and MA_j
                MA_threshold = input["MA_Threshold"] # MA Threshold
                if MA_diff > MA_threshold:
                    score += 1
                elif MA_diff <= MA_threshold and MA_diff >= 0:
                    pass
                else:
                    score -= 1
                    
    # ----------------------- CRS Score ---------------------------
    if input["Comparative_Relative_Strength"]["Active"] == "Yes":
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
        if input[f"Relative_Strength_Index_{i}"]["Active"] == "Yes":
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
        Sto_threshold = input["Stochastic_Threshold"] # Sto Threshold
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
        MACD_threshold = input["MACD_Threshold"] # MACD Threshold
        if MACD_diff > MACD_threshold:
            score += 1
        elif MACD_diff <= MACD_threshold and MACD_diff >= 0:
            pass
        else:
            score -= 1
    
    print(active_count, " ", score)
    return score / active_count
    
    
def main(Symbol):
    global df, output_file
    output_file = Symbol
    # Download historical stock price data
    print(Symbol)
    df = yf.download(Symbol, start="2023-01-01", end="2024-02-23", interval=input["Timeframe"])

    calc_MA("MA_1", input["Moving_Average_1"])
    calc_MA("MA_2", input["Moving_Average_2"])
    calc_MA("MA_3", input["Moving_Average_3"])
    calc_MA("MA_4", input["Moving_Average_4"])
    calc_MA("MA_5", input["Moving_Average_5"])
    calc_RSI("RSI1", input["Relative_Strength_Index_1"])
    calc_RSI("RSI2", input["Relative_Strength_Index_2"])
    calc_RSI("RSI3", input["Relative_Strength_Index_3"])
    calc_CRS("CRS", input["Comparative_Relative_Strength"])
    calc_Stochastic("Stochastic", input["Stochastic"])
    calc_MACD("MACD", input["MACD"])
    
    last_row = df.tail(1)
    
    return calc_output(last_row)
    
    
    print(last_row)

@app.post("/rating")
def rating(_input: InputModel):
    global input
    input = _input.dict()
    stock_csv = pd.read_csv(f"./data/{input['InputFile']}")
    stock_list = stock_csv["Symbol"].tolist()
    print("stocK: ", stock_list)
    ans = []
    for stock in stock_list:
        ans.append(main(stock))
        df.to_csv(f'./data/{output_file}.csv', index=False)
    stock_csv["Rating"] = ans
    stock_csv.to_csv('./data/output.csv', index=False)
    return True

@app.post("/upload")
def rating(file: UploadFile = Form(...)):
    with open(f"./data/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return True

app.mount("/get-answer", StaticFiles(directory="./data"), name="static")

@app.post("/", tags=["Root"])
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7000, reload=True)