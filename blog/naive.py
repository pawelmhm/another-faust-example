# To run
# python blog/naive.py
# server will listen on localhost:8088
import aiohttp
import aiohttp_jinja2
import jinja2
from aiohttp import web


routes = web.RouteTableDef()


async def post_to_slack(username):
    async with aiohttp.ClientSession() as session:
        print(f"making request for {username}")
        # make request to httpbin endpoint that returns after 9 secs delay
        async with session.get('https://httpbin.org/delay/9') as res:
            return await res.json()


@routes.view("/")
class SubscriptionView(web.View):
    @aiohttp_jinja2.template('subscription.jinja2')
    async def get(self) -> web.StreamResponse:
        return {}

    async def post(self) -> web.StreamResponse:
        post_data = await self.request.post()
        username = post_data['username']
        await post_to_slack(username)
        return web.Response(text='thanks')


if __name__ == "__main__":
    app = web.Application()
    app.add_routes(routes)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('jinja_templates'))
    web.run_app(app)