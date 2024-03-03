APP_DATA_DB_NAME = "postgres"

LINKEDIN__STARTING_HOUR = 0

LINKEDIN__MAX_RESULTS_PER_SEARCH = 1600

LINKEDIN__BUILD_LEAD_REQUESTS_AMOUNT = 1

LINKEDIN__LEAD_SEARCH_GET_REQUEST_QUERY = """select *
                                                from requests
                                                where type = true
                                                  and status = 0
                                                  and project =%s
                                                order by case
                                                             when data::text like '%"value": "I"%' then 0
                                                             when data::text like '%"value": "H"%' then 1
                                                             when data::text like '%"value": "G"%' then 2
                                                             when data::text like '%"value": "F"%' then 3
                                                             when data::text like '%"value": "E"%' then 4
                                                             when data::text like '%"value": "D"%' then 5
                                                             when data::text like '%"value": "C"%' then 6
                                                             when data::text like '%"value": "B"%' then 7
                                                             else 8
                                                             end,
                                                         start desc, id
                                                limit 1"""

# this query needs: select accounts.id, accounts.name from ...
FORMATS__SIMPLE_SEARCH_STRATEGY_GET_ACCOUNTS_QUERY = '''select id,name from accounts
                                                         where id not in (select account_fk from rocketreach)
                                                         order by employee_count_range desc nulls last,
                                                                  case when id in (select account_fk from leads) then 1
                                                                  else 0 end desc limit 10'''

ADDRESSING__SECONDS_OF_SLEEP_BETWEEN_GENERATIONS = 3600 * 24

VALIDATION__MILLIONVERIFIER_API_KEY = "FXKyAAHwqR7iP5NEJJw66gqId"

SENDING__NUMBER_OF_NOT_SENT_MESSAGES_FETCHED_PER_DB_QUERY = 10

SENDING__DELTA_TIME_BETWEEN_MESSAGES_FOR_SAME_RECIPIENT_IP = 20

SENDING__MAX_MESSAGES_FOR_SAME_RECIPIENT_BY_SAME_SENDER_PER_HOUR = 3
