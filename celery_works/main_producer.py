
from celery_works.celery_consumers import generate_book_content
from celery.result import AsyncResult



def generate_book( data):
    result = generate_book_content.apply_async(args=[data],
                                  routing_key='book_generate')
    print(result.task_id)
    # result.get()
    return {'inquiry_id':result.task_id}

def check_status(id):
    result = AsyncResult(id)
    return {'inquiry_result':result.status}


