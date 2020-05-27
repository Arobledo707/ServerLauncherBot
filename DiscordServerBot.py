import discord
import subprocess
import asyncio
from discord.ext import commands
import json
import traceback
import logging
from enum import Enum
import time
import os
import random
import urllib.request


logging.basicConfig(filename='./console.txt', filemode='a+', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

version = '0.2'

token = None
server_id = None
command_prefix = []
command_roles = []
client = commands.Bot(command_prefix)
client.case_insensitive = True


console_log = 'console.txt'
config_file = 'config.json'
terraria_script_path = None
terraria_exit_path = None
ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')

class message_type(Enum):
    LOG = 0
    ERROR = 1
    WARNING = 2
    INFO = 3

error = '```excel\n'
warning = '```http\n'
log = '```Elm\n'

end_code_block = '```'

#------------------------------------------------------check_config_file----------------------------------------------------------
def check_config_file():
    """Checks if config file exists if not it creates one"""
    if not os.path.exists(config_file):
        create_json_config_file()
    parse_json_config()


#-----------------------------------------------------parse_json_config
def parse_json_config():
    try:
        with open(config_file) as file:
            data = json.load(file)
            global token
            token = data['token']
            global terraria_script_path
            terraria_script_path = data['terrariastart']
            global terraria_exit_path
            terraria_exit_path = data['terrariaexit']
            for role in data['roles']:
                global command_roles
                if role not in command_roles:
                    command_roles.append(role)
                    print_and_log(message_type.INFO, 'Adding ' + role + ' to command roles')
                else:
                    print_and_log(message_type.INFO, role + ' was already in command roles!')
            for prefix in data['prefixes']:
                global command_prefix
                if prefix not in command_prefix:
                    command_prefix.append(prefix)
                    print_and_log(message_type.INFO, 'Adding ' + prefix + ' to bot prefixes')
                else:
                    print_and_log(message_type.INFO, prefix + ' is already a prefix!')
    except Exception as e:
        print_and_log(message_type.ERROR, e)
        print_and_log(message_type.INFO, 'Creating a new JSON file')
        create_json_config_file()



#------------------------------------------------------------add_to_json-------------------------------------------------------
def add_prefix_to_json(type, to_add):
    with open(config_file, "a") as file:
        data = json.load(file)
        data[type].append(to_add)
        json_data = json.dumps(data, indent = len(data))
        file.write(json_data)


#-------------------------------------------------------------remove_from_json-------------------------------------------------------
def remove_from_json(type, to_remove):
    with open(config_file, "w") as file:
        data = json.load(file)
        data[type].remove(to_remove)
        json_data = json.dumps(data, indent = len(data))
        file.write(json_data)


#----------------------------------------------check_if_roles_assigned----------------------------------------------------------------
def check_if_roles_assigned():
    global command_roles
    if len(command_roles) == 0:
        print_and_log(message_type.ERROR, 'No roles assigned. Either generate a new file or add\n"roles": ["FakeRole"] in config.json')


#--------------------------------------------------roles----------------------------------------------------------------------------
@client.command(name='Roles',
                description='Sends client the list of roles that the bot will take commands from.',
                brief='Sends client roles bot listens to',
                aliases=['roles'],
                pass_context=True)
async def roles(context):
    """Sends client each role in commandRoles"""
    if len(command_roles) == 0:
        await context.send(format_message(message_type.ERROR, 'Error: No roles have been added. Use AddRole to add a role.'))
        return
    async with context.typing():
        await context.send(format_message(message_type.LOG, 'These are the roles that the bot will take commands from:'))
        for role in command_roles:
            await context.send(format_message(message_type.LOG, role))
        await context.send(format_message(message_type.LOG, 'Done listing roles.'))

#--------------------------------------------------------create_json_config_file------------------------------------------------------
# Creates initial json config file for the bot
def create_json_config_file():
    file = open(config_file, 'w+')
    try:
        global token
        if token is None:
            token = "Enter Token Here"
        global terraria_script_path;
        if terraria_script_path is None:
            terraria_script_path = "Enter script path here"
        global terraria_exit_path;
        if terraria_exit_path is None:
            terraria_exit_path = "Enter script path here"
        file.write('''{
"token": "''' + token + '''",
"terrariastart": "''' + terraria_script_path + '''",
"terrariaexit": "''' + terraria_script_path + '''",
"prefixes": ["$"],
"roles": ["Admin"]
}''')
    except UnicodeEncodeError as e:
        print_and_log(message_type.INFO, 'Failed to write JSON file')
        print_and_log(message_type.ERROR, e)
    file.close()


#----------------------------------------------------------prefixes---------------------------------------------------------------
@client.command(name='Prefixes',
                description='Lists the command prefixes that have been set',
                brief='Lists command prefixes',
                aliases=['prefixes', 'p'],
                pass_context=True)
async def prefixes(context):
    """Sends client all prefixes in command_prefix"""
    if command_prefix == 0:
        await context.send(format_message(message_type.ERROR, 'Error: no prefixes assigned. Either add a prefix in xml or delete config file and run again'))
        return
    await context.send(format_message(message_type.LOG, 'Here are all the command prefixes'))
    for prefix in command_prefix:
        await context.send(format_message(message_type.LOG, prefix))
    await context.send(format_message(message_type.LOG, 'Done!'))

#------------------------------------------------------add_role----------------------------------------------------------------------
@client.command(name='AddRole',
                description='Adds a server role that the bot will take commands from.',
                brief='Add a role that the bot will listen to.',
                aliases=['addrole'],
                pass_context=True)
async def add_role(context, role=None):
    """Adds a role to the list of roles the bot will listen to. Adds a new xml element for the role."""
    if role is None:
        await context.send(format_message(message_type.WARNING, 'Role not entered'))
        return
    async with context.typing():
        role = role.replace("'", '')
        server = client.get_guild(server_id)
        added_role = None
        for serv_role in server.roles:
            if role.lower() == serv_role.name.lower():
                added_role = serv_role.name
                break
        else:
            await context.send(format_message(message_type.WARNING, 'Server does not have this role'))
            return
        command_roles.append(added_role)
        add_to_json('role', added_role)
        await context.send(format_message(message_type.LOG, added_role + ' has been added'))

#----------------------------------------------------------remove_role---------------------------------------------------------------
@client.command(name='RemoveRole',
                description='Removes a server role that the bot takes commands from.',
                brief='Remove a role that the bot listens to',
                aliases=['removerole'],
                pass_context=True)
async def remove_role(context, role=None):
    """Removes specified role from list of roles the bot listens to and removes it from the xml config file."""
    if role == None:
        await context.send(format_message(message_type.WARNING, 'Role not entered'))
    role = role.replace("'", '')
    remove_role = None
    for serv_role in command_roles:
        if serv_role.lower() == role:
            remove_role = serv_role
            break
    else:
        await context.send(format_message(message_type.WARNING, 'Role was not in Command Roles'))
        return
    if len(command_roles) == 1:
        await context.send(format_message(message_type.WARNING, 'Only one Role can give the bot commands. Add another role to be able to remove this one.'))
        return
    command_roles.remove(serv_role)
    #LogCommand(context.message)
    remove_from_json('role', serv_role)
    await context.send(format_message(message_type.LOG, serv_role + ' has been removed'))

#---------------------------------------------------get_ip-----------------------------------------------------------------------------
@client.command(name='ip',
                description="Get's ip",
                brief='pubic ip',
                pass_context=True)
async def get_ip(context):
    await context.send(format_message(message_type.LOG, ip))

#-----------------------------------------------start_terraria_server-----------------------------------------------------------------
@client.command(name='StartTerrariaServer',
                description='Starts terraria server if it is not running',
                brief='Starts terraria server',
                aliases=['st', 'terraria'],
                pass_context=True)
async def start_terraria_server(context):
    if terraria_script_path is None or terraria_script_path is 'Enter script path here':
        await context.send(format_message(message_type.ERROR, 'Script path not entered!'))
    await context.send(format_message(message_type.LOG, 'Starting Terraria Server!'))
    subprocess.call(terraria_script_path, shell=True)

#-----------------------------------------------exit_terraria_server-----------------------------------------------------------------
@client.command(name='ExitTerrariaServer',
                description='Exits terraria server ',
                brief='exits terraria server',
                aliases=['exitterraria', 'ExitTerraria', 'QuitTerraria', 'quitterraria', 'et'],
                pass_context=True)
async def exit_terraria_server(context):
    if terraria_exit_path is None or terraria_exit_path is 'Enter script path here':
        await context.send(format_message(message_type.ERROR, 'Script path not entered!'))
    await context.send(format_message(message_type.LOG, 'Exiting Terraria Server!'))
    subprocess.call(terraria_exit_path, shell=True)



#-----------------------------------------------------get_version----------------------------------------------------------------------
@client.command(name='GetVersion',
                description='Sends client version of the bot',
                brief='Version number',
                aliases=['Version', 'v'],
                pass_context=True)
async def get_version(context):
    """sends user bot's version number"""
    async with context.typing():
        await context.send(format_message(message_type.LOG,'Version: ' + version))


#------------------------------------------------coin_flip--------------------------------------------------------------------------
@client.command(name='CoinFlip',
                description='random 0-1 then prints heads or tails',
                brief='coin flip',
                aliases=['cf', 'Coin', 'coinflip'],
                pass_context=True)
async def coin_flip(context):
    """random 0-1 and sends results"""
    async with context.typing():
        result = random.randint(0,1)
        coin_result = 'Heads'
        if result is 0:
            coin_result = 'Tails'
        await context.send(format_message(message_type.LOG, coin_result))

#------------------------------------------------------format_message---------------------------------------------------------------
def format_message(message_type, message):
    """Formats a message by adding a color and making them into a code block in discord"""
    formatted_message = None
    if message_type == message_type.ERROR:
        formatted_message = error + message
    elif message_type == message_type.LOG:
        formatted_message = log + message
    elif message_type == message_type.WARNING:
        formatted_message = warnining + message
    formatted_message += end_code_block
    return formatted_message


#---------------------------------------------------------print_and_log---------------------------------------------------------------
def print_and_log(message_type, string):
    """prints string to console and writes string to log file"""
    print(string)
    if message_type == message_type.INFO:
        logging.info(string, exc_info=True)
    elif message_type == message_type.WARNING:
        logging.warning(string, exc_info=True)
    elif message_type == message_type.ERROR:
        logging.error(string, exc_info=True)
    else:
        logging.log(string, exc_info=True)

#-------------------------------------------------------on_ready------------------------------------------------------------------
@client.event
async def on_ready(message):
    """This is called when the bot comes is ready"""
    if len(client.guilds) > 1:
        print_and_log(LogTypeWarning,'Connected to more than one server!')
    for server in client.guilds:
        print_and_log(message_type.INFO,'Connected to: ' + server.name)
        global server_id
        server_id = server.id
        break
    commands = client.commands
    print_and_log(message_type.INFO, 'Running version: ' + version)


#-------------------------------------------------------on_message------------------------------------------------------------------
@client.event
async def on_message():
    if message.author.bot == True:
        return
    for prefix in command_prefix:
        if message.content[0].lower() == prefix:
            break
    else:
        return
    global server_id
    this_server = client.get_guild(server_id)
    server_member = this_server.get_member(message.author.id)
    if server_member is None:
        return
    else:
        roles = server_member.roles
        bot_listens = False
        for role in command_roles:
            for r in roles:
                if role == r.name:
                    bot_listens = True
                    break
    if bot_listens:
        message.content = message.content.lower()
        message.author = server_member
        await client.process_commands(message)
        
    
#-------------------------------------------------run_client-----------------------------------------------------------------------
def run_client(client):
    """Try to run the bot and if it fails wait a minute and try again"""
    bot_loop = asyncio.get_event_loop()
    while True:
        try:
            #Check config file and apply settings
            check_config_file()
            check_if_roles_assigned()
            global token
            bot_loop.run_until_complete(client.start(token))
        except Exception as e:
            if e is not IOError:
                print_and_log(message_type.ERROR, e)
        print_and_log(message_type.INFO, 'Waiting 60 seconds then restarting')
        time.sleep(60)

print_and_log(message_type.INFO, "Discord Api Version: " + discord.__version__)
run_client(client)
