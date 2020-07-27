import os
import configparser
import sys
from random import sample
from typing import List
from imgurpython import ImgurClient
from datetime import date


# Typings
Memes = List[str]
UsedMemes = List[str]

# Obtain the current directory for reference
script_path = os.path.dirname(os.path.realpath(__file__))
used_path = os.path.join(script_path, "data", "used.txt")


def get_used_memes() -> UsedMemes:
    """
    Gets a list of memes which were already used.
    Extracts a list from a flat file, one meme per line.
    """

    lines = []
    with open(used_path) as f:
        lines = [line.rstrip() for line in f]
    return lines


def updated_used_memes(memes: Memes) -> None:
    """
    Updates the used memes list.
    """

    with open(used_path, 'a') as f:
        f.write("\n".join(memes))


def is_eligable_meme(dir: str, meme: str, used_memes: UsedMemes) -> bool:
    """
    Check if meme is eligable to be included.
    Must be a file, and must not have been used before.
    """

    if not os.path.isfile(os.path.join(dir, meme)):
        # Not a file, skip
        return False

    if meme in used_memes:
        # Used already, skip
        return False
    return True


def get_random_memes(dir: str, limit: int, used_memes: UsedMemes = []) -> Memes:
    """
    Get (limit) number of memes which have no been used yet.
    """

    memes = [f for f in os.listdir(dir) if is_eligable_meme(dir, f, used_memes)]
    return sample(memes, limit)


def setup_imgur(config: configparser) -> ImgurClient:
    """
    Setups Imgur and logs in the user.
    """

    imgur = client = ImgurClient(
        client_id=config.get("daily-memes", "imgur_client_id"),
        client_secret=config.get("daily-memes", "imgur_client_secret")
    )
    imgur.set_user_auth(
        access_token=config.get("daily-memes", "imgur_access_token"),
        refresh_token=config.get("daily-memes", "imgur_refresh_token")
    )
    return imgur


def post_to_imgur(imgur: ImgurClient, config: configparser, dir: str, memes: Memes) -> str:
    """
    Uploads images and creates a public albumb of the memes.
    """

    # Upload images
    image_ids: List[str] = []
    for meme in memes:
        response = imgur.upload_from_path(
            path=os.path.join(dir, meme),
            config=None,
            anon=False
        )
        image_ids.append(response["id"])

    # Create album
    ymd = str(date.today())
    title = config.get("daily-memes", "imgur_album_title_prefix")
    desc = config.get("daily-memes", "imgur_album_desc")
    album = imgur.create_album({
        "title": f"{title} {ymd}",
        "desc": desc,
        "ids": ",".join(image_ids),
        "privacy": "public"
    })
    return album["id"]


if __name__ == "__main__":
    # Get config
    config = configparser.ConfigParser()
    config.read(os.path.join(script_path, "data", "config.ini"))

    # Setup Imgur client
    imgur = setup_imgur(config)

    # Get used memes
    used_memes = get_used_memes()

    # Get X random memes
    memes = get_random_memes(
        dir=config.get("daily-memes", "memes"),
        limit=int(config.get("daily-memes", "limit")),
        used_memes=used_memes
    )
    if len(memes) == 0:
        print("No more memes to upload")
        sys.exit()

    # Post to Imgur album
    try:
        album = post_to_imgur(
            config=config,
            imgur=imgur,
            dir=config.get("daily-memes", "memes"),
            memes=memes
        )
        print(f"https://imgur.com/a/{album}")

        # Update used memes
        updated_used_memes(memes)
    except Exception as e:
        print(e)
