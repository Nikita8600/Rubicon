from decimal import Decimal

from django.contrib.auth.models import User
from django.db import transaction as db_transaction
from django.utils import timezone

from .models import BankAccount, Card, Notification, Transaction

MINIMUM_WITHDRAWAL = Decimal("100.00")


def _active_account_for_user(user, account_id):
    return (
        BankAccount.objects.select_for_update()
        .filter(id=account_id, user=user, status="ACTIVE")
        .first()
    )


@db_transaction.atomic
def deposit_money(user, account_id, amount, description=""):
    amount = Decimal(amount)
    if amount <= 0:
        raise ValueError("Deposit amount must be greater than ₹0.")

    account = _active_account_for_user(user, account_id)
    if not account:
        raise ValueError("Active bank account not found.")

    account.balance += amount
    account.save(update_fields=["balance", "updated_at"])

    txn = Transaction.objects.create(
        user=user,
        account=account,
        transaction_type="DEPOSIT",
        amount=amount,
        description=description or "Cash deposit",
        balance_after=account.balance,
        status="SUCCESS",
    )

    Notification.objects.create(
        user=user,
        title="Deposit Successful",
        message=f"₹{amount:.2f} has been deposited into your account.",
    )
    return txn


@db_transaction.atomic
def withdraw_money(user, account_id, amount, description=""):
    amount = Decimal(amount)
    if amount < MINIMUM_WITHDRAWAL:
        raise ValueError("Minimum withdrawal amount is ₹100.")

    account = _active_account_for_user(user, account_id)
    if not account:
        raise ValueError("Active bank account not found.")

    remaining = account.balance - amount
    if remaining < account.minimum_balance:
        raise ValueError(
            f"Minimum balance of ₹{account.minimum_balance:.2f} must be maintained."
        )

    account.balance = remaining
    account.save(update_fields=["balance", "updated_at"])

    txn = Transaction.objects.create(
        user=user,
        account=account,
        transaction_type="WITHDRAW",
        amount=amount,
        description=description or "Cash withdrawal",
        balance_after=account.balance,
        status="SUCCESS",
    )

    Notification.objects.create(
        user=user,
        title="Withdrawal Successful",
        message=f"₹{amount:.2f} has been withdrawn from your account.",
    )
    return txn


@db_transaction.atomic
def transfer_money(
    sender,
    sender_account_id,
    receiver_account_number,
    amount,
    description="",
):
    amount = Decimal(amount)

    if amount <= 0:
        raise ValueError("Transfer amount must be greater than ₹0.")

    sender_account = _active_account_for_user(
        sender, sender_account_id
    )
    if not sender_account:
        raise ValueError("Sender account not found.")

    receiver_account = (
        BankAccount.objects.select_for_update()
        .select_related("user")
        .filter(
            account_number=receiver_account_number,
            status="ACTIVE",
        )
        .first()
    )
    if not receiver_account:
        raise ValueError("Receiver account not found.")

    if sender_account.id == receiver_account.id:
        raise ValueError("You cannot transfer money to your own account.")

    remaining = sender_account.balance - amount
    if remaining < sender_account.minimum_balance:
        raise ValueError(
            f"Transfer failed. You must maintain a minimum balance of "
            f"₹{sender_account.minimum_balance:.2f}."
        )

    sender_account.balance = remaining
    sender_account.save(update_fields=["balance", "updated_at"])

    receiver_account.balance += amount
    receiver_account.save(update_fields=["balance", "updated_at"])

    sender_txn = Transaction.objects.create(
        user=sender,
        account=sender_account,
        transaction_type="TRANSFER",
        amount=amount,
        description=description
        or f"Transfer to {receiver_account.account_number}",
        balance_after=sender_account.balance,
        status="SUCCESS",
    )

    Transaction.objects.create(
        user=receiver_account.user,
        account=receiver_account,
        transaction_type="RECEIVE",
        amount=amount,
        description=description
        or f"Received from {sender_account.account_number}",
        balance_after=receiver_account.balance,
        status="SUCCESS",
    )

    Notification.objects.create(
        user=sender,
        title="Transfer Successful",
        message=(
            f"₹{amount:.2f} transferred to "
            f"{receiver_account.account_number}."
        ),
    )

    Notification.objects.create(
        user=receiver_account.user,
        title="Money Received",
        message=(
            f"₹{amount:.2f} received from "
            f"{sender_account.account_number}."
        ),
    )

    return sender_txn


CARD_PAYMENT_LIMIT = Decimal("20000.00")
CARD_MAX_TRANSACTIONS_PER_DAY = 4


@db_transaction.atomic
def card_payment(user, card_id, amount, description=""):
    amount = Decimal(amount)
    if amount <= 0:
        raise ValueError("Card payment amount must be greater than ₹0.")
    if amount > CARD_PAYMENT_LIMIT:
        raise ValueError("Maximum card payment limit is ₹20,000 per transaction.")

    card = (
        Card.objects.select_for_update()
        .select_related("account")
        .filter(id=card_id, user=user, status="ACTIVE", account__status="ACTIVE")
        .first()
    )
    if not card:
        raise ValueError("Active card not found.")

    today = timezone.localdate()
    used_today = card.transactions.filter(
        transaction_type="CARD", status="SUCCESS", created_at__date=today
    ).count()
    if used_today >= min(card.max_transactions_per_day, CARD_MAX_TRANSACTIONS_PER_DAY):
        raise ValueError("Card transaction limit reached. Maximum 4 successful card transactions are allowed per day.")

    account = BankAccount.objects.select_for_update().get(pk=card.account_id)
    remaining = account.balance - amount
    if remaining < account.minimum_balance:
        raise ValueError(
            f"Payment failed. Minimum balance of ₹{account.minimum_balance:.2f} must be maintained."
        )

    account.balance = remaining
    account.save(update_fields=["balance", "updated_at"])

    txn = Transaction.objects.create(
        user=user, account=account, card=card, transaction_type="CARD",
        amount=amount, description=description or f"{card.get_card_type_display()} payment",
        balance_after=account.balance, status="SUCCESS",
    )
    Notification.objects.create(
        user=user, title="Card Payment Successful",
        message=f"₹{amount:.2f} paid using your {card.get_card_type_display()}. {used_today + 1}/4 card transactions used today.",
    )
    return txn
