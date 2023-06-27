import snowflake.client

snowflake.client.setup('127.0.0.1', 8910)
for i in range(10):
    print(snowflake.client.get_guid())

