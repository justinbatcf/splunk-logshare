[cloudflare://<name>]

zone_name = <value>
auth_email = <value>
auth_key = <value>
last_ray_id = <value>

*in seconds
request_timeout= <value>

* time to wait for reconnect after timeout or error
backoff_time = <value>

* in seconds or a cron syntax
polling_interval= <value>

* whether multiple requests spawned by tokenization are run in parallel or sequentially. Defaults to false (0)
sequential_mode= <value>

* an optional stagger time period between sequential requests.Defaults to 0
sequential_stagger_time= <value>
