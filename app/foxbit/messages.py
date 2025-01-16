def order_executed(side, quantity, price):
    formatted_value = "{:.8f}".format(quantity)
    pt_side = 'COMPRA' if side == 'BUY' else 'VENDA'

    msg = "Uma ordem foi criada!\n\n"
    msg += f"Tipo de ordem: {pt_side}\n"
    msg += f"Quantidade: {formatted_value} BTC\n"
    msg += f"Preço: {price} BRL"

    return msg

def order_cancelled(quantity, price, reason):
    formatted_value = "{:.8f}".format(quantity)
    txt = "Ordem Cancelada!\n\n"
    txt += f"Quantidade: {formatted_value}\n"
    txt += f"Preço: {price}\n"
    txt += f"Razão: {reason}\n"

    return txt

def order_filled(quantity, price):
    formatted_value = "{:.8f}".format(quantity)
    txt = "Ordem totalmente executada!\n\n"
    txt += f"Quantidade: {formatted_value}\n"
    txt += f"Preço: {price}\n"

    return txt

def order_partially_cancelled(quantity, executed, price, reason):
    formatted_value = "{:.8f}".format(quantity)
    txt = "Ordem parcialmente executada!\n\n"
    txt += f"Quantidade: {formatted_value}\n"
    txt += f"Executada: {executed}\n"
    txt += f"Preço: {price}\n"
    txt += f"Razão: {reason}\n"

    return txt

def lock_for_security(data, code):
    txt = "Suas operações estão bloqueadas!\n\n"
    txt += "Durante operações automáticas, um erro foi encontrado"
    txt += " ao tentar salvar uma ordem já executada pela foxbit.\n"
    txt += "Por motivos de segurança, as ordens de compra e venda automáticas"
    txt += " estão desativas para sua conta. Contate o suporte para investigação.\n\n"
    txt += "DATA\n----------------\n"
    txt += f"{data}\n\n"
    txt += "CODE\n----------------\n"
    txt += f"{code}\n\n"

    return txt
