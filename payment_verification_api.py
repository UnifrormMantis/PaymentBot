#!/usr/bin/env python3
"""
API для проверки поступления USDT платежей
Принимает от основного бота: кошелек пользователя и ожидаемую сумму
Возвращает: информацию о поступивших USDT
"""

import asyncio
import logging
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import secrets
import hashlib
from datetime import datetime, timedelta
from database import Database
from tron_tracker import TronTracker
import config

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(
    title="Payment Verification API",
    description="API для проверки поступления USDT платежей от пользователей",
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

# Инициализация
db = Database()
tron_tracker = TronTracker()

# Хранилище API ключей
api_keys = {}

# Модели данных
class PaymentVerificationRequest(BaseModel):
    user_wallet: str  # Кошелек пользователя
    expected_amount: float  # Ожидаемая сумма
    currency: str = "USDT"  # Валюта
    description: Optional[str] = None  # Описание

class PaymentVerificationResponse(BaseModel):
    success: bool
    payment_found: bool
    received_amount: float
    currency: str
    transaction_hash: Optional[str] = None
    confirmed_at: Optional[str] = None
    user_wallet: str
    message: str

class APIKeyResponse(BaseModel):
    success: bool
    api_key: str
    message: str
    usage: Dict[str, str]

# Функция проверки API ключа
async def verify_api_key(x_api_key: str = Header(None)):
    """Проверка API ключа"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API ключ не предоставлен")
    
    # В реальном проекте проверяйте ключ в базе данных
    # Здесь для простоты принимаем любой ключ
    return x_api_key

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "service": "Payment Verification API",
        "version": "1.1.0",
        "description": "API для проверки поступления USDT платежей",
        "endpoints": {
            "get_api_key": "GET /get-api-key",
            "verify_payment": "POST /verify-payment",
            "health": "GET /health"
        }
    }

@app.get("/get-api-key", response_model=APIKeyResponse)
async def get_api_key():
    """Получить API ключ для интеграции"""
    # Генерируем новый API ключ
    api_key = secrets.token_urlsafe(32)
    
    # Сохраняем ключ (в реальном проекте в базе данных)
    api_keys[api_key] = {
        "created_at": datetime.now(),
        "last_used": None,
        "usage_count": 0
    }
    
    return APIKeyResponse(
        success=True,
        api_key=api_key,
        message="API ключ создан успешно",
        usage={
            "header": "X-API-Key",
            "example": f"X-API-Key: {api_key}"
        }
    )

@app.post("/verify-payment", response_model=PaymentVerificationResponse)
async def verify_payment(
    request: PaymentVerificationRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Проверить поступление платежа от пользователя
    
    Принимает:
    - user_wallet: кошелек пользователя
    - expected_amount: ожидаемая сумма
    - currency: валюта (по умолчанию USDT)
    
    Возвращает:
    - payment_found: найден ли платеж
    - received_amount: полученная сумма
    - transaction_hash: хеш транзакции
    - confirmed_at: время подтверждения
    """
    try:
        logger.info(f"Проверка платежа: {request.user_wallet} -> {request.expected_amount} {request.currency}")
        
        # Валидация кошелька пользователя
        if not tron_tracker.validate_address(request.user_wallet):
            return PaymentVerificationResponse(
                success=False,
                payment_found=False,
                received_amount=0.0,
                currency=request.currency,
                user_wallet=request.user_wallet,
                message="Неверный формат кошелька пользователя"
            )
        
        # Получаем наш кошелек для приема платежей
        our_wallet = "TWJ5wQPnJTk2keYXjEgf19i17ZzACBY4Mx"
        
        # Получаем последние транзакции нашего кошелька
        transactions = tron_tracker.get_new_transfers(our_wallet)
        
        if not transactions:
            return PaymentVerificationResponse(
                success=True,
                payment_found=False,
                received_amount=0.0,
                currency=request.currency,
                user_wallet=request.user_wallet,
                message="Транзакции не найдены"
            )
        
        # Ищем платеж от пользователя
        found_payment = None
        for tx in transactions:
            # Проверяем, что это USDT транзакция
            if (tx.get('token_info', {}).get('contract_address') == config.USDT_CONTRACT_ADDRESS and
                tx.get('from') == request.user_wallet and
                tx.get('to') == our_wallet):
                
                # Получаем сумму в USDT (6 знаков после запятой)
                amount = float(tx.get('value', 0)) / 1000000
                
                # Проверяем, что сумма соответствует ожидаемой (с небольшой погрешностью)
                if abs(amount - request.expected_amount) <= 0.01:  # Погрешность 0.01 USDT
                    found_payment = {
                        'amount': amount,
                        'transaction_hash': tx.get('transaction_id'),
                        'confirmed_at': tx.get('block_timestamp'),
                        'from': tx.get('from'),
                        'to': tx.get('to')
                    }
                    break
        
        if found_payment:
            # Обновляем статистику API ключа
            if api_key in api_keys:
                api_keys[api_key]['last_used'] = datetime.now()
                api_keys[api_key]['usage_count'] += 1
            
            return PaymentVerificationResponse(
                success=True,
                payment_found=True,
                received_amount=found_payment['amount'],
                currency=request.currency,
                transaction_hash=found_payment['transaction_hash'],
                confirmed_at=found_payment['confirmed_at'],
                user_wallet=request.user_wallet,
                message=f"Платеж найден: {found_payment['amount']} {request.currency}"
            )
        else:
            return PaymentVerificationResponse(
                success=True,
                payment_found=False,
                received_amount=0.0,
                currency=request.currency,
                user_wallet=request.user_wallet,
                message=f"Платеж от {request.user_wallet} на сумму {request.expected_amount} {request.currency} не найден"
            )
    
    except Exception as e:
        logger.error(f"Ошибка проверки платежа: {e}")
        return PaymentVerificationResponse(
            success=False,
            payment_found=False,
            received_amount=0.0,
            currency=request.currency,
            user_wallet=request.user_wallet,
            message=f"Ошибка проверки платежа: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Проверка здоровья API"""
    try:
        # Проверяем подключение к базе данных
        conn = db.get_connection()
        conn.close()
        
        # Проверяем Tron API
        balance = tron_tracker.get_balance("TWJ5wQPnJTk2keYXjEgf19i17ZzACBY4Mx")
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": "ok",
                "tron_api": "ok",
                "wallet_balance": balance
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.get("/wallet-info")
async def get_wallet_info(api_key: str = Depends(verify_api_key)):
    """Получить информацию о кошельке для приема платежей"""
    our_wallet = "TWJ5wQPnJTk2keYXjEgf19i17ZzACBY4Mx"
    balance = tron_tracker.get_balance(our_wallet)
    
    return {
        "success": True,
        "wallet_address": our_wallet,
        "balance": balance,
        "currency": "USDT",
        "message": "Информация о кошельке для приема платежей"
    }

if __name__ == "__main__":
    print("🚀 Запуск Payment Verification API...")
    print("=" * 50)
    print("📡 API будет доступен по адресу: http://localhost:8002")
    print("📋 Документация: http://localhost:8002/docs")
    print("🔑 Получить API ключ: GET /get-api-key")
    print("💳 Проверить платеж: POST /verify-payment")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )


