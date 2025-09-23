from fastapi import APIRouter
from cea.api.currency_rates import router as currency_rates_router
from cea.api.deal import router as deal_router

router = APIRouter()


router.include_router(currency_rates_router, tags=['Currency Rates'])
router.include_router(deal_router, tags=['Deal'])
