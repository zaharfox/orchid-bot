from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from database.db import get_all_users, get_orchids_needing_care


async def send_daily_reminders(bot: Bot):
    users = await get_all_users()
    for user in users:
        telegram_id = user[1]
        needing_care = await get_orchids_needing_care(telegram_id)
        if needing_care:
            lines = ["🌸 <b>Привет! Ваши орхидеи ждут ухода:</b>\n"]
            for orchid, needs in needing_care:
                lines.append(f"🌺 <b>{orchid[2]}</b> ({orchid[3]}):")
                for need in needs:
                    lines.append(f"  • {need}")
                lines.append("")
            lines.append("Откройте бота, чтобы отметить уход ✅")
            try:
                await bot.send_message(telegram_id, "\n".join(lines), parse_mode="HTML")
            except Exception as e:
                print(f"Failed to send reminder to {telegram_id}: {e}")


async def setup_scheduler(scheduler: AsyncIOScheduler, bot: Bot):
    """Add the daily reminder job. Runs every hour and checks user-specific times."""
    scheduler.add_job(
        send_daily_reminders,
        trigger="cron",
        hour=9,
        minute=0,
        args=[bot],
        id="daily_reminders",
        replace_existing=True
    )
