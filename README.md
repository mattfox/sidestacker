# Side-Stacker

[Requirements](https://docs.monadical.com/s/monadical-study-guide#Difficulty-Advanced-senior-full-stack-applicants)

## Setup

Make a virtualenv and install requirements.

```
git clone git@github.com:mattfox/sidestacker.git
cd sidestacker
./setup-dev.sh
```

Make life easier with an `.envrc` file. Call `source .envrc` or better yet, have [Direnv](https://direnv.net/docs/installation.html) do it for you.

```
cat > .envrc << EOF
source venv/bin/activate
EOF
```

Make a database and run migrations.

```
python manage.py migrate
```

## Operation

To run the servers:

```
python manage.py runserver
# sanic
```


## The Plan

Matt's notes on how to write this.

1. ✓ Django project basics (virtualenv, can fetch page from runserver)
1. ✓ Game model stubs
1. ✓ Game model tests (new moves, game completion cases)
1. ✓ Implement game model methods (make test pass)
1. Simple URLs, views, templates (associate session with game, match making, only initial state supported)
1. Support whole game lifecycle (waiting for match, taking turns, completion)
1. Javascript, websockets, Sanic (update game view without refresh; page refresh reloads game state)
