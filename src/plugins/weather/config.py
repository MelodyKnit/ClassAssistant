from pydantic import BaseSettings


class Config(BaseSettings):
    loading_weather = False

    # 中国天气气象局
    class CmaWeatherApi:
        url = "https://weather.cma.cn/api/now/57679"
        params = {}

    # oppo color 天气
    class OppoWeatherApi:
        url = "https://weather.oppomobile.com/dailyForecastAd/v1/00282430113087"
        params = {
            "language": "zh-cn",
            "unit": "c",
            "appVerCode": "8002026",
            "appVerName": "8.2.26",
            "caller": "WEATHER_APP",
            "frontCode": "2.0",
            "fromWeatherApp": "true"
        }
