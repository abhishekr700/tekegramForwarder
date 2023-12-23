from telethon import TelegramClient, events, sync
from telethon.tl.types import UpdateNewMessage
from telethon.tl.types import InputMessagesFilterPhotos
import os
import logging
import sys

# Logging setup
logging.basicConfig(
    filename='output.log',
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO)
# Also log to stdout
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

tg_api_id = os.getenv("TG_API_ID")
tg_api_hash = os.getenv("TG_API_HASH")

# Chats to monitor messages from
main_grp=int(os.getenv("MAIN_GRP"))
test_forward_grp=int(os.getenv("TEST_GRP"))
nitish_dm=int(os.getenv("TEST_DM"))


# Group to forward messages to
forward_grp=int(os.getenv("FWD_GRP"))

client = TelegramClient('session_name', tg_api_id, tg_api_hash)

# Utility function to forward message to a group
async def forwardToGrp(msg):
    msgId = msg.id
    logging.info("Forward to grp: %s", msgId)
    # chatId = event.chat_id
    msgText = msg.text
    # isReply = event.is_reply
    msgPhoto = msg.photo
    sender = msg.sender
    senderName = ''.join(filter(None, [sender.first_name, " ", sender.last_name]))

    msgWithSender = senderName + ":" + msgText

    if msgPhoto is not None:
        filePath = await client.download_media(msg.photo, "./image")
        logging.info("Image saved to: %s", filePath)
    else:
        filePath = None

    await client.send_message(forward_grp, msgWithSender, file = filePath)

    # Remove the downloaded image
    if filePath is not None:
        os.remove(filePath)
        logging.info("file deleted")

@client.on(events.NewMessage)
async def newMessageEventHandler(event):
    chatId = event.chat_id
    msgText = event.message.text
    isReply = event.is_reply
    msgPhoto = event.message.photo
    sender = event.message.sender

    if event.chat_id != test_forward_grp and event.chat_id != nitish_dm and event.chat_id != main_grp:
        logging.info("Unneceesary chat: %s", chatId)
        return

    senderName = ''.join(filter(None, [sender.first_name, " ", sender.last_name]))
    myMsgText = senderName + ":" + msgText

    logging.info({
        'chatId': chatId,
        'msgText': msgText,
        'isReply': isReply,
        'msgPhoto': msgPhoto,
        'sender': sender,
        'senderName': senderName,
        'myMsgText': myMsgText
    })


    if event.chat_id == test_forward_grp or event.chat_id == nitish_dm or event.chat_id == main_grp:
        try:
            await forwardToGrp(event.message)
        except Exception as e:
            logging.error(e)
            await client.send_message(forward_grp, "Forwarding failed.")





# Test func : try to get old messages from a group and invoke forwardToGrp
async def getMsg():
    logging.info("getmsg call")
    msgs = await client.get_messages(main_grp, 3, filter=InputMessagesFilterPhotos)
    logging.info("Total Messages %s", len(msgs))
    for msg in msgs:
        await forwardToGrp(msg)


async def main():
    # Now you can use all client methods listed below, like for example...
    # await client.send_message('me', 'Hello to myself!')
    await getMsg()

with client:
    # Uncomment below when you want to run main()
    # client.loop.run_until_complete(main())
    client.run_until_disconnected()


