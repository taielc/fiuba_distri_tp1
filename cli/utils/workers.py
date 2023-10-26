"""Workers configuration.

base_filter
    ┃
    ┃   # QUERY 1
    ┣━━ filter_by_stops ━━━━━━━━━━━━━━━━┓
    ┃       ┃                           ┃
    ┃       ┃   # QUERY 3               ┃
    ┃       ┗━━ aggregate_by_route      ┃
    ┃             ┃                     ┃
    ┃             ┗ fastest_by_route ━━━┫
    ┃                                   ┃
    ┃   # QUERY 2                       ┃
    ┣━━ dist_calculator ━━━━━━━━━━━━━━━━┫
    ┃                                   ┃
    ┃   # QUERY 4                       ┃
    ┣━━ general_avg_price               ┃
    ┃        ┃                          ┃
    ┗━━━━━━━━┻ filter_by_price          ┃
                ┃                       ┃
                ┗━ price_by_route ━━━━━━┫
                                        ┃
                                     RESULTS
"""

SINGLE_WORKERS = ["fastest_by_route", "price_by_route"]
NON_SINGLE_WORKERS = {
    # general
    "base_filter": 4,
    # QUERY 1 (& 3)
    "filter_by_stops": 2,
    # QUERY 2
    "dist_calculator": 2,
    # QUERY 3
    "aggregate_by_route": 2,
    # QUERY 4
    "general_avg_price": 2,
    "filter_by_price": 2,
}
