from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from typing import Optional

app = FastAPI(title="Google Maps Proxy API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción podrías limitarlo a tu app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key de Google Maps (desde variable de entorno)
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

@app.get("/")
async def root():
    return {
        "status": "OK",
        "message": "Google Maps Proxy API funcionando",
        "endpoints": [
            "/api/maps/search-places",
            "/api/maps/place-details"
        ]
    }

@app.get("/api/maps/search-places")
async def search_places(
    query: str = Query(..., min_length=3, description="Término de búsqueda"),
    location: Optional[str] = Query(None, description="Latitud,Longitud para búsqueda cercana")
):
    """
    Buscar lugares usando Google Places Autocomplete
    """
    try:
        # Parámetros para Google Places API
        params = {
            "input": query,
            "key": GOOGLE_MAPS_API_KEY,
            "language": "es",
            "components": "country:mx"
        }
        
        # Si hay ubicación, agregar radio de búsqueda
        if location:
            params["location"] = location
            params["radius"] = 50000  # 50km
        
        print(f"🔍 Búsqueda: '{query}'{' cerca de ' + location if location else ''}")
        
        # Hacer petición a Google
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/place/autocomplete/json",
                params=params,
                timeout=10.0
            )
            response.raise_for_status()
            
        data = response.json()
        
        print(f"✅ Resultados: {len(data.get('predictions', []))} lugares encontrados")
        
        return data
        
    except httpx.HTTPError as e:
        print(f"❌ Error HTTP: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al consultar Google Maps: {str(e)}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/maps/place-details")
async def place_details(
    place_id: str = Query(..., description="ID del lugar de Google Places")
):
    """
    Obtener detalles de un lugar específico
    """
    try:
        print(f"📍 Obteniendo detalles de: {place_id}")
        
        # Parámetros para Google Places Details API
        params = {
            "place_id": place_id,
            "key": GOOGLE_MAPS_API_KEY,
            "language": "es",
            "fields": "geometry,name,formatted_address,address_components"
        }
        
        # Hacer petición a Google
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/place/details/json",
                params=params,
                timeout=10.0
            )
            response.raise_for_status()
            
        data = response.json()
        
        print(f"✅ Detalles obtenidos para: {data.get('result', {}).get('name', 'N/A')}")
        
        return data
        
    except httpx.HTTPError as e:
        print(f"❌ Error HTTP: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al consultar Google Maps: {str(e)}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/maps/geocode")
async def geocode_address(
    address: str = Query(..., description="Dirección a geocodificar")
):
    """
    Convertir dirección de texto a coordenadas
    """
    try:
        print(f"🗺️ Geocodificando: {address}")
        
        params = {
            "address": address,
            "key": GOOGLE_MAPS_API_KEY,
            "language": "es",
            "components": "country:mx"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params=params,
                timeout=10.0
            )
            response.raise_for_status()
            
        data = response.json()
        
        print(f"✅ Geocoding exitoso")
        
        return data
        
    except httpx.HTTPError as e:
        print(f"❌ Error HTTP: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al geocodificar: {str(e)}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint de salud para Render
@app.get("/health")
async def health_check():
    return {"status": "healthy"}