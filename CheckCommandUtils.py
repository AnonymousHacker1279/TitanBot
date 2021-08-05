import json
from operator import mod

async def CheckCommandPerms(ctx):
	with open('nobot_users.json', 'r') as f:
		data = json.load(f)
		maxIndex = 0
		userIndex = None
		modifiedUserMention = str(ctx.message.author.mention)[ : 2] + "!" + str(ctx.message.author.mention)[2 : ]
		for i in data:
			maxIndex = maxIndex + 1
			if str(modifiedUserMention) in i['user']:
				userIndex = maxIndex
		if userIndex != None:
			return True
		else:
			return False

async def CheckNoUserPings(user: str):
	with open('noping_users.json', 'r') as f:
		data = json.load(f)
		maxIndex = 0
		userIndex = None
		modifiedUserMention = user.replace('!', '') 
		for i in data:
			maxIndex = maxIndex + 1
			if modifiedUserMention in i['user']:
				userIndex = maxIndex
		if userIndex != None:
			return False
		else:
			return True