import random
import uuid
from datetime import datetime, timedelta
from string import ascii_lowercase
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel


class Game(BaseModel):
    id: str
    rate_limit: int
    attempts: int = 0
    last_attempt: datetime | None = None


class GameID(BaseModel):
    id: str


class Answer(BaseModel):
    game: Game
    correct: bool


class Item(BaseModel):
    id: str
    game_id: str
    answer: str


app = FastAPI()

# In-memory for now
games = {}


async def rate_limiter(request: Request):
    game_id = request.path_params["game_id"]
    game = games.get(game_id)

    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    now = datetime.now()
    if game.last_attempt is None:
        game.last_attempt = now

    window = game.last_attempt
    rate_limit_window = timedelta(seconds=60)
    since_window_start = now - window
    if since_window_start > rate_limit_window:
        # reset if window has expired
        game.attempts = 1
        game.last_attempt = now
    else:
        # if within the rate limit window
        if game.attempts >= game.rate_limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        game.attempts += 1

    return


@app.post("/start", response_model=GameID)
def start_game():
    game_id = str(uuid.uuid4())
    rate_limit = random.randint(1, 10)
    game = Game(id=game_id, rate_limit=rate_limit)
    response = GameID(id=game_id, rate_limit=rate_limit)
    games[game_id] = game
    return response


@app.get("/{game_id}/item/", response_model=Item, dependencies=[Depends(rate_limiter)])
def get_game_item(game_id: str):
    game = games.get(game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    item = Item(
        id=str(uuid.uuid4()),
        game_id=game.id,
        answer="".join(random.choice(ascii_lowercase) for _ in range(8)),
    )
    return item


@app.get("/{game_id}/solution/", response_model=Game)
def get_game_solution(game_id: str):
    game = games.get(game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    return Game(**game.dict())


@app.get("/{game_id}/guess/{limit_guess}", response_model=Answer)
def answer(game_id: str, limit_guess: int):
    game = games.get(game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    correct = limit_guess == game.rate_limit
    return Answer(game=game, correct=correct)
