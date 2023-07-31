from utils.db import get_name, increase_count, chatdb
import uvloop
from pyrogram.client import Client
from pyrogram import filters
from datetime import date
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
import matplotlib.pyplot as plt
import io 

uvloop.install()
app = Client(
    "boto",
    api_id="19099900",
    api_hash="2b445de78e5baf012a0793e60bd4fbf5",
    bot_token="6206599982:AAFhXRwC0SnPCBK4WDwzdz7TbTsM2hccgZc",
)


@app.on_message(
    ~filters.bot
    & ~filters.forwarded
    & filters.group
    & ~filters.via_bot
    & ~filters.service
)
async def inc_user(_, message: Message):
    if message.text:
        if (
            message.text.strip() == "/top@RankingssBot"
            or message.text.strip() == "/top"
        ):
            return await show_top_today(_, message)

    chat = message.chat.id
    user = message.from_user.id
    increase_count(chat, user)
    print(chat, user, "increased")


async def show_top_today(_, message: Message):
    print("today top in", message.chat.id)
    chat = chatdb.find_one({"chat": message.chat.id})
    today = str(date.today())

    if not chat:
        return await message.reply_text("no data available")

    if not chat.get(today):
        return await message.reply_text("no data available for today")

    t = "🔰 **Today's Top Users :**\n\n"

    pos = 1
    user_names = []
    user_counts = []
    for i, k in sorted(chat[today].items(), key=lambda x: x[1], reverse=True)[:10]:
        i = await get_name(app, i)

        t += f"**{pos}.** {i} - {k}\n"
        user_names.append(i)
        user_counts.append(k)
        pos += 1

    # Create the bar graph
    fig, ax = plt.subplots()
    ax.bar(user_names, user_counts)
    ax.set_title("Top Users Today")
    ax.set_xlabel("Users")
    ax.set_ylabel("Counts")

    # Save the graph to a buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    # Send the graph as a photo with the caption
    await message.reply_photo(
        photo=buffer,
        caption=t,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Overall Ranking", callback_data="overall")]]
        ),
    )


@app.on_callback_query(filters.regex("overall"))
async def show_top_overall_callback(_, query: CallbackQuery):
    print("overall top in", query.message.chat.id)
    chat = chatdb.find_one({"chat": query.message.chat.id})

    if not chat:
        return await query.answer("No data available", show_alert=True)

    await query.answer("Processing... Please wait")

    t = "🔰 **Overall Top Users :**\n\n"

    overall_dict = {}
    for i, k in chat.items():
        if i == "chat" or i == "_id":
            continue

        for j, l in k.items():
            if j not in overall_dict:
                overall_dict[j] = l
            else:
                overall_dict[j] += l

    pos = 1
    for i, k in sorted(overall_dict.items(), key=lambda x: x[1], reverse=True)[:10]:
        i = await get_name(app, i)

        t += f"**{pos}.** {i} - {k}\n"
        pos += 1

   # Create the bar graph
    fig, ax = plt.subplots()
    ax.bar(user_names, user_counts)
    ax.set_title("Overall Top Users")
    ax.set_xlabel("Users")
    ax.set_ylabel("Counts")

    # Save the graph to a buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    # Send the graph as a photo with the caption
    await query.message.edit_photo(
        photo=buffer,
        caption=t,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Today's Ranking", callback_data="today")]]
        ),
    )
@app.on_callback_query(filters.regex("today"))
async def show_top_today_callback(_, query: CallbackQuery):
    print("today top in", query.message.chat.id)
    chat = chatdb.find_one({"chat": query.message.chat.id})
    today = str(date.today())

    if not chat:
        return await query.answer("No data available", show_alert=True)

    if not chat.get(today):
        return await query.answer("No data available for today", show_alert=True)

    await query.answer("Processing... Please wait")

    t = "🔰 **Today's Top Users :**\n\n"

    pos = 1
    user_names = []  # Fetch user names again
    user_counts = []  # Fetch user counts again
    for user_id, count in sorted(chat[today].items(), key=lambda x: x[1], reverse=True)[:10]:
        user_name = await get_name(app, user_id)
        t += f"**{pos}.** {user_name} - {count}\n"
        user_names.append(user_name)
        user_counts.append(count)
        pos += 1
    user_names = []  # Fetch user names again
    user_counts = []  # Fetch user counts again
    for i, k in sorted(chat[today].items(), key=lambda x: x[1], reverse=True)[:10]:
        i = await get_name(app, i)

        t += f"**{pos}.** {i} - {k}\n"
        user_names.append(i)
        user_counts.append(k)
        pos += 1

    # Create the bar graph
    fig, ax = plt.subplots()
    ax.bar(user_names, user_counts)
    ax.set_title("Top Users Today")
    ax.set_xlabel("Users")
    ax.set_ylabel("Counts")

    # Save the graph to a buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    # Delete the previous message
    await query.message.delete()

    # Send a new message with the updated photo and caption
    await query.message.reply_photo(
        photo=buffer,
        caption=t,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Overall Ranking", callback_data="overall")]]
        ),
    )


print("started")
app.run()
