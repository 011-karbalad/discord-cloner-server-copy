import discord
import json
import os
# ⚠️ توکن اکانت دیسکورد خودتو اینجا بذار
TOKEN = "your token"

client = discord.Client()

@client.event
async def on_ready():
    print(f"✅ Logged in as: {client.user} (ID: {client.user.id})")

@client.event
async def on_message(message):
    if message.author.id != client.user.id:
        return


    if message.content == "1back":
        guild = message.guild
        backup_data = {
            "guild_name": guild.name,
            "roles": [],
            "categories": [],
            "channels": []
        }

   
        for role in guild.roles:
            if role.is_default():
                continue
            backup_data["roles"].append({
                "name": role.name,
                "color": role.color.value,
                "permissions": role.permissions.value,
                "position": role.position
            })

        # گرفتن کتگوری‌ها
        for category in guild.categories:
            backup_data["categories"].append({
                "id": category.id,
                "name": category.name
            })

        # گرفتن چنل‌ها و وابستگی‌شون به کتگوری
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel) or isinstance(channel, discord.VoiceChannel):
                backup_data["channels"].append({
                    "name": channel.name,
                    "type": str(channel.type),
                    "category_id": channel.category_id
                })

        # ذخیره در فایل
        with open("backup.json", "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=4)

        await message.channel.send("✅ بکاپ با موفقیت گرفته شد!")

    #  اجرای بکاپ
    if message.content == "/restore":
        guild = message.guild
        if not os.path.exists("backup.json"):
            await message.channel.send("⛔ فایل بکاپ وجود ندارد.")
            return

        with open("backup.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # ساخت رول‌ها
        for role_data in data["roles"]:
            await guild.create_role(
                name=role_data["name"],
                color=discord.Color(role_data["color"]),
                permissions=discord.Permissions(role_data["permissions"]),
                
            )

        # ساخت کتگوری‌ها (و نگه‌داشتن مپ ID قدیم به جدید)
        category_map = {}
        for category in data["categories"]:
            new_cat = await guild.create_category(name=category["name"])
            category_map[category["id"]] = new_cat

        # ساخت چنل‌ها داخل کتگوری مناسب
        for channel in data["channels"]:
            ch_type = channel["type"]
            cat_obj = category_map.get(channel["category_id"])

            if ch_type == "text":
                await guild.create_text_channel(channel["name"], category=cat_obj)
            elif ch_type == "voice":
                await guild.create_voice_channel(channel["name"], category=cat_obj)

        await message.channel.send("🎉 ریستور با موفقیت انجام شد!")

client.run(TOKEN)
