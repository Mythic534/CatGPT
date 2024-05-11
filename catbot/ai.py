from io import BytesIO
import logging
from openai import OpenAI



class Catifier:
    """
    ChatGPT cat interface class
    """
    def __init__(self, config: dict):
        """
        Initializes the chatGPT interface
        :param config: dict containing key value pairs of configuration variables
        """
        self.config = config
        self.client = OpenAI(
            api_key=config["OPENAI_API_KEY"]
        )
        self.model = config["GPT_MODEL"]
        # system message setting the global behavior of the model
        self.cat_config = {
            "role": "system",
            "content": "You mimick a cat and try to rephrase everything using cat-related analogies and puns",
        }

    async def catify(self, message: str) -> str:
        """
        Command to turn the incoming message into a "catified" version of itself
        :param message: The incoming message
        :return: A catified version of the incoming message
        """
        logging.info(f"catify was called with {message}")
        
        # Remove '/catify' from the message
        message_parts = message.split(' ', 1)
        if len(message_parts) > 1:
            message = message_parts[1]
        else:
            message = ""  # If message has only '/catify', set it to empty string
        
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                self.cat_config,
                {
                    "role": "user",
                    "content": "Please turn the following text into a cat text.",
                },
                {"role": "user", "content": message},
            ],
        )
        answer = completion.choices[0].message.content
        logging.info(f"catify is returning {answer}")
        return answer

    async def reply(self, message: str) -> str:
        """
        Method to interface with ChatGPT. Get's a response from the model and turns it into cat style
        :param message: The incoming message
        :return: The reply from ChatGPT,
        """
        logging.info(f"reply was called with {message}")
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[self.cat_config, {"role": "user", "content": message}],
        )
        answer = completion.choices[0].message.content
        logging.info(f"reply is returning {answer}")
        return answer

    async def transcribe(self, audio_file: BytesIO) -> str:
        """
        Creates a transcript of an audio file (e.g. a voice message) using whisper.
        Turns the transcript into a catfied version.
        :param audio_file: Input audio file, e.g. open("audio.mp3," "rb")
        :return: Catified transcript of the audio file
        """
        transcript = (await self.client.Transcription.create("whisper-1", audio_file))["text"]
        cat_transcript = await self.catify(transcript)
        return cat_transcript

    async def generate_image(self, prompt: str, size: str) -> str:
        logging.info(f"Generate image was called with {prompt=}")
        response = await self.client.Image.create(
            prompt=prompt,
            n=1,
            size=size
        )
        image_url = response['data'][0]['url']
        logging.info(f"Generate image URL: {image_url}")
        return image_url
