# Side-Stacker

[Requirements](https://docs.monadical.com/s/monadical-study-guide#Difficulty-Advanced-senior-full-stack-applicants)

<img width="492" alt="sidestacker" src="https://github.com/mattfox/sidestacker/assets/783056/80687c59-6fd9-4210-ab81-d890039c2663">

This uses Django for the backend, [Sanic](https://sanic.dev/en/) for websockets, a little bit of Javascript and [HTMX](https://htmx.org/) for the frontend, and PostgreSQL for the database and async notifications (SQLite would work just fine for the database except the interprocess communication uses Postgres LISTEN/NOTIFY).

This is purposefully kept very simple- no Javascript build process and no static files to serve.

## Setup

Make a virtualenv and install requirements.

```
git clone git@github.com:mattfox/sidestacker.git
cd sidestacker
./setup-dev.sh
```

Make a PostgreSQL user and database.

```
createuser --pwprompt sidestacker  # Record the password
createdb --owner sidestacker sidestacker_db
```

Make life easier with an `.envrc` file. Call `source .envrc` or better yet, have [Direnv](https://direnv.net/docs/installation.html) do it for you.

```
cat > .envrc << EOF
source venv/bin/activate
export DATABASE_URL=postgres://sidestacker:password@127.0.0.1/sidestacker_db
export SECRET_KEY=something really random (like from https://duckduckgo.com/?t=h_&q=password+30+strong&ia=answer)
EOF
```

Create database tables.

```
cd app/
python manage.py migrate
```

## Operation

To run the servers:

```
cd app/
python manage.py runserver
sanic server --port 8001
```

## The Plan

Matt's notes on how to write this:

1. ✓ Django project basics (virtualenv, can fetch page from runserver)
1. ✓ Game model stubs
1. ✓ Game model tests (new moves, game completion cases)
1. ✓ Implement game model methods (make test pass)
1. ✓ Simple URLs, views, templates (associate session with game, match making, only initial state supported)
1. ✓ Support whole game lifecycle (waiting for match, taking turns, completion)
1. ✓ Consider design (layout, colours, mobile)
1. ✓ Javascript, websockets, Sanic, PostgreSQL notify (update game view without refresh; page refresh reloads game state)
