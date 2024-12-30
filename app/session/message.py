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

# DEPRECATED
ASK_EMAIL = "Por favor, digite seu e-mail"

ASK_PASSWORD = "Por favor, digite sua senha (não esqueça de apagar a mensagem contendo a senha logo" \
               + " em seguida)"

INVALID_EMAIL_OR_PASSWORD = "Email ou senha inválidos. Digite /login para tentar logar novamente"

LOGGED = "Você foi logado com sucesso na API do Foxbit!"

ASK_HISTORY_LIMIT = "Digite o tamanho da janela (valor inteiro)"

INVALID_HISTORY_LIMIT = "Valor para tamanho da janela é inválido. Digite /trade_start para" \
                        + " tentar novamente"

ASK_VALLEY = "Digite o valor para o vale (de 0 a 1)"

INVALID_VALLEY = "Valor para o vale inválido. Digite /trade_start e tente novamente"

TRADE_CREATED = "Trade criada com sucesso! Em breve notificações do seu trade"

ASK_PROFIT = "Digite o valor para o lucro esperado (de 0 a 1)"

INVALID_PROFIT = "Valor para o lucro inválido. Digite /trade_start e tente novamente"

WARNING_NOT_LOGGED = "Você não está logado. Digite /login para logar"

WARNING_ALREADY_LOGGED = "Você já está logado."

def currency_buyed(price):
  msg = f"Moeda comprada por {price} reais. Aguardando momento para a venda."
  return msg

def currency_sold(buyed, sold):
  profit = sold - buyed
  percent = (sold/buyed - 1.0) * 100

  msg = f"Venda realizada!!!!!\n\n" \
        + f"Comprado por: R$ {buyed}\n" \
        + f"Vendido por: R$ {sold}\n" \
        + f"Lucro por: R$ {profit}\n" \
        + f"Percentual: {percent}%"

  return msg

def current_price(price):
  msg = f"O atual valor da moeda é de R$ {price}"
  return msg

def log_error(status, description, path, body):
  msg = f"Session Error: {status}.\nDescription: {description}\n" \
        + f"path: {path}\n" \
        + f"body: {body}\n\n" \
        + f"Devido a este erro sua sessão foi resetada, por favor " \
        + f"registre este erro no nosso repositório: https://github.com/kinhosz/Saturn/issues/new"

  return msg

def accountNotFound():
  msg = "Esta conta no telegram não existe no nosso banco de dados. Por favor, " \
      + "entre em contato conosco."
    
  return msg
