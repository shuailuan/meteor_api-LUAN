# Meteor API Server

Locally hosted API server to integrate a WS2080 weather station and the New Zealand MetService public API. This allows current local weather data to be combined with forecast data and maps from the MetService. 
- Requires an accessable instance of [WeeWX](https://www.weewx.com/docs.html) connected to the local weather station.
- External MetService API calls are cached (60 seconds).

## JSON Endpoints

### Forecasts
Returns an array of seven days of MetService forecast data.

*http://<server_ip>/forecasts*

```
{
    "days": [
        {
            "date": "27 Jul",
            "dateISO": "2022-07-27T12:00:00+12:00",
            "dow": "Wednesday",
            "forecast": "Scattered rain clearing this evening. Southwesterlies.",
            "forecastWord": "Few showers",
            "issuedAt": "9:03am 27 Jul",
            "issuedAtISO": "2022-07-27T09:03:00+12:00",
            "issuedAtRaw": 1658869380000,
            "max": 12,
            "min": 2,
            "riseSet": {
                "day": "27 July 2022",
                "dayISO": "2022-07-27T00:00:00+12:00",
                "firstLight": "7:17am",
                "firstLightISO": "2022-07-27T07:17:00+12:00",
                "lastLight": "5:57pm",
                "lastLightISO": "2022-07-27T17:57:00+12:00",
                "moonRise": "7:02am",
                "moonRiseISO": "2022-07-27T07:02:00+12:00",
                "moonSet": "3:32pm",
                "moonSetISO": "2022-07-27T15:32:00+12:00",
                "sunRise": "7:48am",
                "sunRiseHour": 8,
                "sunRiseISO": "2022-07-27T07:48:00+12:00",
                "sunSet": "5:26pm",
                "sunSetHour": 17,
                "sunSetISO": "2022-07-27T17:26:00+12:00"
            }
        },
    ]
}
```

## Rain Maps

Returns an array of MetService rain map data.

*http://<server_ip>/rain-maps*
```
{
    "imageData": [
        {
            "dateTimeISO": "2022-07-27T10:43:00+12:00",
            "longDateTime": "10:43am Wed, 27 Jul",
            "shortDateTime": "10:43am Wed",
            "url": "https://MetService.com/publicData/rainRadar/image/CHRISTCHURCH/300K/2022-07-27T10:43:00+12:00",
            "validFrom": "10:43am Wed, 27 Jul",
            "validFromISO": "2022-07-27T10:43:00+12:00",
            "validFromRaw": 1658875380000
        },
    ]
}
```

### Isobaric Map Data

Returns an array of MetService isobaric map data.

*http://<server_ip>/iso-maps*

```
{
    "imageData": [
        {
            "description": "Analysis for 6am Tue, 26 Jul",
            "issuedTime": "7:51am Tue, 26 Jul",
            "issuedTimeISO": "2022-07-26T07:51:00+12:00",
            "url": "https://MetService.com/IcePics/fc/5d9-18236840d00-18236840d00-18236840d00-18236ea0fb1.gif",
            "validFromDateSegment": "Tue, 26 Jul",
            "validFromTime": "6am Tue, 26 Jul",
            "validFromTimeISO": "2022-07-26T06:00:00+12:00",
            "validFromTimeSegment": "6am"
        },
    ]
}
```

### Current Conditions

Returns the current local conditions.

*http://<server_ip>/current*

```
{
    "outsideTemp": 9.7,
    "insideTemp": 24.8,
    "pressureMBar": 999.0,
    "rainRate": 0.0,
    "wind": {
        "speedKts": 7.0,
        "directionDegrees": 232.0,
        "cardinalStr": "SW"
    }
}
```

## Development

Add a *.env* file to the project root with the following environmental variable;
```
DEBUG=1
```
To start the dev server run;
```
python -m app
```
Server hot reloading will be enabled on code changes.

## Tests

```
python -m pytest
```

## Settings

The following variables can be configured in the *.env* file;
| Variable     | Description       |
| ------------ | ----------------- |
| DEBUG        | 1 if enabled      |
| HOST         | Defaults to 0.0.0.0 |
| PORT         | Defaults to 8001  |
| CITY         | **Required.** City required for forecast data (see **Valid Cities**) |
| RADAR_LOCATION | **Required.** Location of radar for rain map data (see **Valid Radar Locations**)
| WX_STATION_URL | **Required.** URL of local weather station e.g http://192.168.1.99 |

## Deployment

The application can either be run standalone;

```
python -m app
```
Or via Docker;

```
docker build -t meteor_api .
```
```
docker run -p 8001:8001 \
    -e CITY=Christchurch \
    -e RADAR_LOCATION=nz \
    -e WX_STATION_URL=http://192.168.1.99 \
    -d meteor_api
```

## Valid Cities

All cities tested and verified with MetService API (42 cities):

### Northland
- kaitaia
- kerikeri
- paihia
- russell
- whangarei
- dargaville

### Auckland & Waikato
- auckland
- hamilton
- whitianga
- thames

### Bay of Plenty & Rotorua
- tauranga
- rotorua
- whakatane
- taupo

### East Coast
- gisborne
- napier
- hastings

### Taranaki & Central North Island
- new-plymouth
- taumarunui
- wanganui
- palmerston-north

### Wairarapa & Wellington
- masterton
- levin
- paraparaumu
- wellington

### Nelson & Marlborough
- blenheim
- nelson
- motueka

### West Coast
- westport
- reefton
- greymouth
- hokitika

### Canterbury
- kaikoura
- christchurch
- ashburton
- timaru

### Otago
- oamaru
- dunedin
- queenstown
- wanaka

### Southland
- invercargill
- milford-sound

**Note:** City identifiers are case-sensitive and use lowercase with hyphens.

## Valid Radar Locations

- nz

- northland

- auckland

- bop

- mahia

- new-plymouth

- wellington

- westland

- christchurch

- invercargill
