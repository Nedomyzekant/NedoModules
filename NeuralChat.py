__version__ = (0, 2, 0)
# meta developer: @NedoModules
# requires: aiohttp

import asyncio
import json
import re
import time
import io
import base64
import logging
from typing import Optional, Dict, Any, Tuple, List

import aiohttp
from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class NeuralChatMod(loader.Module):
    strings = {
        "name": "NeuralChat [BETA]",
        "no_args": "<b>Введите запрос!</b>",
        "no_reply": " <b>Ответьте на сообщение для контекста!</b>",
        "no_api_config": " <b>Сначала настройте API!</b>\nИспользуйте: .nset key &lt;ключ&gt;, .nset url &lt;url&gt;, .nset model &lt;модель&gt;",
        "generating": " <b>Генерирую ответ...</b>\n<i>Модель: {model}</i>",
        "generating_code": " <b>Генерирую код...</b>\n<i>Модель: {model}</i>",
        "error": " <b>Ошибка API:</b>\n<code>{error}</code>",
        "timeout": "<b>Таймаут запроса</b>",
        "config_saved": "<b>Настройки сохранены!</b>\n{config}",
        "config_cleared": " <b>Настройки очищены</b>",
        "current_config": "<b>Текущие настройки:</b>\n{config}",
        "api_list": " <b>Поддерживаемые API:</b>\n{list}\n<b>Также поддерживаются любые openai подобные API!</b>",
        "prompt_variables": "🔧 <b>Доступные переменные в промпте:</b>\n{vars}",
        "response_variables": "🔧 <b>Доступные переменные в шаблоне ответа:</b>\n{vars}",
        "template_set": "<b>Шаблон ответа установлен!</b>",
        "file_sent": " <b>Код отправлен файлом!</b>\n{info}",
        "file_analysis": "🔍 <b>Анализирую файл...</b>\n<i>Тип: {file_type}</i>\n<i>Модель: {model}</i>",
        "file_not_found": "❌ <b>Файл не найден!</b>\nОтветьте на сообщение с файлом.",
        "no_file_content": "❌ <b>Не удалось получить содержимое файла!</b>",
        "analysis_no_question": "❌ <b>Укажите вопрос для анализа!</b>\nИспользуйте: .ncheck &lt;вопрос&gt; &lt;реплай на файл&gt;",
        "connection_error": "❌ <b>Ошибка соединения:</b>\n<code>{error}</code>\nПроверьте интернет-соединение и URL API.",
        "api_response_error": "❌ <b>Некорректный ответ от API:</b>\n<code>{error}</code>",
        "streaming_generation": "🔄 <b>Генерирую ответ...</b>\n<i>Модель: {model}</i>\n<i>Получено символов: {chars}</i>",
        "usage": (
            "<b>Использование:</b>\n\n"
            "<code>.nchat [промт]</code> - Задать вопрос нейросети\n"
            "<code>.ncode [промт]</code> - Сгенерировать код (только код)\n"
            "<code>.ncheck вопрос [реплай на файл]</code> - Проанализировать файл\n"
            "<code>.nset key &lt;ключ&gt;</code> - Установить API ключ\n"
            "<code>.nset url &lt;url&gt;</code> - Установить URL API\n"
            "<code>.nset model &lt;модель&gt;</code> - Установить модель\n"
            "<code>.nset temp &lt;0.0-2.0&gt;</code> - Установить температуру\n"
            "<code>.nset prompt &lt;промпт&gt;</code> - Установить системный промпт\n"
            "<code>.nset codeprompt &lt;промпт&gt;</code> - Установить промпт для генерации кода\n"
            "<code>.nset template &lt;шаблон&gt;</code> - Установить шаблон ответа\n"
            "<code>.nset streaming &lt;вкл/выкл&gt;</code> - Включить/выключить потоковую генерацию\n"
            "<code>.nset spoiler &lt;вкл/выкл&gt;</code> - Автоматически сворачивать цитаты (&gt;) в спойлер\n"
            "<code>.nconfig</code> - Показать настройки\n"
            "<code>.nclear</code> - Очистить историю\n"
            "<code>.napis</code> - Список API\n"
            "<code>.nvars</code> - Переменные в промпте\n"
            "<code>.nrvars</code> - Переменные в шаблоне ответа\n"
            "<code>.nhelp</code> - Показать справку\n"
            "<code>.nfile</code> - Отправить последний ответ файлом\n"
        ),
        "_cmd_doc_nchat": "[промт/реплай] - Задать вопрос нейросети",
        "_cmd_doc_ncode": "[промт] - Сгенерировать код (возвращает только код)",
        "_cmd_doc_ncheck": "<вопрос> [реплай на файл] - Проанализировать файл",
        "_cmd_doc_nset": "<параметр> <значение> - Настройка API",
        "_cmd_doc_nconfig": "Показать текущие настройки",
        "_cmd_doc_nclear": "Очистить историю диалога",
        "_cmd_doc_napis": "Показать список API",
        "_cmd_doc_nvars": "Показать переменные для промпта",
        "_cmd_doc_nrvars": "Показать переменные для шаблона ответа",
        "_cmd_doc_nhelp": "Показать справку",
        "_cmd_doc_nfile": "Отправить последний ответ файлом",
    }
    
    strings_ru = {
        "_cls_doc": "Модуль для работы с нейросетями и КУЧЕЙ ненужных для обычного пользователя настроек",
        "_cmd_doc_nchat": "[промт/реплай] - Задать вопрос нейросети",
        "_cmd_doc_ncode": "[промт] - Сгенерировать код (возвращает только код)",
        "_cmd_doc_ncheck": "<вопрос> [реплай на файл] - Проанализировать файл",
        "_cmd_doc_nset": "<параметр> <значение> - Настройка API",
        "_cmd_doc_nconfig": "Показать текущие настройки",
        "_cmd_doc_nclear": "Очистить историю диалога",
        "_cmd_doc_napis": "Показать список API",
        "_cmd_doc_nvars": "Показать переменные для промпта",
        "_cmd_doc_nrvars": "Показать переменные для шаблона ответа",
        "_cmd_doc_nhelp": "Показать справку",
        "_cmd_doc_nfile": "Отправить последний ответ файлом",
    }
    
    API_PRESETS = {
        "openai": {
            "url": "https://api.openai.com/v1/chat/completions",
            "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini"],
            "format": "openai"
        },
        "anthropic": {
            "url": "https://api.anthropic.com/v1/messages",
            "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-3.5-sonnet"],
            "format": "anthropic"
        },
        "gemini": {
            "url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            "models": ["gemini-pro", "gemini-ultra", "gemini-1.5-pro"],
            "format": "gemini"
        },
        "openrouter": {
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "models": ["mistralai/mixtral-8x7b", "google/gemma-7b", "meta-llama/llama-2-70b", "gpt-3.5-turbo", "gpt-4"],
            "format": "openai"
        },
        "groq": {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "models": ["llama2-70b-4096", "mixtral-8x7b-32768", "gemma-7b-it"],
            "format": "openai"
        },
        "deepseek": {
            "url": "https://api.deepseek.com/v1/chat/completions",
            "models": ["deepseek-chat", "deepseek-coder"],
            "format": "openai"
        },
        "local": {
            "url": "http://localhost:1234/v1/chat/completions",
            "models": ["local-model", "llama", "mistral"],
            "format": "openai"
        }
    }
    
    SAMPLE_PROMPTS = {
        "default": "Ты - полезный ассистент. Отвечай точно и по делу.",
        "friendly": "Ты - дружелюбный и общительный помощник. Разговаривай тепло, используй смайлики 😊 и будь позитивным!",
        "formal": "Ты - формальный профессиональный ассистент. Используй официальный стиль, будь точным и лаконичным.",
        "code_expert": "Ты - эксперт по программированию. Отвечай технично, приводи примеры кода, объясняй сложные концепции просто.",
        "creative": "Ты - креативный писатель. Будь изобретательным, используй метафоры, давай развернутые и интересные ответы.",
        "brief": "Ты - помощник, который отвечает кратко и по существу. Не используй лишних слов, только факты.",
        "sarcastic": "Ты - саркастичный помощник с чувством юмора. Отвечай с иронией, но оставайся полезным.",
        "teacher": "Ты - терпеливый учитель. Объясняй понятно, задавай наводящие вопросы, помогай учиться.",
    }
    
    DEFAULT_TEMPLATES = {
        "default": "<blockquote><b>{question}</b></blockquote>\n{answer}\n\n<b>Модель:</b> {model}",
        "simple": "{answer}\n\n— {model}",
        "code": "<blockquote><b>{question}</b></blockquote>\n{answer}\n\n <i>{model}</i>",
        "minimal": "{answer}",
        "detailed": "🗣️ <b>Вопрос:</b> {question}\n\n{answer}\n\n?? <b>Модель:</b> {model}\n⏱️ <b>Время:</b> {thinking_time:.2f} сек.",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "api_key",
                "",
                lambda: "API ключ",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "api_url",
                "https://api.deepseek.com/v1/chat/completions",
                lambda: "URL API эндпоинта",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "model",
                "deepseek-chat",
                lambda: "Название модели",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "temperature",
                0.7,
                lambda: "Температура (креативность) 0.0-2.0",
                validator=loader.validators.Float(minimum=0.0, maximum=2.0),
            ),
            loader.ConfigValue(
                "max_tokens",
                2048,
                lambda: "Максимальное количество токенов",
                validator=loader.validators.Integer(minimum=1, maximum=16384),
            ),
            loader.ConfigValue(
                "system_prompt",
                "Ты - полезный ассистент. Отвечай точно и по делу.",
                lambda: "Системный промпт (можно использовать {username}, {date}, {time}, {model}, {chat_id})",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "code_prompt",
                "Ты - эксперт по программированию. Возвращай только код, без объяснений, без текста до и после кода, без комментариев типа 'Вот код:'. Только чистый код.",
                lambda: "Промпт для генерации кода",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "analysis_prompt",
                "Ты - эксперт по анализу кода и текстовых файлов. Тщательно анализируй содержимое файла и давай развернутые, технически грамотные ответы. Обращай внимание на: синтаксис, структуру, потенциальные ошибки, безопасность, лучшие практики. Форматируй ответ с использованием заголовков и списков.",
                lambda: "Промпт для анализа файлов",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "response_template",
                "<blockquote><b>{question}</b></blockquote>\n{answer}\n\n<b>Модель:</b> {model}",
                lambda: "Шаблон ответа (можно использовать {question}, {answer}, {model}, {thinking_time})",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "timeout",
                300,
                lambda: "Таймаут запроса в секундах (0 = без таймаута)",
                validator=loader.validators.Integer(minimum=0, maximum=600),
            ),
            loader.ConfigValue(
                "use_markdown",
                True,
                lambda: "Использовать Markdown в ответах",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "show_thinking_time",
                True,
                lambda: "Показывать время генерации в шаблоне",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "auto_detect_code",
                True,
                lambda: "Автоопределение кода и форматирование",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "has_file",
                False,
                lambda: "Автоматически отправлять код файлом .py",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "file_min_length",
                500,
                lambda: "Минимальная длина для отправки файлом",
                validator=loader.validators.Integer(minimum=100, maximum=10000),
            ),
            loader.ConfigValue(
                "preserve_history",
                True,
                lambda: "Сохранять историю диалога",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "max_history",
                10,
                lambda: "Максимум сообщений в истории",
                validator=loader.validators.Integer(minimum=1, maximum=50),
            ),
            loader.ConfigValue(
                "code_cleanup",
                True,
                lambda: "Очищать код от лишнего текста",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "smart_file_detection",
                True,
                lambda: "Умное определение файлов для отправки",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "file_clean_header",
                True,
                lambda: "Не добавлять комментарии в файлы",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "max_file_size",
                100000,
                lambda: "Максимальный размер файла для анализа (байт)",
                validator=loader.validators.Integer(minimum=1000, maximum=500000),
            ),
            loader.ConfigValue(
                "streaming",
                True,
                lambda: "Потоковая генерация ответа",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "stream_update_interval",
                1.0,
                lambda: "Интервал обновления при потоковой генерации (секунды)",
                validator=loader.validators.Float(minimum=0.1, maximum=5.0),
            ),
            loader.ConfigValue(
                "auto_spoiler_quotes",
                True,
                lambda: "Автоматически сворачивать цитаты (>) в спойлер",
                validator=loader.validators.Boolean(),
            ),
        )
        
        self.conversations = {}
        self._session = None
        self._last_response = {}
        self._active_requests = {}

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self._session = aiohttp.ClientSession()

    async def on_unload(self):
        if self._session:
            await self._session.close()

    def _get_conversation_key(self, message) -> str:
        chat_id = utils.get_chat_id(message)
        return f"neural_chat_{chat_id}"

    async def _get_conversation_history(self, message) -> list:
        if not self.config["preserve_history"]:
            return [{"role": "system", "content": await self._format_system_prompt(message)}]
        
        key = self._get_conversation_key(message)
        if key not in self.conversations:
            self.conversations[key] = [
                {"role": "system", "content": await self._format_system_prompt(message)}
            ]
        return self.conversations[key]

    async def _add_to_history(self, message, role: str, content: str):
        if not self.config["preserve_history"]:
            return
            
        history = await self._get_conversation_history(message)
        history.append({"role": role, "content": content})
        
        if len(history) > self.config["max_history"]:
            system_msg = history[0]
            history = [system_msg] + history[-(self.config["max_history"]-1):]

    async def _format_system_prompt(self, message) -> str:
        prompt = self.config["system_prompt"]
        
        try:
            me = await self.client.get_me()
            username = me.username or me.first_name or "Пользователь"
            
            from datetime import datetime
            now = datetime.now()
            date = now.strftime("%d.%m.%Y")
            time_str = now.strftime("%H:%M:%S")
            
            replacements = {
                "{username}": username,
                "{date}": date,
                "{time}": time_str,
                "{model}": self.config["model"],
                "{chat_id}": str(utils.get_chat_id(message)),
                "{timestamp}": str(int(time.time())),
            }
            
            for var, value in replacements.items():
                prompt = prompt.replace(var, value)
                
        except Exception:
            pass
            
        return prompt

    async def _format_code_prompt(self, message) -> str:
        prompt = self.config["code_prompt"]
        
        try:
            me = await self.client.get_me()
            username = me.username or me.first_name or "Пользователь"
            
            from datetime import datetime
            now = datetime.now()
            date = now.strftime("%d.%m.%Y")
            time_str = now.strftime("%H:%M:%S")
            
            replacements = {
                "{username}": username,
                "{date}": date,
                "{time}": time_str,
                "{model}": self.config["model"],
                "{chat_id}": str(utils.get_chat_id(message)),
                "{timestamp}": str(int(time.time())),
            }
            
            for var, value in replacements.items():
                prompt = prompt.replace(var, value)
                
        except Exception:
            pass
            
        return prompt

    async def _format_analysis_prompt(self, message, file_type: str, file_name: str) -> str:
        prompt = self.config["analysis_prompt"]
        
        try:
            me = await self.client.get_me()
            username = me.username or me.first_name or "Пользователь"
            
            from datetime import datetime
            now = datetime.now()
            date = now.strftime("%d.%m.%Y")
            time_str = now.strftime("%H:%M:%S")
            
            replacements = {
                "{username}": username,
                "{date}": date,
                "{time}": time_str,
                "{model}": self.config["model"],
                "{chat_id}": str(utils.get_chat_id(message)),
                "{timestamp}": str(int(time.time())),
                "{file_type}": file_type,
                "{file_name}": file_name,
            }
            
            for var, value in replacements.items():
                prompt = prompt.replace(var, value)
                
        except Exception:
            pass
            
        return prompt

    async def _detect_api_format(self, url: str) -> Tuple[str, Dict[str, Any]]:
        url_lower = url.lower()
        
        for preset_name, preset in self.API_PRESETS.items():
            if preset["url"] in url or preset_name in url_lower:
                return preset["format"], preset
        
        if "{model}" in url:
            return "gemini", self.API_PRESETS.get("gemini", self.API_PRESETS["openai"])
        
        if "openai.com" in url_lower or "openai" in url_lower:
            return "openai", self.API_PRESETS["openai"]
        elif "anthropic.com" in url_lower or "anthropic" in url_lower:
            return "anthropic", self.API_PRESETS["anthropic"]
        elif "googleapis.com" in url_lower or "google" in url_lower:
            return "gemini", self.API_PRESETS["gemini"]
        elif "openrouter.ai" in url_lower or "openrouter" in url_lower:
            return "openai", self.API_PRESETS["openrouter"]
        elif "groq.com" in url_lower or "groq" in url_lower:
            return "openai", self.API_PRESETS["groq"]
        elif "deepseek.com" in url_lower or "deepseek" in url_lower:
            return "openai", self.API_PRESETS["deepseek"]
        
        return "openai", self.API_PRESETS["openai"]

    async def _prepare_openai_payload(self, messages: list, streaming: bool = False, **kwargs) -> dict:
        logger.info(f"Preparing OpenAI payload with model: {self.config['model']}, streaming: {streaming}")
        payload = {
            "model": self.config["model"],
            "messages": messages,
            "temperature": self.config["temperature"],
            "max_tokens": self.config["max_tokens"],
            "stream": streaming,
        }
        
        if "deepseek" in self.config["model"].lower() or "deepseek.com" in self.config["api_url"].lower():
            payload["stream"] = streaming
            if self.config["max_tokens"] < 4096:
                payload["max_tokens"] = 4096
        
        return payload

    async def _prepare_anthropic_payload(self, messages: list, **kwargs) -> dict:
        logger.info(f"Preparing Anthropic payload with model: {self.config['model']}")
        anthropic_messages = []
        system_content = ""
        
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                anthropic_messages.append(msg)
        
        if not system_content:
            system_content = self.config["system_prompt"]
        
        return {
            "model": self.config["model"],
            "messages": anthropic_messages,
            "system": system_content,
            "max_tokens": self.config["max_tokens"],
            "temperature": self.config["temperature"],
        }

    async def _prepare_gemini_payload(self, messages: list, **kwargs) -> dict:
        logger.info(f"Preparing Gemini payload with model: {self.config['model']}")
        contents = []
        
        for msg in messages:
            role = "user" if msg["role"] in ["user", "system"] else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        return {
            "contents": contents,
            "generationConfig": {
                "temperature": self.config["temperature"],
                "maxOutputTokens": self.config["max_tokens"],
            }
        }

    async def _call_api_streaming(self, messages: list, status_msg, chat_id: int) -> tuple[Optional[str], Optional[float], Optional[str]]:
        if not self.config["api_key"]:
            await utils.answer(message, "❌ <b>API ключ не установлен!</b>\nИспользуйте: <code>.nset key ваш_ключ</code>")
            return None, None, "API ключ не установлен"
        
        if not self.config["api_url"]:
            await utils.answer(message, "❌ <b>URL API не установлен!</b>\nИспользуйте: <code>.nset url ваш_url</code>")
            return None, None, "URL API не установлен"

        api_format, api_preset = await self._detect_api_format(self.config["api_url"])
        start_time = time.time()
        
        logger.info(f"Calling API with streaming: {self.config['api_url']}")
        logger.info(f"API Format: {api_format}")
        logger.info(f"Model: {self.config['model']}")

        url = self.config["api_url"]
        
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.config["api_key"]:
            headers["Authorization"] = f"Bearer {self.config['api_key']}"
        
        if api_format in ["anthropic", "gemini"]:
            return None, None, f"Streaming для {api_format} API не реализован"
        else:
            payload = await self._prepare_openai_payload(messages, streaming=True)
        
        logger.info(f"Streaming request to: {url}")
        
        full_response = ""
        model_used = self.config["model"]
        last_update_time = time.time()
        update_interval = self.config["stream_update_interval"]
        
        try:
            timeout = aiohttp.ClientTimeout(
                connect=30,
                sock_read=None,
                total=None
            ) if self.config["timeout"] == 0 else aiohttp.ClientTimeout(total=self.config["timeout"])
            
            async with self._session.post(
                url,
                headers=headers,
                json=payload,
                timeout=timeout
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"API error {response.status}: {error_text[:500]}")
                    return None, None, f"HTTP {response.status}: {error_text[:200]}"
                
                buffer = ""
                async for line in response.content:
                    if line:
                        line = line.decode('utf-8').strip()
                        
                        if not line or line == "data: [DONE]":
                            continue
                        
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                
                                choices = data.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content = delta.get("content", "")
                                    
                                    if content:
                                        full_response += content
                                        buffer += content
                                        
                                        if data.get("model"):
                                            model_used = data.get("model")
                                    
                                    finish_reason = choices[0].get("finish_reason")
                                    if finish_reason:
                                        logger.info(f"Stream finished with reason: {finish_reason}")
                                        break
                                
                                current_time = time.time()
                                if current_time - last_update_time >= update_interval and buffer:
                                    try:
                                        await utils.answer(
                                            status_msg,
                                            f"🔄 <b>Генерирую ответ...</b>\n"
                                            f"<i>Модель: {model_used}</i>\n"
                                            f"<i>Получено символов: {len(full_response)}</i>\n"
                                            f"<i>Последние символы:</i>\n<code>{buffer[-200:]}</code>"
                                        )
                                        buffer = ""
                                        last_update_time = current_time
                                    except Exception as e:
                                        logger.error(f"Error updating status: {e}")
                                
                            except json.JSONDecodeError as e:
                                logger.error(f"JSON decode error in stream: {e}, line: {line}")
                                continue
                
                thinking_time = time.time() - start_time
                logger.info(f"Streaming completed. Total time: {thinking_time:.2f}s, chars: {len(full_response)}")
                
                if not full_response:
                    logger.warning("Empty response from streaming API")
                    return None, None, "Пустой ответ от нейросети"
                
                return full_response, thinking_time, model_used
                
        except asyncio.TimeoutError:
            logger.error("Streaming request timeout")
            return None, None, "Таймаут при потоковой генерации"
        except aiohttp.ClientError as e:
            logger.error(f"Client error in streaming: {e}")
            return None, None, f"Ошибка соединения при потоковой генерации: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in streaming: {e}")
            return None, None, f"Ошибка при потоковой генерации: {str(e)}"

    async def _call_api_regular(self, messages: list, is_code_request: bool = False, is_analysis: bool = False) -> tuple[Optional[str], Optional[float], Optional[str]]:
        if not self.config["api_url"]:
            await utils.answer(message, "❌ <b>URL API не установлен!</b>\nИспользуйте: <code>.nset url ваш_url</code>")
            return None, None, "URL API не установлен"

        api_format, api_preset = await self._detect_api_format(self.config["api_url"])
        start_time = time.time()
        
        logger.info(f"Calling API regularly: {self.config['api_url']}")
        logger.info(f"API Format: {api_format}")
        logger.info(f"Model: {self.config['model']}")

        url = self.config["api_url"]
        
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.config["api_key"]:
            headers["Authorization"] = f"Bearer {self.config['api_key']}"
        
        if api_format == "anthropic":
            payload = await self._prepare_anthropic_payload(messages)
        elif api_format == "gemini":
            payload = await self._prepare_gemini_payload(messages)
        else:
            payload = await self._prepare_openai_payload(messages, streaming=False)
        
        logger.info(f"Regular request to: {url}")
        
        try:
            timeout_value = 300 if self.config["timeout"] == 0 else self.config["timeout"]
            timeout = aiohttp.ClientTimeout(total=timeout_value)
            logger.info(f"Making request with timeout: {timeout_value}s")
            
            async with self._session.post(
                url,
                headers=headers,
                json=payload,
                timeout=timeout
            ) as response:
                
                response_time = time.time() - start_time
                logger.info(f"Response status: {response.status}")
                logger.info(f"Response time: {response_time:.2f}s")
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"API error {response.status}: {error_text[:500]}")
                    return None, None, f"HTTP {response.status}: {error_text[:200]}"
                
                response_text = await response.text()
                logger.info(f"Response text (first 500 chars): {response_text[:500]}")
                
                try:
                    if not response_text.strip():
                        logger.error("Empty response from API")
                        return None, None, "Пустой ответ от API"
                    
                    data = json.loads(response_text)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    logger.error(f"Response text: {response_text[:500]}")
                    return None, None, f"Некорректный JSON от API: {str(e)}"
                
                thinking_time = time.time() - start_time
                logger.info(f"Total processing time: {thinking_time:.2f}s")

                content = ""
                model_used = self.config["model"]
                
                if api_format == "anthropic":
                    if isinstance(data, dict):
                        content = data.get("content", [{}])[0].get("text", "")
                        model_used = data.get("model", self.config["model"])
                        
                elif api_format == "gemini":
                    if isinstance(data, dict):
                        candidates = data.get("candidates", [])
                        if candidates and isinstance(candidates, list) and candidates[0]:
                            candidate = candidates[0]
                            content_parts = candidate.get("content", {}).get("parts", [])
                            if content_parts and isinstance(content_parts, list) and content_parts[0]:
                                content = content_parts[0].get("text", "")
                        
                else:
                    if isinstance(data, dict):
                        choices = data.get("choices", [])
                        if choices and isinstance(choices, list) and choices[0]:
                            first_choice = choices[0]
                            if isinstance(first_choice, dict):
                                message = first_choice.get("message", {})
                                if isinstance(message, dict):
                                    content = message.get("content", "")
                        
                        model_used = data.get("model", self.config["model"])
                
                logger.info(f"Response model: {model_used}")
                
                if not content:
                    logger.warning(f"Empty content in response. Full response: {json.dumps(data, indent=2)[:1000]}")
                    return None, None, "Пустой ответ от нейросети"

                if is_code_request and self.config["code_cleanup"]:
                    content = self._clean_code_response(content)

                logger.info(f"Response length: {len(content)} characters")
                return content, thinking_time, model_used

        except asyncio.TimeoutError:
            logger.error(f"Request timeout after {timeout_value}s")
            return None, None, "Таймаут запроса. Попробуйте включить потоковую генерацию (.nset streaming true) или увеличьте таймаут."
        except aiohttp.ClientError as e:
            logger.error(f"Client error: {e}")
            return None, None, f"Ошибка соединения: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None, None, str(e)

    async def _call_api(self, messages: list, is_code_request: bool = False, is_analysis: bool = False) -> tuple[Optional[str], Optional[float], Optional[str]]:
        if self.config["streaming"] and not is_analysis:
            api_format, _ = await self._detect_api_format(self.config["api_url"])
            if api_format in ["anthropic", "gemini"]:
                logger.info(f"API {api_format} не поддерживает streaming, используем обычный режим")
                return await self._call_api_regular(messages, is_code_request, is_analysis)
            else:
                logger.info("Using streaming API call")
                return "STREAMING_REQUIRED", 0.0, self.config["model"]
        else:
            logger.info("Using regular API call")
            return await self._call_api_regular(messages, is_code_request, is_analysis)

    def _clean_code_response(self, text: str) -> str:
        patterns_to_remove = [
            r'^.*?(вот код:|код:|пример:|решение:|ответ:|смотрите:|изучите:|далее:|ниже:|полный код:|полный пример:).*?\n',
            r'^.*?(here.*?code:|code:|solution:|example:|answer:|full code:|complete code:).*?\n',
            r'```.*?\n',
            r'```$',
            r'^[\s\-*]*$',
            r'^#.*?$',
        ]
        
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        text = text.strip()
        
        lines = text.split('\n')
        code_keywords = ['import ', 'from ', 'def ', 'class ', 'async ', '@', 'print(', 'return ', 'if ', 'for ', 'while ']
        
        has_code_keywords = any(any(keyword in line for keyword in code_keywords) for line in lines)
        
        if has_code_keywords and len(lines) >= 2:
            return text
        
        return text

    def _wrap_spoiler_quotes(self, text: str) -> str:
        if not self.config["auto_spoiler_quotes"]:
            return text
            
        lines = text.split('\n')
        in_quote_block = False
        quote_lines = []
        result_lines = []
        
        for line in lines:
            line_stripped = line.lstrip()
            if line_stripped.startswith('>'):
                if not in_quote_block:
                    in_quote_block = True
                    quote_lines = []
                clean_line = line_stripped[1:].lstrip() if len(line_stripped) > 1 else ''
                quote_lines.append(clean_line)
            else:
                if in_quote_block:
                    if quote_lines:
                        quote_text = '\n'.join(quote_lines)
                        result_lines.append(f'<blockquote expandable>{utils.escape_html(quote_text)}</blockquote>')
                    in_quote_block = False
                result_lines.append(line)
        
        if in_quote_block and quote_lines:
            quote_text = '\n'.join(quote_lines)
            result_lines.append(f'<blockquote expandable>{utils.escape_html(quote_text)}</blockquote>')
        
        return '\n'.join(result_lines)

    def _detect_file_type(self, file_name: str, content: str = "") -> Tuple[str, str]:
        file_name_lower = file_name.lower()
        content_lower = content.lower() if content else ""
        
        ext_patterns = {
            '.py': ('Python скрипт', 'python'),
            '.plugin': ('Exteragram плагин', 'python'),
            '.js': ('JavaScript файл', 'javascript'),
            '.jsx': ('React JSX файл', 'javascript'),
            '.ts': ('TypeScript файл', 'typescript'),
            '.tsx': ('React TypeScript файл', 'typescript'),
            '.html': ('HTML документ', 'html'),
            '.htm': ('HTML документ', 'html'),
            '.css': ('CSS стили', 'css'),
            '.scss': ('SCSS стили', 'scss'),
            '.less': ('LESS стили', 'less'),
            '.json': ('JSON данные', 'json'),
            '.sql': ('SQL скрипт', 'sql'),
            '.txt': ('Текстовый файл', 'text'),
            '.md': ('Markdown документ', 'markdown'),
            '.yml': ('YAML файл', 'yaml'),
            '.yaml': ('YAML файл', 'yaml'),
            '.xml': ('XML документ', 'xml'),
            '.csv': ('CSV данные', 'csv'),
            '.ini': ('Конфигурационный файл', 'ini'),
            '.cfg': ('Конфигурационный файл', 'cfg'),
            '.conf': ('Конфигурационный файл', 'conf'),
            '.sh': ('Bash скрипт', 'bash'),
            '.bash': ('Bash скрипт', 'bash'),
            '.bat': ('Batch файл', 'batch'),
            '.ps1': ('PowerShell скрипт', 'powershell'),
            '.php': ('PHP скрипт', 'php'),
            '.java': ('Java файл', 'java'),
            '.cpp': ('C++ файл', 'cpp'),
            '.c': ('C файл', 'c'),
            '.cs': ('C# файл', 'csharp'),
            '.go': ('Go файл', 'go'),
            '.rs': ('Rust файл', 'rust'),
            '.rb': ('Ruby файл', 'ruby'),
            '.pl': ('Perl скрипт', 'perl'),
            '.lua': ('Lua скрипт', 'lua'),
            '.swift': ('Swift файл', 'swift'),
            '.kt': ('Kotlin файл', 'kotlin'),
            '.dart': ('Dart файл', 'dart'),
            '.r': ('R скрипт', 'r'),
            '.m': ('Objective-C файл', 'objectivec'),
        }
        
        for ext, (desc, lang) in ext_patterns.items():
            if file_name_lower.endswith(ext):
                return desc, lang
        
        if content:
            if ('@loader.tds' in content or 
                'class.*?Module.*?loader.Module' in content or
                '__version__' in content):
                return ('Hikka плагин', 'python')
            
            python_keywords = [
                'import ', 'from ', 'def ', 'class ', 'async def ',
                '@', 'self.', 'super()', '__init__', 'print('
            ]
            if any(keyword in content for keyword in python_keywords):
                return ('Python скрипт', 'python')
            
            js_keywords = [
                'function ', 'const ', 'let ', 'var ', '=>', 'console.log',
                'document.', 'window.', 'export ', 'import ', 'require('
            ]
            if any(keyword in content for keyword in js_keywords):
                return ('JavaScript файл', 'javascript')
            
            html_patterns = [
                r'<!DOCTYPE html>', r'<html', r'<head>', r'<body>',
                r'<div', r'<span', r'<p>', r'<h1>'
            ]
            if any(re.search(pattern, content_lower) for pattern in html_patterns):
                return ('HTML документ', 'html')
            
            if (content.strip().startswith('{') and content.strip().endswith('}')) or \
               (content.strip().startswith('[') and content.strip().endswith(']')):
                try:
                    json.loads(content)
                    return ('JSON данные', 'json')
                except:
                    pass
            
            if content_lower.startswith('<?xml'):
                return ('XML документ', 'xml')
            
            md_patterns = [r'^# ', r'^## ', r'\[.*?\]\(.*?\)', r'!\[.*?\]\(.*?\)']
            md_count = sum(1 for pattern in md_patterns if re.search(pattern, content, re.MULTILINE))
            if md_count >= 2:
                return ('Markdown документ', 'markdown')
        
        return ('Текстовый файл', 'text')

    def _analyze_plugin_structure(self, content: str) -> Dict[str, Any]:
        analysis = {
            "has_version": bool(re.search(r'__version__\s*=', content)),
            "has_meta": bool(re.search(r'meta developer:', content, re.IGNORECASE)),
            "has_loader_decorator": bool(re.search(r'@loader\.tds', content)),
            "has_module_class": bool(re.search(r'class.*?\(.*?loader\.Module', content)),
            "has_strings": bool(re.search(r'strings\s*=', content)),
            "has_commands": bool(re.search(r'@loader\.command', content)),
            "has_config": bool(re.search(r'loader\.ModuleConfig', content)),
            "has_client_ready": bool(re.search(r'async def client_ready', content)),
            "has_on_unload": bool(re.search(r'async def on_unload', content)),
        }
        
        structure_score = sum(1 for key, value in analysis.items() if value)
        
        warnings = []
        
        if "import asyncio" not in content and "import aiohttp" not in content:
            warnings.append("Отсутствуют важные импорты (asyncio, aiohttp)")
        
        if '"""' not in content and "'''" not in content:
            warnings.append("Отсутствует документация класса/модуля")
        
        if "eval(" in content or "exec(" in content:
            warnings.append("⚠️ Обнаружены потенциально опасные функции eval/exec")
        
        if "os.system" in content or "subprocess" in content:
            warnings.append("⚠️ Обнаружены системные вызовы")
        
        if content.count("try:") < 1 or content.count("except") < 1:
            warnings.append("Мало обработчиков ошибок")
        
        analysis["structure_score"] = structure_score
        analysis["warnings"] = warnings
        analysis["is_valid_plugin"] = structure_score >= 5
        
        return analysis

    async def _get_file_content(self, message) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        reply = await message.get_reply_message()
        
        if not reply:
            return None, None, "Нет реплая на сообщение с файлом"
        
        if not reply.document:
            return None, None, "В реплае нет файла"
        
        doc = reply.document
        
        if doc.size > self.config["max_file_size"]:
            return None, None, f"Файл слишком большой ({doc.size} байт > {self.config['max_file_size']} байт)"
        
        try:
            file = await reply.download_media(bytes)
            if not file:
                return None, None, "Не удалось скачать файл"
            
            try:
                content = file.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    content = file.decode('utf-8-sig')
                except UnicodeDecodeError:
                    try:
                        content = file.decode('cp1251')
                    except UnicodeDecodeError:
                        try:
                            content = file.decode('latin-1', errors='ignore')
                        except Exception:
                            return None, None, "Не удалось декодировать файл (не текстовый формат?)"
            
            file_name = reply.file.name or "unknown"
            return content, file_name, None
            
        except Exception as e:
            logger.error(f"Error getting file content: {e}")
            return None, None, f"Ошибка при получении файла: {str(e)}"

    def _detect_language(self, text: str) -> Tuple[bool, str]:
        text_lower = text.lower()
        lines = text.split('\n')
        
        patterns = {
            'python': [
                (r'^import\s+\w+', 3),
                (r'^from\s+\w+\s+import', 3),
                (r'def\s+\w+\s*\(', 2),
                (r'class\s+\w+\s*\(', 2),
                (r'async\s+def', 2),
                (r'@\w+\.', 2),
                (r'\.py\b', 1),
                (r'loader\.Module', 5),
                (r'@loader\.', 5),
                (r'strings\s*=\s*\{', 3),
                (r'__version__\s*=\s*\(', 3),
                (r'self\.', 2),
            ],
            'javascript': [
                (r'function\s+\w+\s*\(', 2),
                (r'const\s+\w+\s*=', 2),
                (r'let\s+\w+\s*=', 2),
                (r'var\s+\w+\s*=', 2),
                (r'console\.log', 1),
                (r'\.js\b', 1),
                (r'document\.', 1),
                (r'window\.', 1),
                (r'export\s+', 2),
                (r'import\s+', 2),
                (r'require\(', 2),
                (r'\.then\(', 1),
                (r'\.catch\(', 1),
            ],
            'html': [
                (r'<!DOCTYPE html>', 3),
                (r'<html.*?>', 2),
                (r'<head>', 2),
                (r'<body>', 2),
                (r'<div.*?>', 1),
                (r'<\/\w+>', 1),
                (r'<\w+.*?>', 1),
                (r'<script>', 2),
                (r'<style>', 2),
            ],
            'css': [
                (r'\w+\s*\{.*?\}', 2),
                (r'@media', 2),
                (r'\.\w+\s*\{', 2),
                (r'#\w+\s*\{', 2),
                (r':\s*{', 1),
                (r'}\s*$', 1),
                (r'font-size:', 1),
                (r'color:', 1),
            ],
            'bash': [
                (r'^#!/bin/(bash|sh)', 3),
                (r'^\$\s', 2),
                (r'^\w+=\".*?\"', 2),
                (r'^echo\s+', 1),
                (r'^cd\s+', 1),
                (r'^ls\b', 1),
                (r'^mkdir\b', 1),
                (r'^sudo\b', 1),
            ],
            'sql': [
                (r'SELECT\s+.+?\s+FROM', 3),
                (r'INSERT\s+INTO', 3),
                (r'UPDATE\s+\w+\s+SET', 3),
                (r'CREATE\s+TABLE', 3),
                (r'DROP\s+TABLE', 2),
                (r'WHERE\s+', 2),
                (r'JOIN\s+', 2),
                (r'GROUP BY', 2),
                (r'ORDER BY', 2),
            ],
            'json': [
                (r'^\s*\{', 2),
                (r'^\s*\[', 2),
                (r'\".*?\"\s*:', 1),
                (r',\s*$', 1),
            ],
        }
        
        scores = {lang: 0 for lang in patterns}
        
        for i, line in enumerate(lines[:50]):
            for lang, lang_patterns in patterns.items():
                for pattern, weight in lang_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        scores[lang] += weight
                        if i < 5:
                            scores[lang] += 1
        
        if '```' in text:
            lang_matches = re.findall(r'```(\w+)', text)
            for match in lang_matches:
                if match in scores:
                    scores[match] += 5
        
        ext_patterns = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.sh': 'bash',
            '.sql': 'sql',
            '.json': 'json',
            '.txt': 'text',
        }
        
        for ext, lang in ext_patterns.items():
            if ext in text:
                scores[lang] += 2
        
        max_score = max(scores.values())
        if max_score > 5:
            best_lang = max(scores, key=scores.get)
            return True, best_lang
        
        has_braces = '{' in text and '}' in text
        has_semicolons = text.count(';') > text.count('\n') * 0.3
        has_equals = text.count('=') > text.count('\n') * 0.5
        
        if has_braces and (has_semicolons or has_equals):
            return True, 'javascript'
        
        return False, 'text'

    def _is_likely_code_file(self, text: str) -> bool:
        if not self.config["smart_file_detection"]:
            return len(text) > self.config["file_min_length"]
        
        lines = text.strip().split('\n')
        
        if len(lines) < 3:
            return False
        
        code_indicators = [
            ('import ', 2),
            ('def ', 2),
            ('class ', 2),
            ('function ', 2),
            ('<?php', 3),
            ('<html', 2),
            ('SELECT ', 2),
            ('CREATE ', 2),
            ('{', 1),
            ('}', 1),
            ('=', 0.5),
            ('(', 0.5),
            (')', 0.5),
        ]
        
        score = 0
        total_lines = min(len(lines), 50)
        
        for i, line in enumerate(lines[:50]):
            line_lower = line.lower().strip()
            
            for indicator, weight in code_indicators:
                if indicator in line_lower:
                    score += weight
                    if i < 10:
                        score += 1
        
        normalized_score = score / total_lines
        
        if '```' in text:
            normalized_score += 1
        
        is_code = normalized_score > 0.8 or len(text) > 1000
        
        return is_code and len(text) > self.config["file_min_length"]

    def _format_code_blocks(self, text: str) -> str:
        if not self.config["auto_detect_code"]:
            return text
            
        lines = text.split('\n')
        result = []
        in_code_block = False
        current_block = []
        current_lang = ''
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if line.strip().startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    lang_match = line.strip()[3:].strip()
                    current_lang = lang_match if lang_match else 'text'
                    current_block = []
                else:
                    in_code_block = False
                    if current_block:
                        block_content = '\n'.join(current_block)
                        if current_lang == 'text':
                            _, detected_lang = self._detect_language(block_content)
                            current_lang = detected_lang if detected_lang else 'text'
                        
                        result.append(f'<pre><code class="language-{current_lang}">{utils.escape_html(block_content)}</code></pre>')
                    current_block = []
                    current_lang = ''
            elif in_code_block:
                current_block.append(line)
            else:
                result.append(line)
            
            i += 1
        
        if in_code_block and current_block:
            block_content = '\n'.join(current_block)
            if current_lang == 'text':
                _, detected_lang = self._detect_language(block_content)
                current_lang = detected_lang if detected_lang else 'text'
            result.append(f'<pre><code class="language-{current_lang}">{utils.escape_html(block_content)}</code></pre>')
        
        final_text = '\n'.join(result)
        is_code, lang = self._detect_language(text)
        if is_code and not in_code_block and 'pre><code' not in final_text:
            if len(text.split('\n')) > 3:
                return f'<pre><code class="language-{lang}">{utils.escape_html(text)}</code></pre>'
        
        return final_text

    def _format_response(self, prompt: str, response: str, model: str, thinking_time: float, message, is_code: bool = False, is_analysis: bool = False) -> str:
        escaped_prompt = utils.escape_html(prompt)
        raw_response = response
        
        formatted_response = raw_response
        
        if not is_code and self.config["use_markdown"]:
            formatted_response = self._format_code_blocks(raw_response)
            formatted_response = self._convert_markdown(formatted_response)
        elif is_code:
            is_code_block, lang = self._detect_language(raw_response)
            if is_code_block:
                formatted_response = f'<pre><code class="language-{lang}">{utils.escape_html(raw_response)}</code></pre>'
            else:
                formatted_response = utils.escape_html(raw_response)
        else:
            formatted_response = utils.escape_html(raw_response)
        
        if self.config["auto_spoiler_quotes"]:
            formatted_response = self._wrap_spoiler_quotes(formatted_response)
        
        chat_id = utils.get_chat_id(message)
        self._last_response[chat_id] = {
            'prompt': prompt,
            'response': raw_response,
            'formatted_response': formatted_response,
            'model': model,
            'thinking_time': thinking_time,
            'timestamp': time.time(),
            'is_code': is_code,
            'is_analysis': is_analysis
        }
        
        template = self.config["response_template"]
        
        variables = {
            "{question}": escaped_prompt,
            "{answer}": formatted_response,
            "{model}": model,
            "{thinking_time}": f"{thinking_time:.2f}",
            "{time}": f"{thinking_time:.2f} сек.",
        }
        
        for var, value in variables.items():
            template = template.replace(var, value)
        
        if (self.config["has_file"] and 
            self._is_likely_code_file(raw_response)):
            template += f'\n\n<i>💾 Используй <code>.nfile</code> чтобы получить ответ файлом</i>'
        
        return template

    def _convert_markdown(self, text: str) -> str:
        text = re.sub(r'^### (.+?)$', r'<b><i>\1</i></b>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+?)$', r'<b>\1</b>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.+?)$', r'<b><u>\1</u></b>', text, flags=re.MULTILINE)
        
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        
        text = re.sub(r'~~(.+?)~~', r'<s>\1</s>', text)
        
        text = re.sub(r'\[(.+?)\]\((https?://.+?)\)', r'<a href="\2">\1</a>', text)
        
        lines = text.split('\n')
        result = []
        in_pre_block = False
        
        for line in lines:
            if '<pre><code' in line:
                in_pre_block = True
                result.append(line)
            elif '</code></pre>' in line:
                in_pre_block = False
                result.append(line)
            elif in_pre_block:
                result.append(line)
            else:
                line = re.sub(r'(?<!["\'])`([^`\n]+?)`(?!["\'])', r'<code>\1</code>', line)
                result.append(line)
        
        return '\n'.join(result)

    async def _send_as_file(self, message, response_data: dict):
        chat_id = utils.get_chat_id(message)
        
        code = response_data['response']
        
        if self.config["code_cleanup"] and response_data.get('is_code', False):
            code = self._clean_code_response(code)
        
        is_code, lang = self._detect_language(code)
        extensions = {
            'python': '.py',
            'javascript': '.js',
            'html': '.html',
            'css': '.css',
            'bash': '.sh',
            'sql': '.sql',
            'json': '.json',
            'text': '.txt',
        }
        ext = extensions.get(lang, '.txt')
        
        timestamp = int(time.time())
        filename = f"response_{timestamp}{ext}"
        
        if self.config["file_clean_header"]:
            content = code
        else:
            header = f"""# Ответ нейросети
# Модель: {response_data['model']}
# Время генерации: {response_data['thinking_time']:.2f} сек.
# Промпт: {response_data['prompt']}
# Дата: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(response_data['timestamp']))}

"""
            content = header + code
        
        file = io.BytesIO(content.encode('utf-8'))
        file.name = filename
        
        caption = (
            f"📁 <b>Файл от {response_data['model']}</b>\n"
            f"⏱️ <b>Время:</b> {response_data['thinking_time']:.2f} сек.\n"
            f"📝 <b>Промпт:</b> {response_data['prompt'][:100]}..."
        )
        
        await utils.answer_file(
            message,
            file,
            caption=caption
        )

    @loader.command(
        ru_doc="[промт/реплай] - Задать вопрос нейросети"
    )
    async def nchatcmd(self, message):
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        
        if args:
            prompt = args
        elif reply and (reply.text or reply.message):
            prompt = reply.text or reply.message
        else:
            await utils.answer(message, self.strings["no_args"])
            return

        if not self.config["api_key"]:
            await utils.answer(message, "❌ <b>API ключ не установлен!</b>\nИспользуйте: <code>.nset key ваш_ключ</code>")
            return
        
        if not self.config["api_url"]:
            await utils.answer(message, "❌ <b>URL API не установлен!</b>\nИспользуйте: <code>.nset url ваш_url</code>")
            return

        history = await self._get_conversation_history(message)
        
        await self._add_to_history(message, "user", prompt)

        model_display = self.config["model"]
        status_msg = await utils.answer(
            message, 
            self.strings["generating"].format(model=model_display)
        )

        if self.config["streaming"]:
            logger.info("Starting streaming generation")
            response, thinking_time, model_used = await self._call_api_streaming(
                history + [{"role": "user", "content": prompt}],
                status_msg,
                utils.get_chat_id(message)
            )
        else:
            logger.info("Starting regular generation")
            response, thinking_time, model_used = await self._call_api_regular(
                history + [{"role": "user", "content": prompt}],
                is_code_request=False
            )

        if response is None:
            error_msg = f"❌ <b>Ошибка:</b>\n<code>{model_used}</code>"
            if "таймаут" in str(model_used).lower():
                error_msg += f"\n\n💡 <b>Совет:</b> Попробуйте включить потоковую генерацию:\n<code>.nset streaming true</code>"
            await utils.answer(status_msg, error_msg)
            return

        await self._add_to_history(message, "assistant", response)

        formatted = self._format_response(prompt, response, model_used, thinking_time, message, is_code=False)
        
        if (self.config["has_file"] and 
            self._is_likely_code_file(response)):
            
            chat_id = utils.get_chat_id(message)
            response_data = {
                'prompt': prompt,
                'response': response,
                'model': model_used,
                'thinking_time': thinking_time,
                'timestamp': time.time(),
                'is_code': True
            }
            
            await self._send_as_file(message, response_data)
            await status_msg.delete()
        else:
            await utils.answer(status_msg, formatted)

    @loader.command(
        ru_doc="[промт] - Сгенерировать код (возвращает только код)"
    )
    async def ncodecmd(self, message):
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "❌ <b>Введите промпт для генерации кода!</b>")
            return

        if not self.config["api_key"] or not self.config["api_url"]:
            await utils.answer(message, self.strings["no_api_config"])
            return

        model_display = self.config["model"]
        status_msg = await utils.answer(
            message, 
            self.strings["generating_code"].format(model=model_display)
        )

        system_prompt = await self._format_code_prompt(message)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": args}
        ]
        
        if self.config["streaming"]:
            response, thinking_time, model_used = await self._call_api_streaming(
                messages,
                status_msg,
                utils.get_chat_id(message)
            )
        else:
            response, thinking_time, model_used = await self._call_api_regular(
                messages,
                is_code_request=True
            )

        if response is None:
            error_msg = f"❌ <b>Ошибка:</b>\n<code>{model_used}</code>"
            if "таймаут" in str(model_used).lower():
                error_msg += f"\n\n💡 <b>Совет:</b> Попробуйте включить потоковую генерацию:\n<code>.nset streaming true</code>"
            await utils.answer(status_msg, error_msg)
            return

        formatted = self._format_response(args, response, model_used, thinking_time, message, is_code=True)
        
        if (self.config["has_file"] and 
            self._is_likely_code_file(response)):
            
            chat_id = utils.get_chat_id(message)
            response_data = {
                'prompt': args,
                'response': response,
                'model': model_used,
                'thinking_time': thinking_time,
                'timestamp': time.time(),
                'is_code': True
            }
            
            await self._send_as_file(message, response_data)
            await status_msg.delete()
        else:
            await utils.answer(status_msg, formatted)

    @loader.command(
        ru_doc="<вопрос> [реплай на файл] - Проанализировать файл"
    )
    async def ncheckcmd(self, message):
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, self.strings["analysis_no_question"])
            return
        
        if not self.config["api_key"] or not self.config["api_url"]:
            await utils.answer(message, self.strings["no_api_config"])
            return
        
        file_content, file_name, error = await self._get_file_content(message)
        
        if error:
            await utils.answer(message, f"❌ <b>Ошибка:</b> {error}")
            return
        
        if not file_content:
            await utils.answer(message, self.strings["no_file_content"])
            return
        
        file_desc, file_lang = self._detect_file_type(file_name, file_content)
        logger.info(f"File type detected: {file_desc} ({file_lang}) for file: {file_name}")
        
        model_display = self.config["model"]
        status_msg = await utils.answer(
            message,
            self.strings["file_analysis"].format(
                file_type=file_desc,
                model=model_display
            )
        )
        
        system_prompt = await self._format_analysis_prompt(message, file_desc, file_name)
        
        analysis_context = ""
        if file_lang == 'python' and ('.plugin' in file_name.lower() or 'loader.Module' in file_content):
            plugin_analysis = self._analyze_plugin_structure(file_content)
            
            analysis_context = f"\n\n**Анализ структуры плагина:**\n"
            analysis_context += f"- Версия: {'✅ Есть' if plugin_analysis['has_version'] else '❌ Нет'}\n"
            analysis_context += f"- Метаданные: {'✅ Есть' if plugin_analysis['has_meta'] else '❌ Нет'}\n"
            analysis_context += f"- Декоратор загрузчика: {'✅ Есть' if plugin_analysis['has_loader_decorator'] else '❌ Нет'}\n"
            analysis_context += f"- Класс модуля: {'✅ Есть' if plugin_analysis['has_module_class'] else '❌ Нет'}\n"
            analysis_context += f"- Строки: {'✅ Есть' if plugin_analysis['has_strings'] else '❌ Нет'}\n"
            analysis_context += f"- Команды: {'✅ Есть' if plugin_analysis['has_commands'] else '❌ Нет'}\n"
            analysis_context += f"- Конфигурация: {'✅ Есть' if plugin_analysis['has_config'] else '❌ Нет'}\n"
            analysis_context += f"- client_ready: {'✅ Есть' if plugin_analysis['has_client_ready'] else '❌ Нет'}\n"
            analysis_context += f"- on_unload: {'✅ Есть' if plugin_analysis['has_on_unload'] else '❌ Нет'}\n"
            
            if plugin_analysis['warnings']:
                analysis_context += f"\n**⚠️ Предупреждения:**\n"
                for warning in plugin_analysis['warnings']:
                    analysis_context += f"- {warning}\n"
            
            analysis_context += f"\n**Оценка структуры:** {plugin_analysis['structure_score']}/9"
            analysis_context += f"\n**Валидность плагина:** {'✅ Да' if plugin_analysis['is_valid_plugin'] else '❌ Нет'}"
        
        user_prompt = f"**Файл:** {file_name}\n**Тип:** {file_desc} ({file_lang})\n**Размер:** {len(file_content)} символов, {len(file_content.splitlines())} строк\n**Вопрос пользователя:** {args}\n\n{analysis_context}\n\n**Содержимое файла:**\n```{file_lang}\n{file_content[:3000]}{'...' if len(file_content) > 3000 else ''}\n```\n\nПроанализируй этот файл и ответь на вопрос пользователя."

        response, thinking_time, model_used = await self._call_api_regular(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            is_code_request=False
        )

        if response is None:
            error_msg = f"❌ <b>Ошибка:</b>\n<code>{model_used}</code>"
            await utils.answer(status_msg, error_msg)
            return

        formatted = self._format_response(
            f"Анализ файла: {file_name}\nВопрос: {args}",
            response, 
            model_used, 
            thinking_time, 
            message, 
            is_analysis=True
        )
        
        await utils.answer(status_msg, formatted)

    @loader.command(
        ru_doc="<параметр> <значение> - Настройка API"
    )
    async def nsetcmd(self, message):
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "❌ <b>Укажите параметр и значение!</b>\nПример: <code>.nset key sk-...</code>")
            return
        
        parts = args.split(" ", 1)
        if len(parts) != 2:
            await utils.answer(message, "❌ <b>Неверный формат!</b>\nИспользуйте: <code>.nset &lt;параметр&gt; &lt;значение&gt;</code>")
            return
        
        param = parts[0].lower()
        value = parts[1]
        
        valid_params = {
            "key": "api_key",
            "url": "api_url",
            "model": "model",
            "temp": "temperature",
            "prompt": "system_prompt",
            "codeprompt": "code_prompt",
            "template": "response_template",
            "timeout": "timeout",
            "max_tokens": "max_tokens",
            "streaming": "streaming",
            "stream_update_interval": "stream_update_interval",
            "spoiler": "auto_spoiler_quotes",
        }
        
        if param not in valid_params:
            await utils.answer(message, f"❌ <b>Неизвестный параметр:</b> {param}\nДоступные: {', '.join(valid_params.keys())}")
            return
        
        config_key = valid_params[param]
        
        try:
            if param == "temp":
                value = float(value)
                if not 0.0 <= value <= 2.0:
                    raise ValueError("Температура должна быть от 0.0 до 2.0")
            elif param == "timeout":
                value = int(value)
                if not 0 <= value <= 600:
                    raise ValueError("Таймаут должен быть от 0 до 600 секунд (0 = без таймаута)")
            elif param == "max_tokens":
                value = int(value)
                if not 1 <= value <= 16384:
                    raise ValueError("Максимальное количество токенов должно быть от 1 до 16384")
            elif param == "stream_update_interval":
                value = float(value)
                if not 0.1 <= value <= 5.0:
                    raise ValueError("Интервал обновления должен быть от 0.1 до 5.0 секунд")
            elif param in ["streaming", "use_markdown", "show_thinking_time", "auto_detect_code",
                          "has_file", "preserve_history", "code_cleanup", "smart_file_detection",
                          "file_clean_header", "auto_spoiler_quotes"]:
                value_lower = value.lower()
                if value_lower in ["true", "yes", "1", "вкл", "да", "on"]:
                    value = True
                elif value_lower in ["false", "no", "0", "выкл", "нет", "off"]:
                    value = False
                else:
                    raise ValueError("Значение должно быть true/false, вкл/выкл, да/нет")
            elif param == "model":
                logger.info(f"Changing model from {self.config['model']} to {value}")
            
            old_value = self.config[config_key]
            self.config[config_key] = value
            
            await utils.answer(message, f"✅ <b>Параметр '{param}' изменен:</b>\n<code>{old_value}</code> → <code>{value}</code>")
            
            if param in ["url", "model"]:
                logger.info(f"API configuration updated: {param} = {value}")
            
        except ValueError as e:
            await utils.answer(message, f"❌ <b>Ошибка значения:</b> {e}")
        except Exception as e:
            logger.error(f"Error setting config: {e}")
            await utils.answer(message, f"❌ <b>Ошибка:</b> {e}")

    @loader.command(
        ru_doc="Показать текущие настройки"
    )
    async def nconfigcmd(self, message):
        config_info = []
        
        safe_keys = [
            "api_url", "model", "temperature", "max_tokens",
            "system_prompt", "code_prompt", "analysis_prompt",
            "response_template", "timeout", "use_markdown",
            "show_thinking_time", "auto_detect_code", "has_file",
            "file_min_length", "preserve_history", "max_history",
            "code_cleanup", "smart_file_detection", "file_clean_header",
            "max_file_size", "streaming", "stream_update_interval",
            "auto_spoiler_quotes"
        ]
        
        for key in safe_keys:
            value = self.config[key]
            if isinstance(value, str) and len(value) > 100:
                value = value[:100] + "..."
            config_info.append(f"<b>{key}:</b> <code>{value}</code>")
        
        api_key_status = "✅ Установлен" if self.config["api_key"] else "❌ Не установлен"
        config_info.insert(0, f"<b>api_key:</b> {api_key_status}")
        
        config_text = "\n".join(config_info)
        await utils.answer(message, f"<b>Текущие настройки:</b>\n\n{config_text}")

    @loader.command(
        ru_doc="Очистить историю диалога"
    )
    async def nclearcmd(self, message):
        chat_id = utils.get_chat_id(message)
        key = f"neural_chat_{chat_id}"
        
        if key in self.conversations:
            self.conversations[key] = [
                {"role": "system", "content": await self._format_system_prompt(message)}
            ]
            await utils.answer(message, "✅ <b>История диалога очищена!</b>")
        else:
            await utils.answer(message, "ℹ️ <b>История диалога уже пуста.</b>")

    @loader.command(
        ru_doc="Показать список API"
    )
    async def napiscmd(self, message):
        api_list = []
        
        for name, preset in self.API_PRESETS.items():
            models = ", ".join(preset["models"][:3])
            if len(preset["models"]) > 3:
                models += f" и еще {len(preset['models']) - 3}"
            
            api_list.append(f"<b>• {name.capitalize()}:</b>\n  URL: <code>{preset['url']}</code>\n  Модели: {models}\n  Формат: {preset['format']}")
        
        await utils.answer(message, f"<b>Поддерживаемые API:</b>\n\n" + "\n\n".join(api_list))

    @loader.command(
        ru_doc="Показать переменные для промпта"
    )
    async def nvarscmd(self, message):
        variables = [
            "<b>{username}</b> - имя пользователя",
            "<b>{date}</b> - текущая дата (дд.мм.гггг)",
            "<b>{time}</b> - текущее время (чч:мм:сс)",
            "<b>{model}</b> - название модели",
            "<b>{chat_id}</b> - ID чата",
            "<b>{timestamp}</b> - метка времени Unix",
            "<b>{file_type}</b> - тип файла (только для анализа)",
            "<b>{file_name}</b> - имя файла (только для анализа)"
        ]
        
        await utils.answer(message, "🔧 <b>Доступные переменные в промпте:</b>\n\n" + "\n".join(variables))

    @loader.command(
        ru_doc="Показать переменные для шаблона ответа"
    )
    async def nrvarcmd(self, message):
        variables = [
            "<b>{question}</b> - вопрос пользователя",
            "<b>{answer}</b> - ответ нейросети",
            "<b>{model}</b> - название модели",
            "<b>{thinking_time}</b> - время генерации в секундах",
            "<b>{time}</b> - время генерации в формате 'X.XX сек.'"
        ]
        
        await utils.answer(message, "🔧 <b>Доступные переменные в шаблоне ответа:</b>\n\n" + "\n".join(variables))

    @loader.command(
        ru_doc="Показать справку"
    )
    async def nhelpcmd(self, message):
        await utils.answer(message, self.strings["usage"])

    @loader.command(
        ru_doc="Отправить последний ответ файлом"
    )
    async def nfilecmd(self, message):
        chat_id = utils.get_chat_id(message)
        
        if chat_id not in self._last_response:
            await utils.answer(message, "❌ <b>Нет последнего ответа для отправки файлом!</b>")
            return
        
        response_data = self._last_response[chat_id]
        
        status_msg = await utils.answer(message, "💾 <b>Подготавливаю файл...</b>")
        
        try:
            await self._send_as_file(message, response_data)
            await status_msg.delete()
        except Exception as e:
            await utils.answer(status_msg, f"❌ <b>Ошибка при отправке файла:</b>\n<code>{e}</code>")