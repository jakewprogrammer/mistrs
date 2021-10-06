import twitter
from dotenv import dotenv_values

def set_up_twitter_api():
  config = dotenv_values(".env")
  TWITTER_CONSUMER_API_KEY = config['CONSUMER_TWITTER_API_KEY']
  TWITTER_CONSUMER_API_KEY_SECRET = config['CONSUMER_TWITTER_API_KEY_SECRET']
  TWITTER_API_KEY = config['TWITTER_API_KEY']
  TWITTER_API_KEY_SECRET = config['TWITTER_API_KEY_SECRET']
  twitter_api = twitter.Api(consumer_key=TWITTER_CONSUMER_API_KEY,
                        consumer_secret=TWITTER_CONSUMER_API_KEY_SECRET,
                        access_token_key=TWITTER_API_KEY,
                        access_token_secret=TWITTER_API_KEY_SECRET)

  twitter_api.VerifyCredentials()
  return twitter_api