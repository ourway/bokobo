from book_rate.models import Rate


def book_average_rate(book_id, db_session):
    res = db_session.query(Rate).filter(Rate.book_id == book_id).all()
    rate_no = len(res)
    rate_sum = 0.0
    for item in res:
        rate_sum += item.rate
    if rate_sum == 0.0:
        rate_average = 0
    else:
        rate_average = rate_sum/rate_no

    return {'rate_no': rate_no, 'rate_average': rate_average}

