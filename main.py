from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

app = FastAPI()

# Tüm tarayıcılardan ve domainlerden istek alabilmesi için CORS ayarı
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bellekte tutulacak ortak veri tabanı
shared_grid_data = {}

class SlotData(BaseModel):
    size: int
    name: str
    url: str
    platform: str
    logoMode: str
    customLogo: str
    expireTime: int

@app.get("/api/grid")
def get_grid():
    # Süresi dolanları otomatik temizle (30 gün)
    now = time.time() * 1000
    expired_keys = [k for k, v in shared_grid_data.items() if now > v.get("expireTime", 0)]
    for k in expired_keys:
        del shared_grid_data[k]
        
    return shared_grid_data

@app.post("/api/grid/{slot_id}")
def update_grid(slot_id: str, data: SlotData):
    shared_grid_data[slot_id] = data.dict()
    return {"status": "success", "message": f"Slot {slot_id} güncellendi."}

@app.delete("/api/grid/{slot_id}")
def delete_grid(slot_id: str):
    if slot_id in shared_grid_data:
        del shared_grid_data[slot_id]
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Slot bulunamadı")