APP_DATA_DB_NAME = "postgres"

LINKEDIN__STARTING_HOUR = 10

LINKEDIN__MAX_RESULTS_PER_SEARCH = 1600

LINKEDIN__BUILD_LEAD_REQUESTS_AMOUNT = 20

# this query needs: select accounts.id, accounts.name from ...
FORMATS__SIMPLE_SEARCH_STRATEGY_GET_ACCOUNTS_QUERY = '''select id,name from accounts
                                                         where id not in (select account_fk from rocketreach)
                                                         order by employee_count_range desc nulls last,
                                                                  case when id in (select account_fk from leads) then 1
                                                                  else 0 end desc limit 10'''

ADDRESSING__SECONDS_OF_SLEEP_BETWEEN_GENERATIONS = 3600*24

VALIDATION__MILLIONVERIFIER_API_KEY = "FXKyAAHwqR7iP5NEJJw66gqId"

SENDING__NUMBER_OF_NOT_SENT_MESSAGES_FETCHED_PER_DB_QUERY = 10

SENDING__DELTA_TIME_BETWEEN_MESSAGES_FOR_SAME_RECIPIENT_IP = 20

SENDING__MAX_MESSAGES_FOR_SAME_RECIPIENT_BY_SAME_SENDER_PER_HOUR = 3
