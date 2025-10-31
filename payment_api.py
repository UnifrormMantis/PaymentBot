#!/usr/bin/env python3
"""
API сервер для платежной системы
Предоставляет HTTP API для интеграции с другими ботами
"""

import asyncio
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
from payment_integration import PaymentIntegration
import config

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(
    title="Payment Bot API",
    description="API для интеграции TRC20 платежей в Telegram боты",
    version="1.1.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация платежной системы
payment_system = PaymentIntegration()

# Модели данных
class PaymentRequest(BaseModel):
    user_id: int
    amount: float
    currency: str = "USDT"
    description: Optional[str] = None

class AutoPaymentRequest(BaseModel):
    user_id: int
    wallet_address: str
    description: Optional[str] = None

class PaymentStatusResponse(BaseModel):
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None

class BalanceResponse(BaseModel):
    success: bool
    wallet_address: Optional[str] = None
    balance: Optional[float] = None
    currency: Optional[str] = None
    error: Optional[str] = None

class PaymentCallback(BaseModel):
    user_id: int
    amount: float
    currency: str
    transaction_hash: str
    wallet_address: str

# Глобальный словарь для хранения callback функций
payment_callbacks: Dict[int, callable] = {}

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "Payment Bot API",
        "version": "1.1.0",
        "status": "running",
        "endpoints": [
            "/docs - Swagger документация",
            "/health - Проверка здоровья",
            "/payment/create - Создать платеж",
            "/payment/auto - Настроить автоматический платеж",
            "/payment/status - Статус платежей",
            "/payment/balance - Баланс кошелька",
            "/payment/callback - Регистрация callback"
        ]
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья API"""
    return {
        "status": "healthy",
        "payment_system": "active",
        "database": "connected"
    }

@app.post("/payment/create", response_model=PaymentStatusResponse)
async def create_payment(request: PaymentRequest):
    """Создание платежа"""
    try:
        result = await payment_system.create_payment_request(
            user_id=request.user_id,
            amount=request.amount,
            currency=request.currency,
            description=request.description
        )
        
        if result['success']:
            return PaymentStatusResponse(
                success=True,
                data=result
            )
        else:
            return PaymentStatusResponse(
                success=False,
                error=result['error']
            )
    except Exception as e:
        logger.error(f"Ошибка создания платежа: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/payment/auto", response_model=PaymentStatusResponse)
async def setup_auto_payment(request: AutoPaymentRequest):
    """Настройка автоматического платежа"""
    try:
        result = await payment_system.create_auto_payment_request(
            user_id=request.user_id,
            wallet_address=request.wallet_address,
            description=request.description
        )
        
        if result['success']:
            return PaymentStatusResponse(
                success=True,
                data=result
            )
        else:
            return PaymentStatusResponse(
                success=False,
                error=result['error']
            )
    except Exception as e:
        logger.error(f"Ошибка настройки автоматического платежа: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/payment/status/{user_id}", response_model=PaymentStatusResponse)
async def get_payment_status(user_id: int, payment_id: Optional[int] = None):
    """Получение статуса платежей"""
    try:
        result = await payment_system.check_payment_status(user_id, payment_id)
        
        if result['success']:
            return PaymentStatusResponse(
                success=True,
                data=result
            )
        else:
            return PaymentStatusResponse(
                success=False,
                error=result['error']
            )
    except Exception as e:
        logger.error(f"Ошибка получения статуса платежей: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/payment/balance/{user_id}", response_model=BalanceResponse)
async def get_wallet_balance(user_id: int):
    """Получение баланса кошелька"""
    try:
        result = await payment_system.get_wallet_balance(user_id)
        
        if result['success']:
            return BalanceResponse(
                success=True,
                wallet_address=result['wallet_address'],
                balance=result['balance'],
                currency=result['currency']
            )
        else:
            return BalanceResponse(
                success=False,
                error=result['error']
            )
    except Exception as e:
        logger.error(f"Ошибка получения баланса: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/payment/callback/{user_id}")
async def register_callback(user_id: int, callback_url: str):
    """Регистрация callback URL для уведомлений о платежах"""
    try:
        # Здесь можно добавить логику для HTTP callback'ов
        # Пока просто сохраняем URL
        payment_callbacks[user_id] = callback_url
        
        logger.info(f"Зарегистрирован callback для пользователя {user_id}: {callback_url}")
        
        return {
            "success": True,
            "message": f"Callback зарегистрирован для пользователя {user_id}",
            "callback_url": callback_url
        }
    except Exception as e:
        logger.error(f"Ошибка регистрации callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/payment/callback/{user_id}")
async def unregister_callback(user_id: int):
    """Отмена регистрации callback"""
    try:
        if user_id in payment_callbacks:
            del payment_callbacks[user_id]
            logger.info(f"Отменена регистрация callback для пользователя {user_id}")
            return {
                "success": True,
                "message": f"Callback отменен для пользователя {user_id}"
            }
        else:
            return {
                "success": False,
                "message": f"Callback не найден для пользователя {user_id}"
            }
    except Exception as e:
        logger.error(f"Ошибка отмены регистрации callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/payment/callbacks")
async def list_callbacks():
    """Список зарегистрированных callback'ов"""
    return {
        "success": True,
        "callbacks": list(payment_callbacks.keys()),
        "count": len(payment_callbacks)
    }

@app.get("/payment/info")
async def get_payment_info():
    """Информация о платежной системе"""
    try:
        info = payment_system.get_integration_info()
        return {
            "success": True,
            "info": info
        }
    except Exception as e:
        logger.error(f"Ошибка получения информации: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Фоновая задача для обработки платежей
async def process_payments_task():
    """Фоновая задача для обработки платежей"""
    while True:
        try:
            await payment_system.process_payments()
            await asyncio.sleep(config.CHECK_INTERVAL)
        except Exception as e:
            logger.error(f"Ошибка в фоновой задаче обработки платежей: {e}")
            await asyncio.sleep(60)  # Ждем минуту при ошибке

@app.on_event("startup")
async def startup_event():
    """Событие запуска приложения"""
    logger.info("🚀 Запуск Payment Bot API...")
    
    # Запускаем фоновую задачу обработки платежей
    asyncio.create_task(process_payments_task())
    
    logger.info("✅ Payment Bot API запущен успешно")

@app.on_event("shutdown")
async def shutdown_event():
    """Событие остановки приложения"""
    logger.info("🛑 Остановка Payment Bot API...")

if __name__ == "__main__":
    # Запуск сервера
    uvicorn.run(
        "payment_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )





