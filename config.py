APP_DATA_DB_NAME = "postgres"

LINKEDIN__MAX_RESULTS_PER_SEARCH = 1600

LINKEDIN__BUILD_LEAD_REQUESTS_AMOUNT = 20

# this query needs: select accounts.id, accounts.name from ...
FORMATS__SIMPLE_SEARCH_STRATEGY_GET_ACCOUNTS_QUERY='''select id,name from accounts
                                                         where id not in (select account_fk from rocketreach)
                                                         order by employee_count_range desc nulls last,
                                                                  case when id in (select account_fk from leads) then 1
                                                                  else 0 end desc limit 10'''

VALIDATION__MILLIONVERIFIER_API_KEY="FXKyAAHwqR7iP5NEJJw66gqId"

