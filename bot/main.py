"""Bot entrypoint: python -m bot.main (long polling)."""
import logging

from telegram.ext import Application, CommandHandler

from app.config import TELEGRAM_BOT_TOKEN
from app.db import Base, engine
from app import models  # noqa: F401 — register tables
from bot import handlers


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s — %(message)s", level=logging.INFO
    )
    if not TELEGRAM_BOT_TOKEN:
        raise SystemExit(
            "TELEGRAM_BOT_TOKEN bo'sh. .env fayliga BotFather'dan olingan tokenni "
            "yozing (qarang: .env.example)."
        )

    Base.metadata.create_all(bind=engine)  # idempotent; safe if API already created tables

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", handlers.cmd_start))
    app.add_handler(CommandHandler("help", handlers.cmd_help))
    app.add_handler(CommandHandler("debt", handlers.cmd_debt))
    app.add_handler(CommandHandler("pay", handlers.cmd_pay))
    app.add_handler(CommandHandler("students", handlers.cmd_students))
    app.add_error_handler(handlers.on_error)

    print("Bot ishga tushdi (polling). To'xtatish: Ctrl+C")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
