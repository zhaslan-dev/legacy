import json
import asyncio
from unittest.mock import MagicMock, mock_open, patch

import pytest
from aiogram import types
from aiogram.dispatcher import Dispatcher

# Импортируем модуль бота
import telegrambot_vol_3


@pytest.fixture
def mock_bot():
    """Фикстура, создающая мок для бота и диспетчера."""
    dp = Dispatcher(bot.bot)
    # Мокаем метод answer у message
    mock_message = MagicMock(spec=types.Message)
    mock_message.answer = AsyncMock()
    # Мокаем метод send_message у бота
    bot.bot.send_message = AsyncMock()
    return dp, mock_message


@pytest.mark.asyncio
async def test_start(mock_bot):
    """Тест команды /start: проверяет наличие клавиатуры и текст."""
    dp, mock_message = mock_bot

    # Вызываем обработчик
    await bot.start(mock_message)

    # Проверяем, что answer был вызван один раз
    mock_message.answer.assert_called_once()
    args, kwargs = mock_message.answer.call_args
    assert args[0] == 'Выберите категорию'
    assert 'reply_markup' in kwargs
    keyboard = kwargs['reply_markup']
    assert isinstance(keyboard, types.ReplyKeyboardMarkup)
    # Проверяем, что кнопки есть
    buttons = [row[0].text for row in keyboard.keyboard]
    assert '🔪 Ножи' in buttons
    assert '🥊 Перчатки' in buttons
    assert '🔫 Снайперские винтовки' in buttons


@pytest.mark.asyncio
async def test_get_discount_knives(mock_bot, mocker):
    """Тест обработчика для ножей: вызов collect_data с cat_type=2 и отправка карточек."""
    dp, mock_message = mock_bot

    # Мокаем collect_data
    mock_collect = mocker.patch('bot.collect_data')
    # Мокаем открытие файла с тестовыми данными
    test_data = [
        {"full_name": "Knife 1", "3d": "http://example.com/1", "overprice": 10, "item_price": 100},
        {"full_name": "Knife 2", "3d": "http://example.com/2", "overprice": 20, "item_price": 200},
    ]
    mock_open_file = mock_open(read_data=json.dumps(test_data))
    mocker.patch('builtins.open', mock_open_file)

    # Мокаем asyncio.sleep, чтобы ускорить тест
    mocker.patch('asyncio.sleep', return_value=None)

    # Вызываем обработчик
    await bot.get_discount_knives(mock_message)

    # Проверяем, что collect_data вызвана с cat_type=2
    mock_collect.assert_called_once_with(cat_type=2)

    # Проверяем, что для каждого элемента отправлено сообщение
    assert mock_message.answer.call_count == len(test_data)
    # Проверяем содержимое первого сообщения
    first_call_args = mock_message.answer.call_args_list[0][0][0]
    assert 'Knife 1' in first_call_args
    assert 'Скидка: 10%' in first_call_args
    assert 'Цена: $100🔥' in first_call_args
    assert 'http://example.com/1' in first_call_args


@pytest.mark.asyncio
async def test_get_discount_guns(mock_bot, mocker):
    """Тест обработчика для снайперок: вызов collect_data с cat_type=4 и отправка карточек."""
    dp, mock_message = mock_bot

    mock_collect = mocker.patch('bot.collect_data')
    test_data = [
        {"full_name": "Sniper 1", "3d": "http://example.com/s1", "overprice": 5, "item_price": 500},
    ]
    mock_open_file = mock_open(read_data=json.dumps(test_data))
    mocker.patch('builtins.open', mock_open_file)
    mocker.patch('asyncio.sleep', return_value=None)

    await bot.get_discount_guns(mock_message)

    mock_collect.assert_called_once_with(cat_type=4)
    assert mock_message.answer.call_count == len(test_data)
    first_call_args = mock_message.answer.call_args_list[0][0][0]
    assert 'Sniper 1' in first_call_args
    assert 'Скидка: 5%' in first_call_args
    assert 'Цена: $500🔥' in first_call_args
