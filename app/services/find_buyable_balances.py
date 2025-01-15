from app.db import DatabaseClient

def find_buyable_balances(btc_price, minimum_btc_trading):
  client = DatabaseClient()

  minimum_brl_value = minimum_btc_trading * btc_price

  sql_query = f"""
SELECT
    b.id                                            AS balance_id,
    GREATEST(
      b.amount * ts.allocation_percentage,
      {minimum_brl_value}
    )                                               AS partial_amount,
    b.price * ts.allocation_percentage              AS partial_price,
    b.user_id                                       AS user_id
FROM balances                                       AS b
JOIN trading_settings                               AS ts
  ON ts.user_id = b.user_id
WHERE b.base_symbol                                 = 'BRL'
  AND b.quote_symbol                                = 'BTC'
  AND ts.lock_buy                                   = FALSE
  AND b.amount                                      > {minimum_brl_value}
  AND (
    b.amount / (
      CASE
        WHEN b.price >= {minimum_btc_trading}
        THEN b.price
        ELSE {minimum_btc_trading}
      END
    )
  ) * POWER(
        ts.percentage_to_buy,
        GREATEST(
          ts.exchange_count,
          1.0
        )
      )                                           > {btc_price}
  """

  res = client.manual(sql_query)

  balances = []
  for r in res:
    balances.append({
      'balance_id': r[0],
      'partial_amount': r[1],
      'partial_price': r[2],
      'user_id': r[3]
    })

  client.disconect()
  return balances
