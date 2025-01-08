def order_executed(side, quantity, price):
    pt_side = 'COMPRA' if side == 'BUY' else 'VENDA'

    msg = "Uma ordem foi criada!\n\n"
    msg += f"Tipo de ordem: {pt_side}\n"
    msg += f"Quantidade: {quantity} BTC\n"
    msg += f"Preço: {price} BRL"

    return msg

def order_cancelled(quantity, price, reason):
    txt = "Ordem Cancelada!\n\n"
    txt += f"Quantidade: {quantity}\n"
    txt += f"Preço: {price}\n"
    txt += f"Razão: {reason}\n"

    return txt

def order_filled(quantity, price):
    txt = "Ordem totalmente executada!\n\n"
    txt += f"Quantidade: {quantity}\n"
    txt += f"Preço: {price}\n"

    return txt

def order_partially_cancelled(quantity, executed, price, reason):
    txt = "Ordem parcialmente executada!\n\n"
    txt += f"Quantidade: {quantity}\n"
    txt += f"Executada: {executed}\n"
    txt += f"Preço: {price}\n"
    txt += f"Razão: {reason}\n"

    return txt
