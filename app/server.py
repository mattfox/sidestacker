from sanic import Sanic
import environ
from asyncpg import create_pool
from game.blueprint import game_blueprint

app = Sanic("SideStacker")
env = environ.Env()

app.config.HTTP_URL = env.str('HTTP_URL', 'http://127.0.0.1:8000/')  # Where Sanic should connect to the HTTP server.
app.config.DATABASE_URL = env.str('DATABASE_URL')


app.blueprint(game_blueprint)
