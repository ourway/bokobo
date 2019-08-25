from prices.models import Price


def delete_book_price(book_id,db_session):
    price = db_session.query(Price).filter(Price.book_id==book_id).first()
    if price:
        db_session.delete(price)
    return True
