from yoomoney import Client

def get_operation_status(order_label):
    # Менять token на свой здесь
    token = ""
    client = Client(token)
    history = client.operation_history()
    for operation in history.operations:
        if operation.label == order_label:
            if operation.status == 'success':
                return 0
    return 1

def get_operation_amount(order_label):
    # Менять token на свой здесь
    token = ""
    client = Client(token)
    history = client.operation_history()
    for operation in history.operations:
        if operation.label == order_label:
            if operation.status == 'success':
                return operation.amount
    return 1