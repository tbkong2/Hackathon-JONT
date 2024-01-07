#imports the all the necessary modules
import os
import discord
import requests
import json
import openai
import string

client = discord.Client(intents=discord.Intents.all())
# discord token
my_secret = os.environ['TOKEN']

# Openai credentials
openai.api_key = "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"


# Discord chat filter
def filter(inputtext):

  # through use of openai api, we can flag and categroize the input text
  response = openai.Moderation.create(inputtext)
  flagged = response['results'][0]['flagged']
  categories = response['results'][0]['categories']
  category_scores = response['results'][0]['category_scores']
  pist = ''
  # if flagged is true, we return the category
  for i in categories:
    if categories[i] == True:
      pist = pist + i + ", "
  pist = pist[:-2]
  # when not flagged, but includes swear words
  if pist == '':
    bad_words = ['fuck', 'shit']
    for words in inputtext.translate(str.maketrans(
        '', '', string.punctuation)).split():
      if words.lower() in bad_words:
        pist = "The above comment may contain: " + 'flagged word'
        return pist
    return False

  pist = "The above comment may contain: " + pist
  return pist


#Uses propmpt engineering to detect misinformation in an input text
def misinfo(text):
  y = "You are a lie detector. Using only a scale from 0 to 1 where 1 is closer to false and 0 is closer to true, print a single decimal to represent the following statement:" + text
  completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                            messages=[{
                                                "role": "user",
                                                "content": y
                                            }])
  return float(completion.choices[0].message.content)


@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))


#intalizes the accuacy and method
method = 'spoil'
accuracy = .7


@client.event
async def on_message(message):

  global method
  global accuracy

  #checks for the method command
  if message.content.startswith('!method'):

    if len(message.content.split()) == 1:

      await message.channel.send(f"Method is {method}")

    elif message.content.split()[1] == "delete":

      method = "delete"
      await message.channel.send("Method changed to " + method)

    elif message.content.split()[1] == "spoil":

      method = "spoil"
      await message.channel.send("Method changed to " + method)

    else:

      await message.channel.send("Invalid method")

  #checks for the accuracy command
  elif message.content.startswith('!accuracy'):

    if len(message.content.split()) == 1:

      await message.channel.send(f"Accuracy is {accuracy}")

    if float(message.content.split()[1]) >= 0 and float(
        message.content.split()[1]) <= 1:

      accuracy = message.content.split()[1]
      await message.channel.send("Accuracy changed to " + accuracy)

    else:

      await message.channel.send("Accuracy can only be between 0 and 1")
  #Implements the method of spoil and delete. If the method is spoil, it will replace the text with a discord spoil cover. If the method is delete, it will delete the the message.
  
  elif filter(message.content) != False and str(message.author) != "HACKATHON#2253":

    user = str(message.author)
    text = str(message.content)

    await message.delete()

    if method == "spoil":
      await message.channel.send(f"The user {user} sent ||{text}||")
      await message.channel.send(filter(message.content))

  elif float(misinfo(message.content)) >= float(accuracy) and str(message.author) != "HACKATHON#2253":
    
    await message.channel.send("The above statement may contain some incorrect information")


client.run(my_secret)
