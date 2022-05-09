import pandas as pd

AQI_BREAKPOINTS = './aqtools/aqi_breakpoints.csv'


def get_aqi(pollutant, value):
    pollutants = {'pm25': '88502',
                  'co': '42101',
                  'no2': '42602',
                  'o3': '44201',
                  'pm10': '81102',
                  'so2': '42401'}

    p = pollutants[pollutant]
    df = pd.read_csv(AQI_BREAKPOINTS)
    p_df = df[df['Parameter Code'] == p]
    aqi = p_df[(p_df['Low Breakpoint'] <= value) & (value < p_df['High Breakpoint'])]
    Cp = value
    BPHi = aqi['High Breakpoint'].values[0]
    BPLo = aqi['Low Breakpoint'].values[0]
    IHi = aqi['High AQI'].values[0]
    ILo = aqi['Low AQI'].values[0]
    IP = (IHi - ILo)/(BPHi - BPLo) * (Cp - BPLo) + ILo
    return int(IP)