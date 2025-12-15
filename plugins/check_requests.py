import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS
from utils import temp
from database.notify_db import notify_db
from database.ia_filterdb import get_search_results

@Client.on_message(filters.command("check_requests") & filters.user(ADMINS))
async def check_pending_requests(client, message):
    """
    অ্যাডমিন কমান্ড: পেন্ডিং রিকোয়েস্ট চেক করা এবং ইউজারদের নোটিফাই করা।
    """
    if not await notify_db.get_all_notify():
        return await message.reply_text("<b>📂 বর্তমানে কোনো পেন্ডিং রিকোয়েস্ট নেই।</b>")

    status_msg = await message.reply_text("<b>⏳ পেন্ডিং রিকোয়েস্ট চেক করা হচ্ছে... দয়া করে অপেক্ষা করুন।</b>")
    
    # ডাটাবেস থেকে সব রিকোয়েস্ট আনা
    requests = await notify_db.get_all_notify()
    
    sent_count = 0
    deleted_count = 0
    total_requests = 0 # Cursor count is tricky in motor, iterating instead.

    async for req in requests:
        total_requests += 1
        user_id = req["id"]
        query = req["query"]
        
        # ডাটাবেসে মুভিটি আছে কিনা চেক করা
        files, _, _ = await get_search_results(message.chat.id, query)
        
        if files:
            try:
                # মুভি পাওয়া গেলে ইউজারকে মেসেজ পাঠানো
                btn = [[InlineKeyboardButton("🎬 Get Movie Now 🎬", url=f"https://t.me/{temp.U_NAME}?start=getfile-{query}")]]
                
                await client.send_message(
                    chat_id=user_id,
                    text=f"<b>🔔 নোটিফিকেশন:</b>\n\n<b>🥳 সুখবর! আপনার রিকোয়েস্ট করা মুভি/সিরিজ '{query}' এখন আমাদের বটে এভেইলেবল!\n\n👇 নিচের বাটনে ক্লিক করে এখনই ডাউনলোড করুন।</b>",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                
                # সফলভাবে পাঠানোর পর ডাটাবেস থেকে রিকোয়েস্ট ডিলিট করা
                await notify_db.remove_notify(user_id, query)
                sent_count += 1
                
            except Exception as e:
                # ইউজার যদি ব্লক করে থাকে বা অ্যাকাউন্ট ডিলিট করে থাকে
                await notify_db.remove_notify(user_id, query)
                deleted_count += 1
                logging.error(f"Failed to send notify to {user_id}: {e}")

    await status_msg.edit_text(
        f"<b>✅ চেকিং সম্পন্ন!</b>\n\n"
        f"📊 <b>পরিসংখ্যান:</b>\n"
        f"✉️ নোটিফিকেশন পাঠানো হয়েছে: <code>{sent_count}</code> জনকে\n"
        f"🗑️ ক্লিন করা হয়েছে (ব্লক/এরর): <code>{deleted_count}</code> টি\n"
        f"⏳ বাকি পেন্ডিং রিকোয়েস্ট: <code>{total_requests - sent_count - deleted_count}</code> টি"
    )
