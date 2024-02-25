from pydantic import BaseModel

class InputModel(BaseModel):
    Timeframe: str
    Moving_Average_1: dict
    Moving_Average_2: dict
    Moving_Average_3: dict
    Moving_Average_4: dict
    Moving_Average_5: dict
    Comparative_Relative_Strength: dict
    Relative_Strength_Index_1: dict
    Relative_Strength_Index_2: dict
    Relative_Strength_Index_3: dict
    Stochastic: dict
    MACD: dict
    MA_Threshold: float
    Stochastic_Threshold: float
    MACD_Threshold: float