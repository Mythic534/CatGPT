# CatGPT Telegram Bot
A not particulary useful, but funny Telegram bot using the offical [ChatGPT API](https://platform.openai.com/docs/guides/chat) and [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot).
You can talk to it just like the normal API, but it will throw in cat puns and feline jokes.
### Prerequisites
- python installed on your system
- A telegram bot and an authentication token ([official instructions](https://core.telegram.org/bots/features#BotFather)) 
- An OpenAI API key ([instructions](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key))

### Usage
Copy the file `.env_template` to `.env`.
Add your telegram bot token and the OpenAI API access token to the `.env` file.
- Run `pip install pipenv --user`
- Run `pipenv shell`
- Run `python main.py`
