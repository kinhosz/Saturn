from orm import Model

def find_sellable_balances(btc_price, minimum_btc_trading):
  sql_query = f"""
SELECT
    b.id                                            AS balance_id,
    GREATEST(
      b.amount * ts.allocation_percentage,
      {minimum_btc_trading}
    )                                               AS partial_amount,
    b.price * ts.allocation_percentage              AS partial_price,
    b.user_id                                       AS user_id
FROM balances                                       AS b
JOIN trading_settings                               AS ts
  ON ts.user_id = b.user_id
WHERE b.base_symbol                                 = 'BTC'
  AND b.quote_symbol                                = 'BRL'
  AND ts.lock_sell                                  = FALSE
  AND b.amount                                      > {minimum_btc_trading}
  AND (
    b.price / (
      CASE
        WHEN b.amount >= {minimum_btc_trading}
        THEN b.amount
        ELSE {minimum_btc_trading}
      END
    )
  ) * POWER(
        ts.percentage_to_sell,
        LEAST(
          ts.exchange_count,
          -1.0
        ) * (-1.0)
      )                                           < {btc_price}
  """

  res = Model.manual(sql_query)

  balances = []
  for r in res:
    balances.append({
      'balance_id': r[0],
      'partial_amount': r[1],
      'partial_price': r[2],
      'user_id': r[3]
    })

  return balances
