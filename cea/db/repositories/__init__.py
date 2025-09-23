from cea.db.models import CurrencyRate, Deal
from cea.db.repositories.currency_rate import CurrencyRateRepository
from cea.db.repositories.deal import DealRepository

currency_rate_repository = CurrencyRateRepository(CurrencyRate)
deal_repository = DealRepository(Deal)
