
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer


def create_chat_bot():
   chatbot = ChatBot('Chattering Bot')
   trainer = ChatterBotCorpusTrainer(chatbot)
   trainer.train('chatterbot.corpus.english')

   while True:
       try:
           bot_input = chatbot.get_response(input())
           print(bot_input)

       except (KeyboardInterrupt, EOFError, SystemExit):
           break


if __name__ == '__main__':
   create_chat_bot()
