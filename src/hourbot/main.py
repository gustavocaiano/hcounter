"""Telegram bot entrypoint and message routing."""

from __future__ import annotations

from datetime import datetime, time
from decimal import Decimal
import sqlite3
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from .config import Settings, load_settings
from .db import init_db, insert_entry
from .service import (
    format_hours_total,
    format_subtotals,
    get_current_month_total,
    get_selected_month_total,
    parse_getmm,
    parse_hours,
)


def _now_local(settings: Settings) -> datetime:
    return datetime.now(ZoneInfo(settings.tz))


def _get_day_total(db_path: str, *, user_id: int, chat_id: int, entry_date: str) -> Decimal:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT hours
            FROM entries
            WHERE user_id = ?
              AND chat_id = ?
              AND entry_date = ?
            """,
            (user_id, chat_id, entry_date),
        )
        total = Decimal("0")
        for (hours_value,) in rows:
            total += Decimal(hours_value)
        return total


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message is None:
        return
    await update.message.reply_text(
        "Hello! Send worked hours as a number (for example: 0, 0.5, 1, 2).\n"
        "Use /month to see this month's total."
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message is None:
        return
    await update.message.reply_text(
        "Commands:\n"
        "/start - intro\n"
        "/help - this help\n"
        "/month - current month subtotal\n"
        "getMM - selected month subtotal (example: get02)\n"
        "\n"
        "Send only a numeric value to add hours (example: 1 or 0.5)."
    )


async def month_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.effective_user is None or update.effective_chat is None:
        return

    settings: Settings = context.application.bot_data["settings"]
    now_local = _now_local(settings)
    month_total = get_current_month_total(
        settings.db_path,
        user_id=update.effective_user.id,
        chat_id=update.effective_chat.id,
        today=now_local.date(),
    )
    await update.message.reply_text(
        f"Month subtotal: {format_hours_total(month_total)}h"
    )


async def numeric_entry_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None:
        return
    if update.effective_user is None or update.effective_chat is None:
        return

    settings: Settings = context.application.bot_data["settings"]
    try:
        hours = parse_hours(update.message.text)
    except ValueError as exc:
        await update.message.reply_text(str(exc))
        return

    now_local = _now_local(settings)
    entry_date = now_local.date().isoformat()

    insert_entry(
        settings.db_path,
        user_id=update.effective_user.id,
        chat_id=update.effective_chat.id,
        entry_date=entry_date,
        hours=hours,
        raw_text=update.message.text,
    )

    day_total = _get_day_total(
        settings.db_path,
        user_id=update.effective_user.id,
        chat_id=update.effective_chat.id,
        entry_date=entry_date,
    )
    month_total = get_current_month_total(
        settings.db_path,
        user_id=update.effective_user.id,
        chat_id=update.effective_chat.id,
        today=now_local.date(),
    )

    await update.message.reply_text(format_subtotals(day_total, month_total))


async def getmm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None:
        return
    if update.effective_user is None or update.effective_chat is None:
        return

    settings: Settings = context.application.bot_data["settings"]
    month = parse_getmm(update.message.text)
    month_total = get_selected_month_total(
        settings.db_path,
        user_id=update.effective_user.id,
        chat_id=update.effective_chat.id,
        month=month,
        today=_now_local(settings).date(),
    )
    await update.message.reply_text(
        f"Month {month:02d} subtotal: {format_hours_total(month_total)}h"
    )


async def daily_reminder_callback(context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=(
            "Reminder: how many hours did you work today? "
            "Send a number like: 0, 0.5, 1, 2"
        ),
    )


def build_application(settings: Settings) -> Application:
    init_db(settings.db_path)

    app = Application.builder().token(settings.bot_token).build()
    app.bot_data["settings"] = settings

    reminder_time = time(
        hour=settings.reminder_hour,
        minute=settings.reminder_minute,
        tzinfo=ZoneInfo(settings.tz),
    )
    app.job_queue.run_daily(
        daily_reminder_callback,
        time=reminder_time,
        chat_id=settings.owner_chat_id,
        name="owner_daily_hours_reminder",
    )

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("month", month_handler))
    app.add_handler(MessageHandler(filters.Regex(r"^get(0[1-9]|1[0-2])$"), getmm_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, numeric_entry_handler))
    return app


def main() -> None:
    settings = load_settings()
    application = build_application(settings)
    application.run_polling()


if __name__ == "__main__":
    main()
