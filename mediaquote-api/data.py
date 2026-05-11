"""Датасеты цитат из фильмов и игр"""
import csv
import json
import os

_BASE = os.path.dirname(os.path.abspath(__file__))


# Дополнительные цитаты с персонажами (не дублируют movie_quotes.txt)
_EXTRA_MOVIES = [
    {"quote": "I am your father.", "character": "Darth Vader", "movie": "Star Wars: The Empire Strikes Back", "year": 1980},
    {"quote": "There is no spoon.", "character": "Spoon Boy", "movie": "The Matrix", "year": 1999},
    {"quote": "I'm the king of the world!", "character": "Jack Dawson", "movie": "Titanic", "year": 1997},
    {"quote": "It's not who I am underneath, but what I do that defines me.", "character": "Bruce Wayne", "movie": "Batman Begins", "year": 2005},
    {"quote": "Get busy living, or get busy dying.", "character": "Andy Dufresne", "movie": "The Shawshank Redemption", "year": 1994},
    {"quote": "Hope is a good thing, maybe the best of things.", "character": "Andy Dufresne", "movie": "The Shawshank Redemption", "year": 1994},
    {"quote": "Life is like a box of chocolates.", "character": "Forrest Gump", "movie": "Forrest Gump", "year": 1994},
    {"quote": "I'm gonna make him an offer he can't refuse.", "character": "Vito Corleone", "movie": "The Godfather", "year": 1972},
    {"quote": "I am inevitable.", "character": "Thanos", "movie": "Avengers: Endgame", "year": 2019},
    {"quote": "Remember who you are.", "character": "Mufasa", "movie": "The Lion King", "year": 1994},
    {"quote": "My precious.", "character": "Gollum", "movie": "The Lord of the Rings: The Two Towers", "year": 2002},
    {"quote": "We're not in Kansas anymore.", "character": "Dorothy", "movie": "The Wizard of Oz", "year": 1939},
    {"quote": "Why so serious? Let's put a smile on that face!", "character": "Joker", "movie": "The Dark Knight", "year": 2008},
    {"quote": "Get to the chopper!", "character": "Dutch", "movie": "Predator", "year": 1987},
    {"quote": "I feel the need — the need for speed!", "character": "Maverick", "movie": "Top Gun", "year": 1986},
    {"quote": "Bond. James Bond.", "character": "James Bond", "movie": "Dr. No", "year": 1962},
    {"quote": "I volunteer as tribute.", "character": "Katniss Everdeen", "movie": "The Hunger Games", "year": 2012},
    {"quote": "Whatever it takes.", "character": "Tony Stark", "movie": "Avengers: Endgame", "year": 2019},
    {"quote": "We are Groot.", "character": "Groot", "movie": "Guardians of the Galaxy", "year": 2014},
    {"quote": "You can't stop what's coming.", "character": "Anton Chigurh", "movie": "No Country for Old Men", "year": 2007},
    {"quote": "You is kind, you is smart, you is important.", "character": "Aibileen Clark", "movie": "The Help", "year": 2011},
]


_MOVIE_CHARACTERS = {
    "do, or do not. there is no try": "Yoda",
    "here's looking at you, kid": "Rick Blaine",
    "frankly, my dear, i don't give a damn": "Rhett Butler",
    "you're gonna need a bigger boat": "Chief Brody",
    "here's johnny": "Jack Torrance",
    "i'll be back": "Terminator",
    "hasta la vista, baby": "Terminator",
    "you talking to me": "Travis Bickle",
    "may the force be with you": "Han Solo",
    "luke, i am your father": "Darth Vader",
    "i am your father": "Darth Vader",
    "to infinity and beyond": "Buzz Lightyear",
    "just keep swimming": "Dory",
    "why so serious": "Joker",
    "you can't handle the truth": "Col. Jessup",
    "i see dead people": "Cole Sear",
    "keep your friends close, but your enemies closer": "Michael Corleone",
    "i'm gonna make him an offer he can't refuse": "Vito Corleone",
    "i'm going to make him an offer he can't refuse": "Vito Corleone",
    "drop the gun, take the cannoli": "Peter Clemenza",
    "run, forrest, run": "Jenny",
    "life is like a box of chocolates": "Forrest Gump",
    "mama always said life was like a box of chocolates": "Forrest Gump",
    "houston, we have a problem": "Jim Lovell",
    "you shall not pass": "Gandalf",
    "my precious": "Gollum",
    "one ring to rule them all": "Gandalf",
    "there's some good in this world": "Samwise Gamgee",
    "you're a wizard, harry": "Rubeus Hagrid",
    "after all, tomorrow is another day": "Scarlett O'Hara",
    "go ahead, make my day": "Harry Callahan",
    "say hello to my little friend": "Tony Montana",
    "yippie-ki-yay": "John McClane",
    "i know kung fu": "Neo",
    "what we've got here is a failure to communicate": "Captain",
    "carpe diem. seize the day, boys": "John Keating",
    "hello. my name is inigo montoya": "Inigo Montoya",
    "greed, for lack of a better word, is good": "Gordon Gekko",
    "are you not entertained": "Maximus",
    "my name is maximus decimus meridius": "Maximus",
    "show me the money": "Rod Tidwell",
    "you had me at hello": "Dorothy Boyd",
    "i'm king of the world": "Jack Dawson",
    "what's in the box": "Detective Mills",
    "the greatest trick the devil ever pulled": "Verbal Kint",
    "i'm not bad. i'm just drawn that way": "Jessica Rabbit",
    "i'll have what she's having": "Customer",
    "every man dies; not every man really lives": "William Wallace",
    "they may take our lives, but they'll never take our freedom": "William Wallace",
    "i am groot": "Groot",
    "we are groot": "Groot",
    "i am iron man": "Tony Stark",
    "i am inevitable": "Thanos",
    "whatever it takes": "Tony Stark",
    "with great power comes great responsibility": "Uncle Ben",
    "why do we fall": "Alfred",
    "it's not who i am underneath": "Bruce Wayne",
    "some men just want to watch the world burn": "Alfred",
    "you either die a hero": "Harvey Dent",
    "if you're good at something, never do it for free": "Joker",
    "let's put a smile on that face": "Joker",
    "a martini. shaken, not stirred": "James Bond",
    "bond. james bond": "James Bond",
    "my name is bond, james bond": "James Bond",
    "exercise gives you endorphins": "Elle Woods",
    "just when i thought i was out": "Michael Corleone",
    "you is kind. you is smart. you is important": "Aibileen Clark",
    "i don't want to survive. i want to live": "Solomon Northup",
    "we accept the love we think we deserve": "Charlie",
    "not quite my tempo": "Fletcher",
    "there are no two words in the english language more harmful than good job": "Fletcher",
    "happiness is only real when shared": "Chris McCandless",
    "i read somewhere... how important it is in life": "Chris McCandless",
    "adventure is out there": "Ellie Fredricksen",
    "dreams feel real while we're in them": "Cobb",
    "an idea is like a virus": "Cobb",
    "do not go gentle into that good night": "Brand",
    "we used to look up at the sky": "Cooper",
    "people keep asking if i'm back": "John Wick",
    "that's my secret, captain. i'm always angry": "Bruce Banner",
    "genius, billionaire, playboy, philanthropist": "Tony Stark",
}


def _load_movies():
    result = []
    path = os.path.join(_BASE, "movie_quotes.txt")
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = None
            try:
                y = int(row.get("year", 0))
                year = y if y > 1800 else None
            except (ValueError, TypeError):
                pass
            quote = row["quote"].strip().strip('"')
            # ищем персонажа по первым словам цитаты
            character = "Unknown"
            quote_lower = quote.lower()
            for key, char in _MOVIE_CHARACTERS.items():
                if quote_lower.startswith(key) or key in quote_lower:
                    character = char
                    break
            result.append({
                "quote": quote,
                "character": character,
                "movie": row["movie"].strip().strip('"'),
                "year": year,
            })

    existing = {q["quote"].lower() for q in result}
    for q in _EXTRA_MOVIES:
        if q["quote"].lower() not in existing:
            result.append(q)

    for i, q in enumerate(result, start=1):
        q["id"] = i

    return result


def _load_games():
    result = []
    path = os.path.join(_BASE, "db.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for i, item in enumerate(data["quotes"], start=1):
        result.append({
            "id": i,
            "quote": item["quote"].strip(),
            "character": item.get("character", "Unknown"),
            "game": item["game"].strip(),
            "year": None,
        })
    return result


MOVIE_DATASET = _load_movies()
GAME_DATASET = _load_games()