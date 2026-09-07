import time as time_
from datetime import datetime
from typing import List, Optional

import humps
from pydantic import BaseModel, ConfigDict, Field


class Wind(BaseModel):
    model_config = ConfigDict(
        alias_generator=humps.camelize,
        populate_by_name=True
    )
    
    speed_kts: float
    direction_degrees: float
    cardinal_str: str


class CurrentWeather(BaseModel):
    model_config = ConfigDict(
        alias_generator=humps.camelize,
        populate_by_name=True
    )
    
    outside_temp: float
    inside_temp: float
    pressure_MBar: float
    rain_rate: float
    wind: Wind


class IsoImageData(BaseModel):
    model_config = ConfigDict(
        alias_generator=humps.camelize,
        populate_by_name=True
    )
    
    description: str
    issued_time: str
    issued_time_ISO: datetime
    url: str
    valid_from_date_segment: str
    valid_from_time: str
    valid_from_time_ISO: datetime
    valid_from_time_segment: str


class IsobaricMaps(BaseModel):
    model_config = ConfigDict(
        alias_generator=humps.camelize,
        populate_by_name=True
    )
    
    image_data: List[IsoImageData]


class RainImageData(BaseModel):
    model_config = ConfigDict(
        alias_generator=humps.camelize,
        populate_by_name=True
    )
    
    date_time_ISO: datetime
    long_date_time: str
    short_date_time: str
    url: str
    valid_from: str
    valid_from_ISO: datetime
    valid_from_raw: int


class RainMaps(BaseModel):
    model_config = ConfigDict(
        alias_generator=humps.camelize,
        populate_by_name=True
    )
    
    image_data: List[RainImageData]


class CelestialData(BaseModel):
    model_config = ConfigDict(
        alias_generator=humps.camelize,
        populate_by_name=True
    )
    
    day: str
    day_ISO: datetime
    first_light: str
    first_light_ISO: datetime
    last_light: str
    last_light_ISO: datetime
    moon_rise: Optional[str] = None
    moon_rise_ISO: Optional[datetime] = None
    moon_set: Optional[str] = None
    moon_set_ISO: Optional[datetime] = None
    sun_rise: str
    sun_rise_hour: int
    sun_rise_ISO: datetime
    sun_set: str
    sun_set_hour: int
    sun_set_ISO: datetime


class ForecastDayData(BaseModel):
    model_config = ConfigDict(
        alias_generator=humps.camelize,
        populate_by_name=True
    )
    
    date: str
    date_ISO: datetime
    dow: str
    forecast: str
    forecast_word: str
    issued_at: str
    issued_at_ISO: datetime
    issued_at_raw: int
    max: int
    min: int
    rise_set: CelestialData


class Forecast(BaseModel):
    model_config = ConfigDict(
        alias_generator=humps.camelize,
        populate_by_name=True
    )
    
    days: List[ForecastDayData]


# LEGACY MODELS #


class AllMaps(BaseModel):
    iso: List[IsoImageData]
    rain: List[RainImageData]


class LegacyCurrentWeather(BaseModel):
    version: str
    current: CurrentWeather
    time: int = Field(default_factory=lambda: int(time_.time() * 1000.0))
    forecasts: List[ForecastDayData]
    maps: AllMaps
