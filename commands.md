# Telegram Bot Commands

This file documents the inputs accepted by Hourbot in Telegram.

## Slash commands

- `/start` - sends the welcome message and basic usage.
- `/help` - shows command help and examples.
- `/commands` - shows the full accepted command list.
- `/month` - shows your current month subtotal.

The bot also registers these slash commands with Telegram (`setMyCommands`), so typing `/` in chat should show command suggestions.

## Text command

- `getMM` - shows subtotal for a selected month in the current year.
  - Format: `get01` to `get12`
  - Examples: `get02`, `get09`, `get12`
  - Rules: lowercase `get` and always 2-digit month.

## Hour entry input

You can send worked hours either as decimal hours or with `h`/`m` suffixes.

- Accepted examples: `0`, `1`, `0.5`, `12.75`, `2h`, `2h 30m`, `30m`, `-1`
- Rules:
  - negative values are allowed for corrections (for example: `-1`)
  - must use `.` as decimal separator
  - with suffixes, `h` means hours and `m` means minutes
  - `+` prefix is not accepted (for example `+2`)
  - no shorthand decimals (for example `.5` is not accepted)

If an input does not match these formats, the bot replies with a validation error.
