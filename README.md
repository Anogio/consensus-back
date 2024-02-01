## Install the dependencies
```
make install
```

## Run the app
```
make run
```

## Deployment

The app is deployed on fly.io

After configuring the project, deploy with
```
flyctl deploy
```

It will be made available at `https://consensus-back.fly.dev/` 
and `https://api.consensus.anog.fr`

## TODO

- Stop using player names as keys, to allow
users with the same name without collision. Use uuids instead.
- Use a session cookie to store the player name.
This would prevent multi-tabbing (make cheating the ballot harder) 
and make it more convenient
- Store the state in DB to avoid having to clean up, facilitate inspection
and avoid concurrency issues (however, there should be no concurrent writes
in the state in practice as the round is only updated by the loop, and the
guesses are specific to each user)
- Clean up the messaging interface. For now the events are defined
both in `app` and `game_runner` and are untyped