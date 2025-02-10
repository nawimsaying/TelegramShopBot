from yoomoney import Quickpay
import controller_db as db
import random

def create_transaction(sum_of_deposit, user_id):
    label_operation = get_label(user_id)
    # Здесь в receiver указывать номер своей карты YooMoney, на которую должна приходить оплата
    quickpay = Quickpay(
        receiver="",
        quickpay_form="shop",
        targets="Deposit",
        paymentType="SB",
        sum=sum_of_deposit,
        label=label_operation
    )

    return quickpay.base_url, quickpay.label

def get_label(user_id):
    status = False
    while status == False:
        order_label = str(random.randint(0, 9999999))
        status = db.check_order_label(order_label)
        if status != False:
            return order_label