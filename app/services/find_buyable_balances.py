from orm import Model

def find_buyable_balances(btc_price, minimum_btc_trading):
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
FROM holding                                        AS b
JOIN wallet                                         AS ts
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

  res = Model.manual(sql_query)

  holdings = []
  for r in res:
    holdings.append({
      'balance_id': r[0],
      'partial_amount': r[1],
      'partial_price': r[2],
      'user_id': r[3]
    })

  return holdings
