def order_executed(side, quantity, price):
    pt_side = 'COMPRA' if side == 'BUY' else 'VENDA'

    msg = "Uma ordem foi criada!\n\n"
    msg += f"Tipo de ordem: {pt_side}\n"
    msg += f"Quantidade: {quantity} BTC\n"
    msg += f"Preço: {price} BRL"

    return msg
