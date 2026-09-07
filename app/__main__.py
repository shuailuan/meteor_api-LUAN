import asyncio

import aiohttp
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from app import external_services as services
from app.config import Settings, get_settings
from app.models import (
    AllMaps,
    CurrentWeather,
    Forecast,
    IsobaricMaps,
    LegacyCurrentWeather,
    RainMaps,
)
from app.sessions import close_session, get_session

app = FastAPI(title="NZ Weather Forecast API")


@app.on_event("shutdown")
async def shutdown_event():
    await close_session()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with city selector UI"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NZ Weather Forecast</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                text-align: center;
                color: white;
                margin-bottom: 30px;
            }
            .header h1 {
                font-size: 2.5rem;
                margin-bottom: 10px;
            }
            .controls {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }
            .city-selector {
                display: flex;
                gap: 15px;
                align-items: center;
                flex-wrap: wrap;
            }
            .city-selector label {
                font-weight: 600;
                color: #333;
            }
            .city-selector select {
                flex: 1;
                min-width: 200px;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 1rem;
                cursor: pointer;
                transition: border-color 0.3s;
            }
            .city-selector select:focus {
                outline: none;
                border-color: #667eea;
            }
            .city-selector button {
                padding: 12px 30px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.3s;
            }
            .city-selector button:hover {
                background: #5568d3;
            }
            .city-selector button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            .loading {
                text-align: center;
                padding: 40px;
                color: white;
                font-size: 1.2rem;
            }
            .error {
                background: #ff6b6b;
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            .forecast-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }
            .forecast-card {
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s;
            }
            .forecast-card:hover {
                transform: translateY(-5px);
            }
            .forecast-card .day {
                font-size: 1.2rem;
                font-weight: 700;
                color: #667eea;
                margin-bottom: 5px;
            }
            .forecast-card .date {
                color: #666;
                font-size: 0.9rem;
                margin-bottom: 15px;
            }
            .forecast-card .temps {
                display: flex;
                gap: 15px;
                margin-bottom: 15px;
                font-size: 1.5rem;
                font-weight: 600;
            }
            .forecast-card .temp-max {
                color: #ff6b6b;
            }
            .forecast-card .temp-min {
                color: #4ecdc4;
            }
            .forecast-card .forecast-word {
                display: inline-block;
                padding: 8px 15px;
                background: #f0f0f0;
                border-radius: 20px;
                font-size: 0.9rem;
                font-weight: 600;
                margin-bottom: 15px;
                color: #333;
            }
            .forecast-card .details {
                color: #666;
                line-height: 1.6;
                margin-bottom: 15px;
            }
            .forecast-card .sun-times {
                display: flex;
                gap: 20px;
                font-size: 0.85rem;
                color: #999;
                padding-top: 15px;
                border-top: 1px solid #e0e0e0;
            }
            @media (max-width: 768px) {
                .header h1 {
                    font-size: 1.8rem;
                }
                .forecast-container {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌦️ New Zealand Weather Forecast</h1>
                <p>Select a city to view the 10-day forecast</p>
            </div>
            
            <div class="controls">
                <div class="city-selector">
                    <label for="citySelect">Choose a city:</label>
                    <select id="citySelect">
                        <!-- Northland -->
                        <option value="kaitaia">Kaitaia</option>
                        <option value="kerikeri">Kerikeri</option>
                        <option value="paihia">Paihia</option>
                        <option value="russell">Russell</option>
                        <option value="whangarei">Whangarei</option>
                        <option value="dargaville">Dargaville</option>
                        
                        <!-- Auckland & Waikato -->
                        <option value="auckland">Auckland</option>
                        <option value="hamilton">Hamilton</option>
                        <option value="whitianga">Whitianga</option>
                        <option value="thames">Thames</option>
                        
                        <!-- Bay of Plenty & Rotorua -->
                        <option value="tauranga">Tauranga</option>
                        <option value="rotorua">Rotorua</option>
                        <option value="whakatane">Whakatane</option>
                        <option value="taupo">Taupo</option>
                        
                        <!-- East Coast -->
                        <option value="gisborne">Gisborne</option>
                        <option value="napier">Napier</option>
                        <option value="hastings">Hastings</option>
                        
                        <!-- Taranaki & Central -->
                        <option value="new-plymouth">New Plymouth</option>
                        <option value="taumarunui">Taumarunui</option>
                        <option value="wanganui">Wanganui</option>
                        <option value="palmerston-north">Palmerston North</option>
                        
                        <!-- Wairarapa & Wellington -->
                        <option value="masterton">Masterton</option>
                        <option value="levin">Levin</option>
                        <option value="paraparaumu">Paraparaumu</option>
                        <option value="wellington">Wellington</option>
                        
                        <!-- Nelson & Marlborough -->
                        <option value="blenheim">Blenheim</option>
                        <option value="nelson">Nelson</option>
                        <option value="motueka">Motueka</option>
                        
                        <!-- West Coast -->
                        <option value="westport">Westport</option>
                        <option value="reefton">Reefton</option>
                        <option value="greymouth">Greymouth</option>
                        <option value="hokitika">Hokitika</option>
                        
                        <!-- Canterbury -->
                        <option value="kaikoura">Kaikoura</option>
                        <option value="christchurch" selected>Christchurch</option>
                        <option value="ashburton">Ashburton</option>
                        <option value="timaru">Timaru</option>
                        
                        <!-- Otago -->
                        <option value="oamaru">Oamaru</option>
                        <option value="dunedin">Dunedin</option>
                        <option value="queenstown">Queenstown</option>
                        <option value="wanaka">Wanaka</option>
                        
                        <!-- Southland -->
                        <option value="invercargill">Invercargill</option>
                        <option value="milford-sound">Milford Sound</option>
                    </select>
                    <button id="fetchBtn" onclick="fetchForecast()">Get Forecast</button>
                </div>
            </div>
            
            <div id="loadingDiv" class="loading" style="display: none;">
                Loading forecast data...
            </div>
            
            <div id="errorDiv" class="error" style="display: none;"></div>
            
            <div id="forecastContainer" class="forecast-container"></div>
        </div>
        
        <script>
            // Fetch forecast on page load for default city
            window.addEventListener('DOMContentLoaded', () => {
                fetchForecast();
            });
            
            async function fetchForecast() {
                const citySelect = document.getElementById('citySelect');
                const city = citySelect.value;
                const loadingDiv = document.getElementById('loadingDiv');
                const errorDiv = document.getElementById('errorDiv');
                const forecastContainer = document.getElementById('forecastContainer');
                const fetchBtn = document.getElementById('fetchBtn');
                
                // Show loading state
                loadingDiv.style.display = 'block';
                errorDiv.style.display = 'none';
                forecastContainer.innerHTML = '';
                fetchBtn.disabled = true;
                
                try {
                    const response = await fetch(`/forecasts?city=${city}`);
                    
                    if (!response.ok) {
                        // Try to get error detail from response
                        let errorMessage = `HTTP error! status: ${response.status}`;
                        try {
                            const errorData = await response.json();
                            if (errorData.detail) {
                                errorMessage = errorData.detail;
                            }
                        } catch (e) {
                            // If JSON parsing fails, use default message
                        }
                        throw new Error(errorMessage);
                    }
                    
                    const data = await response.json();
                    displayForecast(data);
                } catch (error) {
                    console.error('Error fetching forecast:', error);
                    errorDiv.innerHTML = `
                        <strong>⚠️ Failed to load forecast for "${citySelect.options[citySelect.selectedIndex].text}"</strong><br>
                        ${error.message}<br><br>
                        <small>Note: Some cities may not be available in the MetService API. Try selecting a different city.</small>
                    `;
                    errorDiv.style.display = 'block';
                } finally {
                    loadingDiv.style.display = 'none';
                    fetchBtn.disabled = false;
                }
            }
            
            function getWeatherIcon(forecastWord) {
                // Map forecast words to weather icons
                const word = forecastWord.toLowerCase();
                
                if (word.includes('fine') || word.includes('sunny')) return '☀️';
                if (word.includes('clear')) return '🌙';
                if (word.includes('partly cloudy') || word.includes('some cloud')) return '⛅';
                if (word.includes('cloudy') || word.includes('overcast')) return '☁️';
                if (word.includes('rain') && word.includes('heavy')) return '🌧️';
                if (word.includes('rain') || word.includes('showers')) return '🌦️';
                if (word.includes('drizzle')) return '🌧️';
                if (word.includes('snow')) return '❄️';
                if (word.includes('thunder') || word.includes('storm')) return '⛈️';
                if (word.includes('fog') || word.includes('mist')) return '🌫️';
                if (word.includes('wind')) return '💨';
                if (word.includes('hail')) return '🧊';
                
                // Default icon
                return '🌤️';
            }
            
            function displayForecast(data) {
                const forecastContainer = document.getElementById('forecastContainer');
                forecastContainer.innerHTML = '';
                
                if (!data.days || data.days.length === 0) {
                    forecastContainer.innerHTML = '<p style="color: white; text-align: center;">No forecast data available</p>';
                    return;
                }
                
                data.days.forEach(day => {
                    const card = document.createElement('div');
                    card.className = 'forecast-card';
                    
                    const weatherIcon = getWeatherIcon(day.forecastWord);
                    
                    let sunTimes = '';
                    if (day.riseSet) {
                        sunTimes = `
                            <div class="sun-times">
                                <span>🌅 ${day.riseSet.sunRise || 'N/A'}</span>
                                <span>🌇 ${day.riseSet.sunSet || 'N/A'}</span>
                            </div>
                        `;
                    }
                    
                    card.innerHTML = `
                        <div class="day">${day.dow}</div>
                        <div class="date">${day.date}</div>
                        <div class="temps">
                            <span class="temp-max">${day.max}°C</span>
                            <span class="temp-min">${day.min}°C</span>
                        </div>
                        <span class="forecast-word">${weatherIcon} ${day.forecastWord}</span>
                        <div class="details">${day.forecast}</div>
                        ${sunTimes}
                    `;
                    
                    forecastContainer.appendChild(card);
                });
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/forecasts", response_model=Forecast)
async def get_forecasts(
    city: str = Query(None, description="City name for forecast"),
    session: aiohttp.ClientSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
):
    # Use query parameter if provided, otherwise fall back to settings
    selected_city = city if city else settings.city
    if selected_city is None:
        raise HTTPException(400, "City parameter is required")
    
    try:
        forecast = await services.get_forecasts(session, city=selected_city)
        return forecast
    except Exception as e:
        # Handle validation errors (city not found) and other errors gracefully
        error_msg = str(e)
        if "Field required" in error_msg or "ValidationError" in error_msg:
            raise HTTPException(404, f"Forecast data not available for '{selected_city}'. This city may not be supported by the MetService API.")
        else:
            raise HTTPException(500, f"Error fetching forecast: {error_msg}")


@app.get("/rain-maps", response_model=RainMaps)
async def get_rain_maps(session=Depends(get_session), settings=Depends(get_settings)):
    if settings.radar_location is None:
        raise HTTPException(502, "Configuration error")
    return await services.get_rain_map_data(
        session, radar_location=settings.radar_location
    )


@app.get("/iso-maps", response_model=IsobaricMaps)
async def get_iso_maps(met_session=Depends(get_session)):
    return await services.get_iso_map_data(met_session)


@app.get("/current", response_model=CurrentWeather)
async def get_current_conditions(
    session=Depends(get_session), settings: Settings = Depends(get_settings)
):
    if settings.wx_station_url is None:
        raise HTTPException(502, "Configuration error")
    return await services.get_current_data(
        session, wx_station_url=settings.wx_station_url
    )


@app.get("/data", response_model=LegacyCurrentWeather)
@app.get("/data/", include_in_schema=False)
async def get_legacy_weather(
    session=Depends(get_session),
    settings: Settings = Depends(get_settings),
):
    if (
        settings.city is None
        or settings.radar_location is None
        or settings.wx_station_url is None
    ):
        raise HTTPException(502, "Configuration error")
    (
        result_current,
        result_forecasts,
        results_rain_maps,
        results_iso_maps,
    ) = await asyncio.gather(
        services.get_current_data(session, wx_station_url=settings.wx_station_url),
        services.get_forecasts(session, city=settings.city),
        services.get_rain_map_data(session, radar_location=settings.radar_location),
        services.get_iso_map_data(session),
    )
    return LegacyCurrentWeather(
        version=settings.version,
        current=result_current,
        forecasts=result_forecasts.days,
        maps=AllMaps(
            rain=results_rain_maps.image_data, iso=results_iso_maps.image_data
        ),
    )


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run("app.__main__:app", host="0.0.0.0", port=settings.port, reload=settings.debug, root_path=settings.root_path)  # type: ignore
