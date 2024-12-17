from sqlalchemy.exc import IntegrityError
from app.logging_init import logger


from app.models import ProcessedTransaction


def add_transaction(session, transaction_id, status, amount):
    try:
        transaction = ProcessedTransaction(
            transaction_id=transaction_id,
            status=status,
            amount=amount,
        )
        session.add(transaction)
        session.commit()
    except IntegrityError as e:
        logger.error(f"Transaction {transaction_id} already exists: {e}")
        session.rollback()


def mark_email_sent(session, transaction_id):
    transaction = session.query(ProcessedTransaction).filter_by(transaction_id=transaction_id).first()
    if transaction:
        transaction.email_sent = True
        session.commit()
    else:
        logger.error(f"Transaction {transaction_id} was not found")

