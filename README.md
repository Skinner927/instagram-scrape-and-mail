# Instagram Scrape and Mail

Script to scrape multiple instagram accounts and download new images. Those new 
 images can also optionally be emailed. 

This was specifically built to automatically update a Nixplay photo frame I 
 purchased, but feel free to extend it. This was originally part of a larger 
 application I was working on, but plans changed. Otherwise, I would have 
 extended [instagram-scraper](https://github.com/rarcega/instagram-scraper) of 
 which this is based on; maybe I will one day.

## Features

- Only downloads images it has not seen before
- May specify output directory (`working_dir`)
- Can email the new images
- Stores history in a SQLite database
- Works with cron out of the box
- How far to look in the past can be configured, kinda (`max_media_count`)

## Deploying

Create a virtual environment in `venv`, then:

- `source venv/bin/activate`
- `pip install -r requirements.txt`
- `cp config.example.json config.json`
- Edit config.json. More options are in `app/config.py`
- `python run.py`

There are also some flags to override `config.json`, see `python run.py --help`.

## Config
Config is configured via `config.json`. Copy `config.example.json` to start. 
You can view all the config options in `app/config.py`.

### account
The key `account` is for your Instagram account login details. This account will
 be used to scrape instagram. It's best you use a secondary account, but not 
 required.

### friends
`friends` is in limbo. I was going to implement a way to white/black list images 
 downloaded by tag, but never got around to it. So now `friends` is a dict, where 
 the value of each friend is an empty dict. 

### settings -> max_media_count
`max_media_count` specifies how many images to look through for each friend. 

If you set `max_media_count` to 10, and someone has posted 20 new images since 
 last run, you'll only get the newest 10. 

If you set `max_media_count` to 30, and someone has posted 20 new images since 
 last run, you will download the 20 images.

## License
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
 distribute this software, either in source code form or as a compiled
 binary, for any purpose, commercial or non-commercial, and by any
 means.

In jurisdictions that recognize copyright laws, the author or authors
 of this software dedicate any and all copyright interest in the
 software to the public domain. We make this dedication for the benefit
 of the public at large and to the detriment of our heirs and
 successors. We intend this dedication to be an overt act of
 relinquishment in perpetuity of all present and future rights to this
 software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
 OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 OTHER DEALINGS IN THE SOFTWARE.