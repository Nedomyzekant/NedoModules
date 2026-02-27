__version__ = (2, 2, 6)
# meta developer: @NedoModules

import asyncio
import re
from .. import loader, utils
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest

@loader.tds
class YouDownloader(loader.Module):
    """Скачивание YouTube видео через @SaveYoutubeBot"""
    
    strings = {
        "name": "YouDownloader",
        "no_args": "<b> <emoji document_id=5258084046788915494>🙅‍♂️</emoji> Укажи ссылку на YouTube!</b>",
        "no_url": "<b> <emoji document_id=5258084046788915494>🙅‍♂️</emoji> Ссылка не найдена.</b>",
        "searching": "<b> <emoji document_id=5832684940814192333>🔭</emoji> Ищу видео...</b>",
        "no_bot_res": "<b> <emoji document_id=5258084046788915494>🙅‍♂️</emoji> Бот @SaveYoutubeBot не отвечает.</b>",
        "no_formats": "<b> <emoji document_id=5258084046788915494>🙅‍♂️</emoji> Не найдено доступных форматов.</b>",
        "downloading": "<b>🚀 Бот готовит файл...</b>",
        "sending": "<b>📤 Отправляю в чат...</b>",
        "error": "<b> <emoji document_id=5303134392548355140>❌</emoji> Ошибка: {}</b>"
    }

    def __init__(self):
        self.bot_tag = "@SaveYoutubeBot"

    async def client_ready(self, client, db):
        self.client = client

    @loader.command()
    async def ytd(self, message):
        """<ссылка> — скачать видео с YouTube"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings["no_args"])

        link = re.search(r'(https?://[^\s]+)', args)
        if not link:
            return await utils.answer(message, self.strings["no_url"])
        
        video_url = link.group(1)
        chat_id = message.chat_id
        reply_to = message.reply_to_msg_id or message.id

        status_msg = await utils.answer(message, self.strings["searching"])
        
        try:
            sent = await self.client.send_message(self.bot_tag, video_url)
        except Exception as e:
            return await utils.answer(status_msg, self.strings["error"].format(e))

        bot_reply = None
        for _ in range(15):
            await asyncio.sleep(1.5)
            async for msg in self.client.iter_messages(self.bot_tag, limit=5):
                if msg.id > sent.id and msg.reply_markup:
                    bot_reply = msg
                    break
            if bot_reply:
                break

        if not bot_reply:
            return await utils.answer(status_msg, self.strings["no_bot_res"])

        video_title = "Неизвестно"
        title_match = re.search(r"📹\s*(.*?)\s*→", bot_reply.text)
        if title_match:
            video_title = title_match.group(1).strip()

        channel = "Неизвестен"
        author_match = re.search(r"👤\s*#?\s*(.*?)\s*→", bot_reply.text)
        if author_match:
            channel = author_match.group(1).strip()

        buttons = []
        for row in bot_reply.reply_markup.rows:
            btn_row = []
            for btn in row.buttons:
                if re.search(r'\d{3,4}p', btn.text) or "mp" in btn.text.lower():
                    btn_row.append({
                        "text": btn.text,
                        "callback": self._download_handler,
                        "args": (bot_reply.id, btn.data, chat_id, reply_to, sent.id, video_title, channel)
                    })
            if btn_row:
                buttons.append(btn_row)

        if not buttons:
            return await utils.answer(status_msg, self.strings["no_formats"])
        
        buttons.append([{"text": "🚫 Отмена", "action": "close"}])

        await status_msg.delete()

        preview_caption = f"<emoji document_id=5334681713316479679>📱</emoji> <b>{video_title}</b>\n<emoji document_id=5258011929993026890>👤</emoji> <b>{channel}</b>"
        preview_msg = await self.client.send_file(
            chat_id,
            bot_reply.media or "https://via.placeholder.com/600x400.png?text=YouTube",
            caption=preview_caption,
            reply_to=reply_to
        )

        for row in buttons:
            for btn in row:
                if "args" in btn:
                    btn["args"] = (*btn["args"], preview_msg.id)

        await self.inline.form(
            text="<b>📥 Выбери качество:</b>",
            message=chat_id,
            reply_markup=buttons,
            silent=True
        )

    async def _download_handler(self, call, msg_id, cb_data, chat_id, reply_to, sent_id, title, author, preview_id):
        try:
            await call.answer("Загружаю...", show_alert=False)
            await call.edit(self.strings["downloading"], reply_markup=None)

            await self.client(GetBotCallbackAnswerRequest(
                peer=self.bot_tag,
                msg_id=msg_id,
                data=cb_data
            ))

            updated = None
            for _ in range(100):
                await asyncio.sleep(2)
                msgs = await self.client.get_messages(self.bot_tag, ids=msg_id)
                if msgs and (msgs.video or msgs.document):
                    updated = msgs
                    break
            
            if not updated:
                await call.edit("<b>❌ Бот не прислал файл.</b>")
                return

            await call.edit(self.strings["sending"])
            
            final_caption = f"<emoji document_id=5334681713316479679>📱</emoji> <b>{title}</b>\n<emoji document_id=5258011929993026890>👤</emoji> <b>{author}</b>"
            await self.client.send_file(
                chat_id,
                updated.media,
                caption=final_caption,
                reply_to=reply_to,
                supports_streaming=True
            )
            
            # Убираем временные сообщения
            await call.delete()
            try:
                await self.client.delete_messages(chat_id, [preview_id])
            except:
                pass
            try:
                await self.client.delete_messages(self.bot_tag, [sent_id, msg_id])
            except:
                pass

        except Exception as e:
            await call.edit(self.strings["error"].format(str(e)))