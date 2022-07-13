"""
   ____  __  __       ____ _               _ _    
  / __ \|  \/  |_ __ / ___| |__   ___ _ __(_) | __
 / / _` | |\/| | '__| |   | '_ \ / _ \ '__| | |/ /
| | (_| | |  | | |  | |___| | | |  __/ |  | |   <
 \ \__,_|_|  |_|_|   \____|_| |_|\___|_|  |_|_|\_\ 
  \____/

"""

import logging
from pyrogram import Client, idle, filters
from pyrogram.handlers import MessageHandler, ChatMemberUpdatedHandler
from pyrogram.types import Message, ChatMemberUpdated
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, ChannelPrivate, PeerIdInvalid
from time import time
from string import ascii_lowercase, ascii_uppercase, digits
from random import sample
from json import load, dump
from os.path import exists

#----------------------------#

#Error Log

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level = logging.ERROR
)

logger = logging.getLogger(__name__)

#----------------------------#

config = load(open('config.json', 'r', encoding= "utf8"))
api_id = config['api_id']; api_hash = config['api_hash']
TOKEN = config['token']; PHONE = config['phone']
Owner = config['owner']

#----------------------------#

#Cli Account

cli = Client(
    "AntiTabar_Cli",
    api_id,
    api_hash,
    phone_number = PHONE
)

#Api Account

api = Client(
    "AntiTabar_Api",
    api_id,
    api_hash,
    bot_token = TOKEN
)

api.start() #Start Api Account
cli.start() #Start Cli Account

#----------------------------#

BOT = api.get_me() #Api Infoes
ACCOUNT = cli.get_me() #Cli Infoes

write_Settings = lambda obj: dump(obj, open('Settings.json' , 'w'), indent = 4)
read_Settings  = lambda: load(open('Settings.json', 'r',encoding='utf8'))

#----------------------------#

#Check Settings.json File Exist Or Not

if exists('Settings.json') == True:
    pass
else:
    with open('Settings.json', 'x') as File:
        write_Settings(
            {
                "Admin_Status": "Demote",
                "Lock_Channel": False,
                "Lock_Spam": False,
                "Spam_Max_Messages": 4,
                "Spam_Max_Seconds": 10,
                "Forbidden_words": {},
                "Channels": []
            }
        )

#----------------------------#

#Check If Cli Account Knows Bot Or Not

try:
    BOT.id
except PeerIdInvalid:
    cli.send_message(BOT.username, '/start')

#----------------------------#

#Get Settings

settings: dict = read_Settings()

Admin_Status: str = settings['Admin_Status']
Lock_Channel_Messages: bool = settings["Lock_Channel"]
Lock_Spams: bool = settings["Lock_Spam"]
Forbidden_words: dict = settings["Forbidden_words"]
Channels: list = settings['Channels']
Max_Messages: int = settings['Spam_Max_Messages']
Max_Seconds: int = settings['Spam_Max_Seconds']

Spams = {}

def R_R_S(): global settings; write_Settings(settings) ; settings = read_Settings()

#----------------------------#

#Manage Channel Class

class ManageChannel:

    def __init__(self):
        pass

    async def Get_Admins(self, chat_id):
        Admins = await cli.get_chat_members(chat_id, filter='administrators')
        for i in Admins:
            if i.status == 'creator': Admins.remove(i)
            if i.user.id == BOT.id: Admins.remove(i)
        return Admins

    async def Get_Admins_Chat_ID(self, chat_id):
        Admins = await cli.get_chat_members(chat_id, filter='administrators')
        Chat_IDS = list()
        for i in Admins:
            if i.status == 'creator': pass
            else: Chat_IDS.append(str(i.user.id))
        return Chat_IDS

    async def Get_Admins_Username(self, chat_id):
        Admins = await cli.get_chat_members(chat_id, filter='administrators')
        Chat_IDS = list()
        for i in Admins:
            if i.status == 'creator': pass
            else: Chat_IDS.append(str(i.user.username))
        return Chat_IDS
    
    async def Get_Admin_Permissions(self, chat_id, user_id):
        self.user_id = user_id
        Admin = await cli.get_chat_member(chat_id, self.user_id)
        return Admin

    async def Add_Admin_Cli(self, chat_id, user_id):
        try:
            await cli.promote_chat_member(
            chat_id,
            user_id,
            can_post_messages = True,
            can_invite_users=True)
            return True
        except Exception as e: return str(e)

    async def Demote_Admin_Cli(self, chat_id, user_id):
        try:
            await cli.promote_chat_member(
            chat_id,
            user_id,
            can_manage_chat = False)
            return True
        except Exception as e: return str(e)

    async def Change_Permissions(self, chat_id, user_id, permission: str, pers):
        Change_Permissions_To = {
            True: False,
            False: True}
        try:
            await cli.promote_chat_member(
            chat_id = chat_id,
            user_id = user_id,
            can_change_info = Change_Permissions_To[pers.can_change_info] if permission == "can_change_info" else pers.can_change_info,
            can_post_messages = Change_Permissions_To[pers.can_post_messages] if permission == "can_post_messages" else pers.can_post_messages,
            can_edit_messages = Change_Permissions_To[pers.can_edit_messages] if permission == "can_edit_messages" else pers.can_edit_messages,
            can_delete_messages = Change_Permissions_To[pers.can_delete_messages] if permission == "can_delete_messages" else pers.can_delete_messages,
            can_invite_users = Change_Permissions_To[pers.can_invite_users] if permission == "can_invite_users" else pers.can_invite_users,
            can_manage_voice_chats = Change_Permissions_To[pers.can_manage_voice_chats] if permission == "can_manage_voice_chats" else pers.can_manage_voice_chats,
            can_promote_members = Change_Permissions_To[pers.can_promote_members] if permission == "can_promote_members" else pers.can_promote_members)
            return True
        except Exception as e: return str(e)

Manage = ManageChannel()

#Other Functions

def Spam_Detection(chat_id):
    try:
        user = Spams[chat_id]
        user["messages"] += 1
    except:
        Spams[chat_id] = {"next_time": int(time()) + Max_Seconds, "messages": 1}
        user = Spams[chat_id]
    if user["next_time"] > int(time()):
        if user["messages"] > Max_Messages:
            return True
    else:
        Spams[chat_id]["messages"] = 1
        Spams[chat_id]["next_time"] = int(time()) + Max_Seconds
    return False

def addFosh(Fosh: str):
    try:
        global Forbidden_words
        all = ascii_lowercase + ascii_uppercase + digits
        new_id = "".join(sample(all, 10))
        if new_id in Forbidden_words:
            while new_id not in Forbidden_words: new_id = "".join(sample(all, 10))
        Forbidden_words[new_id] = Fosh
        settings['Forbidden_words'][new_id] = Fosh
        R_R_S()
        return True
    except Exception as e: return str(e)

def delFosh(id_word: str):
    try:
        global Forbidden_words
        del Forbidden_words[id_word]
        settings['Forbidden_words'] = Forbidden_words
        R_R_S()
        return True
    except Exception as e: return str(e)

#----------------------------#

#Guide Text

Help_text = """
**راهنمای آنتی تبر**
`!help`


**مشاهده کانال های ثبت شده**
`!show_channels`


**اضافه کردن ضد تبر در کانال**
`!add_channel x`
__x: username / chat_id__


**حذف کردن ضد تبر در کانال**
`!rmw_channel x`
__x: username / chat_id__


**ادمین کردن x در channel:**
`!add_admin x channel`
__x: username / chat_id
channel: username / chat_id__


**از ادمینی دراوردن x در channel:**
`!rmw_admin x channel`
__x: username / chat_id
channel: username / chat_id__


**از ادمینی دراوردن همه در channel:**
`!rmw_all_admins channel`
__channel: username / chat_id__


**دسترسی دادن/ گرفتن از ادمین x در channel:**
`!permission x permission channel`
__x: username / chat_id
channel: username / chat_id
permissions:__
`can_change_info` \ 
`can_post_messages` \ 
`can_edit_messages` \ 
`can_delete_messages` \ 
`can_invite_users` \ 
`can_manage_voice_chats` \ 
`can_promote_members`


**قفل کردن کانال**
`!lock_channel`


**باز کردن قفل کردن کانال**
`!unlock_channel`


**قفل کردن پیام پشت سر هم**
`!lock_spam`


**بازکردن قفل کردن پیام پشت سر هم**
`!unlock_spam`


**تنظیم اسپم**
`!set_spam x y`
__x, y: حداکثر x پیام در y ثانیه
x, y: [1, 2, 3, 4, 5, ...]__


**پاک کردن پیام ها تا پیام ریپلی شده**
`!del`


**مشاهده کلمه های غیر مجاز**
`!show_words`


**اضافه کردن کلمه غیر مجاز**
`!add_word x`
__x: Hello, Hi, Bye, ...__


**حذف کردن کلمه غیر مجاز**
`!del_word x`
__x: Word ID__


**By:
@MrCherik**
"""

#----------------------------#

#Main Functions

async def Help_Cli(cli: Client, message: Message):
    await message.edit(Help_text, parse_mode = 'markdown')

async def Add_Admin_Cli(cli: Client, message: Message):
    try:
        is_admin = await Manage.Add_Admin_Cli(message.command[2], message.command[1])
        Ch = await cli.get_chat(message.command[2])
        if is_admin: await message.edit('آیدی {} با موفقیت در کانال {} ادمین شد.'.format(message.command[1], Ch.title))
        else: await message.edit(is_admin)
    except IndexError: await message.edit('پارامتر ها درست وارد نشده.')

async def Demote_Admin_Cli(cli: Client, message: Message):
    try:
        is_admin = await Manage.Demote_Admin_Cli(message.command[2], message.command[1])
        Ch = await cli.get_chat(message.command[2])
        if is_admin: await message.edit('آیدی {} با موفقیت از کانال {} دیموت شد.'.format(message.command[1], Ch.title))
        else: await message.edit(is_admin)
    except IndexError: await message.edit('پارامتر ها درست وارد نشده.')

async def Demote_All_Admins(cli: Client, message: Message):
    Admins = await Manage.Get_Admins(message.command[1])
    Demoted_Admins = list()
    for Admin in Admins:
        is_admin = await Manage.Demote_Admin_Cli(message.command[1], Admin.user.id)
        if is_admin:
            Demoted_Admins.append(f"[{Admin.user.first_name}](tg://user?id={Admin.user.id})")
        else:
            await message.edit(is_admin)
            return
    await message.edit('ادمین ها با موفقیت دیموت شدند\nادمین های  دیموت شده:\n{}'.format("\n".join(Demoted_Admins)), 'markdown')

async def Change_Permission(cli: Client, message: Message):
    try:
        if message.command[1].isdigit() and message.command[1] in await Manage.Get_Admins_Chat_ID(message.command[3]):
            Admins_Permissions = await Manage.Get_Admin_Permissions(message.command[3], message.command[1])
            permission = await Manage.Change_Permissions(message.command[3], message.command[1], message.command[2], Admins_Permissions)
            if permission: await message.edit('دسترسی {} ادمین {} با موفقیت تغییر کرد.'.format(message.command[2], message.command[1]))
            else: await message.edit(permission)

        elif message.command[1].startswith('@') and message.command[1].replace('@', '') in await Manage.Get_Admins_Username(message.command[3]):
            Admins_Permissions = await Manage.Get_Admin_Permissions(message.command[3], message.command[1])
            permission = await Manage.Change_Permissions(message.command[3], message.command[1], message.command[2], Admins_Permissions)
            if permission: await message.edit('دسترسی {} ادمین {} با موفقیت تغییر کرد.'.format(message.command[2], message.command[1]))
            else: await message.edit(permission)

        else: await message.edit('این آیدی در کانال ادمین نیست.')

    except IndexError: await message.edit('پارامتر ها درست وارد نشده.')

async def Lock_Channel(cli: Client, message: Message):
    global Lock_Channel_Messages
    Lock_Channel_Messages = True
    settings["Lock_Channel"] = True
    R_R_S()
    await message.edit('کانال شما با موفقیت قفل شد.')

async def Unlock_Channel(cli: Client, message: Message):
    global Lock_Channel_Messages
    Lock_Channel_Messages = False
    settings["Lock_Channel"] = False
    R_R_S()
    await message.edit('کانال شما با موفقیت باز شد.')

async def Lock_Spam(cli: Client, message: Message):
    global Lock_Spams
    Lock_Spams = True
    settings["Lock_Spam"] = True
    R_R_S()
    await message.edit('قفل اسپم کانال شما با موفقیت فعال شد.')

async def Unlock_Spam(cli: Client, message: Message):
    global Lock_Spams
    Lock_Spams = False
    settings["Lock_Spam"] = False
    R_R_S()
    await message.edit('قفل اسپم کانال شما با موفقیت غیرفعال شد.')

async def Set_Spam(cli: Client, message: Message):
    try:
        if message.command[1].isdigit() and message.command[2].isdigit():
            global Max_Messages
            global Max_Seconds
            Max_Messages = int(message.command[1])
            Max_Seconds = int(message.command[2])
            settings['Spam_Max_Messages'] = int(message.command[1])
            settings['Spam_Max_Seconds'] = int(message.command[2])
            R_R_S()
            await message.edit('تعداد مجاز ارسال پیام در کانال به حداکثر {} پیام در {} ثانیه با موفقیت ثبت شد.'.format(Max_Messages, Max_Seconds))
        else: await message.edit('پارامتر ها درست وارد نشده.')
    except IndexError: await message.edit('پارامتر ها درست وارد نشده.')

async def Delete_Messages(cli: Client, message: Message):
    if message.chat.id in Channels:
        if message.reply_to_message:
            Last_Post = message.message_id
            Post = message.reply_to_message.message_id
            for message_id in range(Post, Last_Post + 1):
                await cli.delete_messages(message.chat.id, message_id)
        else: await message.edit('این پیام روی پستی ریپلی نشده.')
    else: await message.edit('شما فقط میتونید این دستور رو داخل کانال خودتون بزنید.')

async def Set_Admin_Status(cli: Client, message: Message):
    await message.edit('این دستور فعلا غیر فعاله.')

async def Show_Words(cli: Client, message: Message):
    if Forbidden_words == {}: await message.edit("کلمه ی غیر مجازی یافت نشد.")
    else:
        Words = [f"آیدی کلمه: `{i}` ، کلمه: **{j}**" for i,j in zip(Forbidden_words.keys(), Forbidden_words.values())]
        await message.edit("لیست کلمه های غیرمجاز ثبت شده تا کنون:\n\n"+"\n".join(Words))

async def Add_Word(cli: Client, message: Message):
    try:
        add_word = addFosh(message.command[1])
        if add_word: await message.edit('کلمه ی {} با موفقیت غیر مجاز شد.'.format(message.command[1]))    
        else: await message.edit(add_word)
    except IndexError: await message.edit('پارامتر ها درست وارد نشده.')

async def Del_Word(cli: Client, message: Message):
    try:
        del_word = delFosh(message.command[1])
        if del_word: await message.edit('آیدی کلمه ی {} با موفقیت از لیست کلمات غیر مجاز حذف شد.'.format(message.command[1]))    
        else: await message.edit(del_word)
    except IndexError: await message.edit('پارامتر ها درست وارد نشده.')


async def Add_Channel(cli: Client, message: Message):
    try:
        channel = await cli.get_chat(message.command[1])
        await cli.get_chat_member(message.command[1], ACCOUNT.id)
        await cli.get_chat_member(message.command[1], BOT.id)
        Channels.append(channel.id)
        settings['Channels'] = Channels
        R_R_S()
        await message.edit('کانال با ایدی عددی {} با موفقیت به لیست کانال ها اضافه شد.'.format(channel.id))

    except UserNotParticipant:
        await message.edit('ربات یا اکانت شما در این کانال عضو نیست.')

    except ChatAdminRequired:
        await message.edit('اکانت شما در این کانال ادمین نیست.')

    except ChannelPrivate:
        await message.edit('این کانال خصوصی میباشد، یا اکانت از این کانال بن شده.')

    except IndexError:
        await message.edit('پارامتر ها درست وارد نشده.')


async def Remove_Channel(cli: Client, message: Message):
    try:
        Channels.remove(int(message.command[1]))
        settings['Channels'] = Channels
        R_R_S()
        await message.edit('کانال با ایدی عددی {} با موفقیت حذف شد.'.format(message.command[1]))

    except ValueError:
        await message.edit('آیدی عددی کانال وارد شده اشتباه میباشد.')
    
    except IndexError:
        await message.edit('پارامتر ها درست وارد نشده.')

async def Show_Channels(cli: Client, message: Message):
    All_Channels = str()

    if Channels == []:
        await message.edit('هیچ کانالی تا کنون ثبت نکردید.')
        return

    for channel in Channels:
        try:
            await cli.get_chat_member(channel, ACCOUNT.id)
            await cli.get_chat_member(channel, BOT.id)
            Ch = await cli.get_chat(channel)
            All_Channels = f'{All_Channels}\n\n<b>{Ch.title}</b>:\n<code>{channel}</code>\n<a href="{Ch.invite_link}">Link</a>'

        except UserNotParticipant:
            Channels.remove(channel)
            settings['Channels'] = Channels
            R_R_S()

        except ChatAdminRequired:
            Channels.remove(channel)
            settings['Channels'] = Channels
            R_R_S()

    await message.edit('کانال های ثبت شده در ضد تبر شما:\n\n'+All_Channels, "HTML", disable_web_page_preview = True)


async def Filter_Channels(_, __, message):
    return message.chat.id in Channels

channels = filters.create(Filter_Channels)

#----------------------------#

#Check Member Is Kicked Or Not

async def Check_Kicked(api: Client, chat_member: ChatMemberUpdated):
    if chat_member.new_chat_member and chat_member.new_chat_member.restricted_by:
        if chat_member.new_chat_member.restricted_by.id in Owner:
            pass
        else:
            try:
                await cli.promote_chat_member(chat_member.chat.id, chat_member.new_chat_member.restricted_by.username, can_manage_chat = False)
            except:
                await cli.promote_chat_member(chat_member.chat.id, chat_member.new_chat_member.restricted_by.id, can_manage_chat = False)

#----------------------------#

#Check Channel's Messages

async def Messages(cli: Client, message: Message):
    if message.edit_date:
        return

    if Lock_Channel_Messages:
        await message.delete()
        return
        
    if Lock_Spams:
        if Spam_Detection(message.chat.id):
            await cli.delete_messages(message.chat.id, message.message_id)
            return
    
    if Forbidden_words != {}:
        if message.text:
            for Word in message.text.split():
                if Word in Forbidden_words.values():
                    await cli.delete_messages(message.chat.id, message.message_id)
        elif message.caption:
            for Word in message.caption.split():
                if Word in Forbidden_words.values():
                    await cli.delete_messages(message.chat.id, message.message_id)

#----------------------------#

#Handle Main Functions

cli.add_handler(MessageHandler(Help_Cli, filters.me & filters.regex('help')))

cli.add_handler(MessageHandler(Add_Admin_Cli, filters.me & filters.command('add_admin', '!')))

cli.add_handler(MessageHandler(Demote_Admin_Cli, filters.me & filters.command('rmw_admin', '!')))

cli.add_handler(MessageHandler(Demote_All_Admins, filters.me & filters.command('rmw_all_admins', '!')))

cli.add_handler(MessageHandler(Change_Permission, filters.me & filters.command('permission', '!')))

cli.add_handler(MessageHandler(Delete_Messages, filters.me & filters.command('del', '!')))

cli.add_handler(MessageHandler(Lock_Channel, filters.me & filters.command('lock_channel', '!')))

cli.add_handler(MessageHandler(Unlock_Channel, filters.me & filters.command('unlock_channel', '!')))

cli.add_handler(MessageHandler(Lock_Spam, filters.me & filters.command('lock_spam', '!')))

cli.add_handler(MessageHandler(Unlock_Spam, filters.me & filters.command('unlock_spam', '!')))

cli.add_handler(MessageHandler(Set_Spam, filters.me & filters.command('set_spam', '!')))

cli.add_handler(MessageHandler(Show_Words, filters.me & filters.command('show_words', '!')))

cli.add_handler(MessageHandler(Add_Word, filters.me & filters.command('add_word', '!')))

cli.add_handler(MessageHandler(Del_Word, filters.me & filters.command('del_word', '!')))

cli.add_handler(MessageHandler(Set_Admin_Status, filters.me & filters.command('set', '!')))

cli.add_handler(MessageHandler(Add_Channel, filters.me & filters.command('add_channel', '!')))

cli.add_handler(MessageHandler(Remove_Channel, filters.me & filters.command('rmw_channel', '!')))

cli.add_handler(MessageHandler(Show_Channels, filters.me & filters.command('show_channels', '!')))

cli.add_handler(MessageHandler(Messages, filters.channel & channels))

api.add_handler(ChatMemberUpdatedHandler(Check_Kicked, channels))

#----------------------------#

#Idle To Run Bot ForEver

idle()
cli.stop()
api.stop()

#----------------------------#
