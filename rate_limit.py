from ratelimit import limits, sleep_and_retry
import requests

TWO_MINUTES = 120
#rate limit is 240 every two minutes

@sleep_and_retry
@limits(calls=220, period=TWO_MINUTES)
def get_rate_limited(url):
    response = requests.get(url)
    return response