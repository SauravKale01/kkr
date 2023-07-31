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
import seaborn as sns
import schedule
import time

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

    # Create the bar graph using seaborn and matplotlib
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")
    sns.barplot(x=user_counts, y=user_names, palette="viridis")
    plt.title("Top Users Today", fontsize=16)
    plt.xlabel("Counts", fontsize=14)
    plt.ylabel("Users", fontsize=14)

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

# Modify the show_top_overall_callback function
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
    user_names = []  # Fetch user names again
    user_counts = []  # Fetch user counts again
    for user_id, count in sorted(overall_dict.items(), key=lambda x: x[1], reverse=True)[:10]:
        user_name = await get_name(app, user_id)
        t += f"**{pos}.** {user_name} - {count}\n"
        user_names.append(user_name)
        user_counts.append(count)
        pos += 1

    # Use seaborn to style the plot
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))  # Adjust the figure size

    # Create the horizontal bar chart (polar chart)
    plt.barh(user_names, user_counts, color="lightcoral")

    # Add labels and title
    plt.xlabel("Message Count")
    plt.ylabel("Users")
    plt.title("Overall Top Users - Message Counts")

    # Add count labels to the poles
    for index, value in enumerate(user_counts):
        plt.text(value, index, str(value), ha="left", va="center", color="black", fontweight='bold')

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
            [[InlineKeyboardButton("Today's Ranking", callback_data="today")]]
        ),
    )


# Modify the show_top_today_callback function
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

    # Use seaborn to style the plot
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))  # Adjust the figure size

    # Create the horizontal bar chart (polar chart)
    plt.barh(user_names, user_counts, color="skyblue")

    # Add labels and title
    plt.xlabel("Message Count")
    plt.ylabel("Users")
    plt.title("Top Users Today - Message Counts")

    # Add count labels to the poles
    for index, value in enumerate(user_counts):
        plt.text(value, index, str(value), ha="left", va="center", color="black", fontweight='bold')

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


# Helper function to send the daily message
async def send_daily_message():
    for chat_id in chatdb.distinct("chat"):
        t_data = await show_top_today(chat_id)
        if t_data:
            t, user_names, user_counts = t_data
            buffer = create_bar_graph(
                user_names, user_counts, "Top Users Today", "Users", "Counts"
            )
            await app.send_photo(
                chat_id=chat_id,
                photo=buffer,
                caption=t,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Overall Ranking", callback_data="overall")]]
                ),
            )


# Schedule the daily message
def schedule_daily_message():
    schedule.every().day.at("01:31").do(asyncio.run, send_daily_message)

print("started")
schedule_daily_message()
app.run()

