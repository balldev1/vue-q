from datetime import datetime
from fastapi import FastAPI, WebSocket, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()  # โหลดค่าจากไฟล์ .env
DATABASE_URL = os.getenv("DATABASE_URL")  # อ่านค่าจาก .env

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # หรือกำหนด URL ที่อนุญาต เช่น ["http://localhost:8080"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TruckQueue(Base):
    __tablename__ = "truck_queue"
    id = Column(Integer, primary_key=True, index=True)
    truck_type = Column(String)
    entry_time = Column(DateTime)
    exit_time = Column(DateTime)
    door_type = Column(String)

class TruckQueueCreate(BaseModel):
    truck_type: str
    door_type: str

class TruckType(Base):
    __tablename__ = "truck_type"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

class DoorType(Base):
    __tablename__ = "door_type"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, unique=True)

Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    try:
        # เพิ่ม Truck Types
        if not db.query(TruckType).first():  # ตรวจสอบว่ามีข้อมูลอยู่แล้วหรือไม่
            truck_types = ["10-wheeled", "6-wheeled", "Pickup"]
            for truck in truck_types:
                db.add(TruckType(name=truck))

        # เพิ่ม Door Types
        if not db.query(DoorType).first():  # ตรวจสอบว่ามีข้อมูลอยู่แล้วหรือไม่
            door_numbers = ["1", "2", "3"]
            for door in door_numbers:
                db.add(DoorType(number=door))

        db.commit()
    finally:
        db.close()

# เรียกใช้ seed_data
seed_data()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"New queue entry: {data}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/truck-types/")
def get_truck_types(db: Session = Depends(get_db)):
    return db.query(TruckType).all()

@app.get("/api/door-types/")
def get_door_types(db: Session = Depends(get_db)):
    return db.query(DoorType).all()

@app.post("/api/queue/")
def create_queue(queue: TruckQueueCreate, db: Session = Depends(get_db)):
    db_queue = TruckQueue(truck_type=queue.truck_type, entry_time=datetime.now(), door_type=queue.door_type)
    db.add(db_queue)
    db.commit()
    db.refresh(db_queue)
    return db_queue

@app.get("/api/queue/")
def read_queues(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    queues = db.query(TruckQueue).offset(skip).limit(limit).all()
    return queues

@app.delete("/api/queue/{queue_id}")
def delete_queue(queue_id: int, db: Session = Depends(get_db)):
    db_queue = db.query(TruckQueue).filter(TruckQueue.id == queue_id).first()
    if db_queue is None:
        raise HTTPException(status_code=404, detail="Queue not found")
    db.delete(db_queue)
    db.commit()
    return {"detail": "Queue deleted"}
