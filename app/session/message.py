from datetime import datetime

START = "Olá, seja-bem vindo ao Saturn\n\nEste bot realiza trades automáticos utilizando a" \
        + " API do Foxbit. Para mais informações digite os seguintes comandos:\n" \
        + "/list para listar todos os comandos deste bot\n" \
        + "/help para mais informações sobre como o bot funciona\n" \
        + "/about para mais informações sobre o nosso repositório"

ACCOUNT_ALREADY_EXISTS = "Sua conta já existe.\nPara checar o status da sua conta, digite /profile"

ACCOUNT_CREATED = "Sua conta foi criada com sucesso. Para mais informações sobre o status da sua conta " \
                + "utilize o comando /profile"

UNAUTHORIZED = "Você não tem autorização para realizar esta operação ainda.\n" \
             + "Aguarde ativação da sua conta com /profile"

DEPOSIT_START = "Digite o valor depositado em BRL com um (.) separando as casas decimais.\n" \
              + "Lembre-se que este depósito precisará ser validado pelo sistema."

INVALID_DEPOSIT_AMOUNT = "O valor digitado não é valido. Tente novamente"

DEPOSIT_CREATED = "O Depósito foi criado e está aguardando aprovação."

ACCOUNT_NOT_FOUND = "Sua conta não existe.\nCrie uma digitando /register"

BALANCE_REBASED = "Seu saldo em BRL foi reposicionado!\n"

def error_template(error, func_name):
  msg = "Um erro ocorreu durante sua requisição. Por favor, contate o suporte.\n\n" \
      + f"METHOD\n {func_name}\n\n" \
      + f"DATETIME\n {datetime.now()}\n\n" \
      + f"BODY\n{error}"

  return msg

def error(message):
  msg = "Um erro ocorreu na sua operação. Contate o suporte!\n\n" \
      + f"{message}"
  
  return msg

def profile(username, active):
  msg = f"Username: {username}\n"
  if active:
    msg += "Status da conta: Ativa"
  else:
    msg += "Status da conta: Aguardando aprovação. Contate o suporte."

  return msg

def trading_info(
  btc_price, btc_high, btc_low,
  price_to_sell, price_to_buy, btc_balance,
  btc_cost, brl_balance, brl_cost, brl_current_balance,
  brl_desired_balance
):
  msg = "Trading\n\n"
  msg += "----------------\n"
  msg += f"Preço do Bitcoin:\n{btc_price} BRL\n\n"
  msg += f"Máxima:\n{btc_high} BRL\n\n"
  msg += f"Mínima:\n{btc_low} BRL\n\n"
  msg += "----------------\n"
  msg += f"Preço para venda:\n{price_to_sell} BRL\n\n"
  msg += f"Preço para compra:\n{price_to_buy} BRL\n\n"
  msg += "----------------\n"
  msg += f"Saldo atual(BTC):\n{btc_balance} BTC\n\n"
  msg += f"Custo atual(BTC):\n{btc_cost} BRL\n\n"
  msg += "----------------\n"
  msg += f"Saldo atual(BRL):\n{brl_balance} BRL\n\n"
  msg += f"Custo atual(BRL):\n{brl_cost} BTC\n\n"
  msg += "----------------\n"
  msg += f"Saldo aproximado(BRL):\n{brl_current_balance} BRL\n\n"
  msg += f"Saldo esperado(BRL):\n{brl_desired_balance} BRL\n"

  return msg
