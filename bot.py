import os
import shutil
import argparse
from PIL import Image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)


def convert_tif_to_png(compression_level=6):
    tif_files = [f for f in os.listdir(tif_dir) if f.endswith(".tif")]
    print(
        f"Converting {len(tif_files)} .tifs to .pngs and compressing them. Please wait a moment..."
    )

    for tif_file in tif_files:
        tif_path = os.path.join(tif_dir, tif_file)
        png_path = os.path.join(image_dir, tif_file.replace(".tif", ".png"))

        with Image.open(tif_path) as img:
            img.save(png_path, "PNG", compress_level=compression_level)

    print(f"Converted and compressed {len(tif_files)} .tif files to .png format.")


processing_files = {}


def get_files():
    images = [f for f in os.listdir(image_dir) if f.endswith(".png")]
    masks = [f for f in os.listdir(mask_dir) if f.endswith(".png")]
    images_with_masks = [f for f in images if f in masks]
    print(len(images_with_masks))
    return images_with_masks


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["files"] = get_files()
    await send_next_image_and_mask(update, context, update.message.chat_id)


async def send_next_image_and_mask(
    update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id
):
    files = context.user_data.get("files", [])
    while files:
        filename = files.pop(0)
        image_path = os.path.join(image_dir, filename)
        mask_path = os.path.join(mask_dir, filename)

        if (
            os.path.exists(image_path)
            and os.path.exists(mask_path)
            and filename not in processing_files
        ):
            processing_files[filename] = chat_id
            context.user_data["files"] = files
            keyboard = [
                [
                    InlineKeyboardButton("Keep", callback_data=f"keep:{filename}"),
                    InlineKeyboardButton("Unclear", callback_data=f"move:{filename}"),
                    InlineKeyboardButton(
                        "Confusing", callback_data=f"later:{filename}"
                    ),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            try:
                with (
                    open(image_path, "rb") as image_file,
                    open(mask_path, "rb") as mask_file,
                ):
                    media_group = [
                        InputMediaPhoto(media=image_file),
                        InputMediaPhoto(media=mask_file),
                    ]
                    await context.bot.send_media_group(
                        chat_id=chat_id, media=media_group
                    )
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"Image and Mask: {filename}",
                    reply_markup=reply_markup,
                )
                return
            except Exception as e:
                print(f"Failed to send image or mask: {e}")
                await context.bot.send_message(
                    chat_id=chat_id, text=f"Failed to process image or mask: {e}"
                )
        else:
            context.user_data["files"] = files

    await context.bot.send_message(chat_id=chat_id, text="No images or masks found.")


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, filename = query.data.split(":")

    if (
        filename not in processing_files
        or processing_files[filename] != query.message.chat_id
    ):
        await query.edit_message_text(
            text="This image is already processed or not assigned to you."
        )
        return

    try:
        if action == "move":
            shutil.move(
                os.path.join(mask_dir, filename), os.path.join(unclear_dir, filename)
            )
            await query.edit_message_text(text=f"Removing: {filename}")
        elif action == "keep":
            shutil.move(
                os.path.join(mask_dir, filename), os.path.join(clean_dir, filename)
            )
            await query.edit_message_text(text=f"Keeping: {filename}")
        elif action == "later":
            shutil.move(
                os.path.join(mask_dir, filename), os.path.join(later_dir, filename)
            )
            await query.edit_message_text(text=f"To be processed later: {filename}")

        del processing_files[filename]
        await send_next_image_and_mask(query, context, query.message.chat_id)
    except Exception as e:
        print(f"Failed to move or copy image: {e}")
        await context.bot.send_message(
            query.message.chat_id, text=f"Failed to move or copy image: {e}"
        )


def main():
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
        convert_tif_to_png()

    os.makedirs(clean_dir, exist_ok=True)
    os.makedirs(unclear_dir, exist_ok=True)
    os.makedirs(later_dir, exist_ok=True)

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--safe_name",
        type=str,
        required=True,
        help="Name of your SAFE folder with saved tiles.",
    )
    parser.add_argument(
        "-t", "--token", type=str, required=True, help="Your telegram bot Token."
    )
    args = parser.parse_args()

    TOKEN = args.token
    tif_dir = os.path.join("./data/tiles", args.safe_name)
    mask_dir = os.path.join("./data/bot_filter/masks", args.safe_name)
    image_dir = os.path.join("./data/bot_filter/pngs", args.safe_name)
    clean_dir = os.path.join("./data/bot_filter/clear_masks", args.safe_name)
    unclear_dir = os.path.join("./data/bot_filter/unclear_masks", args.safe_name)
    later_dir = os.path.join("./data/bot_filter/later", args.safe_name)

    main()
