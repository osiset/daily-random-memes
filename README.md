# Daily Memes

This is an automated Python script I use to grab X number of my thousands and thousands of memes, and generate a daily Imgur album with them. No meme is reused twice.

## Installation

`pip install -r requirements.txt`, recommended you do this inside a Python venv.

Python >= 3.6 required.

## Usage

1. Register an [Imgur application](https://api.imgur.com/oauth2/addclient)
2. Enter `Daily Memes` as title
3. Enter `http://localhost/` as redirect path
4. Go to `https://api.imgur.com/oauth2/authorize?client_id=CLIENT_ID&response_type=token`, replacing `CLIENT_ID` with your client ID
5. You will end up at `http://localhost/`, grab the `access_token` and `refresh_token`
6. Edit `data/config.sample.ini` to `data/config.ini` and open the file and fill in all values

`python main.py`

This will grab X random memes from your configured directory, create a public Imgur albums with today's date, and print out the URL to the album.
