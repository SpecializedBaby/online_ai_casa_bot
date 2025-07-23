from aiocryptopay import AioCryptoPay, Networks
from aiocryptopay.const import InvoiceStatus
from aiocryptopay.models.invoice import Invoice

from bot.config import get_config

config = get_config()

network_API = None

if config.network_api_crypto_pay == "TEST_NET":
    network_API = Networks.TEST_NET
elif config.network_api_crypto_pay == "MAIN_NET":
    network_API = Networks.MAIN_NET

crypto = AioCryptoPay(token=config.crypto_pay_token, network=network_API)


async def get_info_crypto_app():
    profile = await crypto.get_me()
    currencies = await crypto.get_currencies()
    balance = await crypto.get_balance()
    rates = await crypto.get_exchange_rates()
    stats = await crypto.get_stats()

    return {
        "profile": profile,
        "currencies": currencies,
        "balance": balance,
        "rates": rates,
        "stats": stats,
    }


async def create_invoice(amount: float, currency: str = "USDT") -> Invoice:
    invoice = await crypto.create_invoice(asset=currency, amount=amount)
    print(f"URL invoice: {invoice.bot_invoice_url}")
    return invoice


async def create_fiat_invoice(
        amount: float,
        fiat: str = "USD",
        currency_type: str = "fiat"
) -> Invoice:
    fiat_invoice = await crypto.create_invoice(
        amount=amount,
        fiat=fiat,
        currency_type=currency_type
    )
    print(fiat_invoice)
    return fiat_invoice


async def get_invoice_status(invoice_id: int) -> InvoiceStatus | str:
    invoice = await crypto.get_invoices(invoice_ids=invoice_id)
    print(invoice.status)
    return invoice.status


def get_invoice_id(invoice: Invoice) -> int:
    return invoice.invoice_id


async def delete_invoice(invoice_id: int) -> bool:
    deleted_invoice = await crypto.delete_invoice(invoice_id=invoice_id)
    return deleted_invoice
