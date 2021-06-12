import time

import aiohttp
import aiohttp_jinja2
import faust
import jinja2
from faust import web

# create an instance of Faust app
app = faust.App('myapp', broker='kafka://localhost')


# This will be our main event class, created when user buys subscription
class Subscription(faust.Record, serializer='json'):
    username: str
    timestamp: float
    authorized: bool

# Define some Kafka topic for your agent
subscription_topic = app.topic('subscriptions', value_type=Subscription)


@app.agent(subscription_topic)
async def post_to_slack(subscriptions):
    async for subscription in subscriptions:
        async with aiohttp.ClientSession() as session:
            print(f"making request for {subscription.username}")
            async with session.get('https://httpbin.org/delay/9') as res:
                response = await res.json()
                print(response)
                return response


@app.page("/")
class SubscriptionView(web.View):
    @aiohttp_jinja2.template('subscription.jinja2')
    async def get(self, request):
        return {"username": "pass"}

    async def post(self, request):
        post_data = await request.post()
        print(post_data)
        username = post_data['username']
        sub = Subscription(
            username=username,
            timestamp=time.time(),
            authorized=True
        )
        await post_to_slack.send(value=sub)
        return self.json({"thank you": "ok"})


@faust.App.on_configured.connect()
def configure(app, conf, **kwargs):
    print("configured")

# aiohttp app is available on app.web Faust app atribute
aiohttp_jinja2.setup(app.web.web_app, loader=jinja2.FileSystemLoader('jinja_templates'))
app.main()

