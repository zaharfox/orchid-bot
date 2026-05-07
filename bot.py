import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN
from database.db import init_db
from handlers import start, orchids, care, facts, reminders, settings
from utils.scheduler import setup_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Init DB
    await init_db()

    # Register routers
    dp.include_router(start.router)
    dp.include_router(orchids.router)
    dp.include_router(care.router)
    dp.include_router(facts.router)
    dp.include_router(reminders.router)
    dp.include_router(settings.router)

    # Setup scheduler for notifications
    scheduler = AsyncIOScheduler()
    await setup_scheduler(scheduler, bot)
    scheduler.start()

    logger.info("Bot started!")
    await dp.start_polling(bot, skip_updates=False)


if __name__ == "__main__":
    asyncio.run(main())
