from asyncio import run
from aiogram import Bot, Dispatcher, F
from aiogram.filters.command import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ContentType
from aiogram.filters import Filter
from random import choice
from aiogram.filters.callback_data import CallbackData, CallbackQuery
import sqlite3
bot = Bot(token="7058050459:AAE4Ic95tM67xKXA5hLhNLxxZTlj3iTsyBA")
dp = Dispatcher()
connection = sqlite3.connect("friend_place_servers.db")
cursor = connection.cursor()


class MyCallback(CallbackData, prefix="my"):
    foo: str
    id: int
    name: str


class Information(StatesGroup):
    name = State()
    second_name = State()
    age = State()
    interests = State()
    photo = State()


class EditName(StatesGroup):
    get_data = State()


class EditSecondName(StatesGroup):
    get_data = State()


class EditAge(StatesGroup):
    get_data = State()


class EditInterests(StatesGroup):
    get_data = State()


class EditPhoto(StatesGroup):
    get_data = State()


@dp.message(Command("start"))
async def start(message, state):
    user_list = lists()
    for i in range(len(user_list)):
        if message.chat.id == int(user_list[i][4]):
            await message.answer("You are already signed in, welcome back I guess.")
            return
    await message.answer("Tell me some information about you. Firstly, what is your name?")
    await state.set_state(Information.name)


@dp.message(Information.name)
async def name(message, state):
    await message.answer("What is your second name?")
    await state.update_data(name=message.text)
    await state.set_state(Information.second_name)


@dp.message(Information.second_name)
async def second_name(message, state):
    await message.answer("What is your age?")
    await state.update_data(second_name=message.text)
    await state.set_state(Information.age)


@dp.message(Information.age)
async def age(message, state):
    await message.answer("What are your interests if you have any?")
    await state.update_data(age=message.text)
    await state.set_state(Information.interests)


@dp.message(Information.interests)
async def interests(message, state):
    await message.answer("Please send your photo.")
    await state.update_data(interests=message.text)
    await state.set_state(Information.photo)


def strip_(s):
    return s.strip()


def lists():
    f = open("users.txt", "r")
    list_thing = []
    for i in f.readlines():
        list_thing.append(i.split("/"))
    for i in range(len(list_thing)):
        list_thing[i][6] = list(map(strip_, list_thing[i][6].split(" ")))
    return list_thing


@dp.message(Information.photo)
async def photo(message, state, bot):
    photos = message.photo[-1]
    await bot.download(photos, destination=f"photos/{message.chat.id}.jpg")
    # await state.finish()
    result = await state.get_data()
    image = FSInputFile(f"photos/{message.chat.id}.jpg")
    await bot.send_photo(message.chat.id, image, caption=f"{result['name']} {result['second_name']} \nAge: {result['age']} \nInterests: {result['interests']}")
    # state.finish()
    text_file = open("users.txt", "a")
    text_file.write(f"{result['name']}/{result['second_name']}/{result['age']}/{result['interests']}/{message.chat.id}/{message.from_user.username}/{message.chat.id}\n")
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Start a selection"), KeyboardButton(text="Edit profile")]])
    await message.answer("You have been registered!", reply_markup=keyboard)


def pickup(list_idk):
    return choice(list_idk)


@dp.message(F.text == "Start a selection")
async def filtered_text(message):
    chosen_user = lists()
    duplicate_id = -1
    ignore_list = []
    for idk in range(len(chosen_user)):
        if str(message.chat.id) in chosen_user[idk]:
            duplicate_id = idk
            ignore_list = chosen_user[idk][6]
    if duplicate_id != -1:
        chosen_user.pop(duplicate_id)
    for idk in ignore_list:
        to_delete = -1
        for i in range(len(chosen_user)):
            if int(chosen_user[i][4]) == int(idk):
                to_delete = i
        if to_delete != -1:
            chosen_user.pop(to_delete)
    if len(chosen_user) == 0:
        await message.answer("All users are gone, try later bruh.")
        return
    chosen_user = pickup(chosen_user)
    kb = [
        [
            InlineKeyboardButton(text="Ignore", callback_data=MyCallback(foo="Ignore", id=int(chosen_user[4]), name=chosen_user[5]).pack()),
            InlineKeyboardButton(text="Send a friend request", callback_data=MyCallback(foo="Request", id=int(chosen_user[4]), name=chosen_user[5]).pack())
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    image = FSInputFile(f"photos/{chosen_user[4]}.jpg")
    await bot.send_photo(message.chat.id, image, caption=f"{chosen_user[0]} {chosen_user[1]} \nAge: {chosen_user[2]} \nInterests: {chosen_user[3]}", reply_markup=keyboard)


@dp.message(F.text == "Edit profile")
async def editor(message):
    user_data = lists()
    kb = [
        [
            InlineKeyboardButton(text="Name", callback_data=MyCallback(foo="name", id=message.chat.id, name=message.from_user.username).pack()),
            InlineKeyboardButton(text="Second name", callback_data=MyCallback(foo="second name", id=message.chat.id, name=message.from_user.username).pack()),
            InlineKeyboardButton(text="Age", callback_data=MyCallback(foo="age", id=message.chat.id, name=message.from_user.username).pack()),
            InlineKeyboardButton(text="Interests", callback_data=MyCallback(foo="interests", id=message.chat.id, name=message.from_user.username).pack()),
            InlineKeyboardButton(text="Profile photo", callback_data=MyCallback(foo="photo", id=message.chat.id, name=message.from_user.username).pack())
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer("What do you want to change in your profile?", reply_markup=keyboard)


def ignore(id_thing, ignored_id):
    some_data_ig = lists()
    for i in range(len(some_data_ig)):
        if str(id_thing) in some_data_ig[i]:
            if str(ignored_id) not in some_data_ig[i][6]:
                some_data_ig[i][6].append(ignored_id)
    file = open("users.txt", "w")
    for i in range(len(some_data_ig)):
        for j in range(len(some_data_ig[i]) - 1):
            file.write(str(some_data_ig[i][j]) + "/")
        for k in range(len(some_data_ig[i][6])):
            if k == len(some_data_ig[i][6]) - 1:
                file.write(str(some_data_ig[i][6][k]))
            else:
                file.write(str(some_data_ig[i][6][k]) + " ")
        file.write("\n")


def find_id(id_idk):
    new_users = lists()
    print(new_users)
    for i in range(len(new_users)):
        if new_users[i][4] == str(id_idk):
            return new_users[i]


@dp.callback_query(MyCallback.filter(F.foo == "Request"))
async def callbacker(callback: CallbackQuery, callback_data: MyCallback):
    await callback.message.answer(f"Your friend request was sent.")
    user = find_id(callback.message.chat.id)
    image = FSInputFile(f"photos/{callback.message.chat.id}.jpg")
    kb = [
        [
            InlineKeyboardButton(text="Accept", callback_data=MyCallback(foo="Accept", id=int(user[4]), name=user[5]).pack()),
            InlineKeyboardButton(text="Decline", callback_data=MyCallback(foo="Decline", id=int(user[4]), name=user[5]).pack())
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await bot.send_photo(callback_data.id, image, caption=f"You have got a friend request!!! \n{user[0]} {user[1]} \nAge: {user[2]} \nInterests: {user[3]}", reply_markup=keyboard)
    ignore(callback.message.chat.id, callback_data.id)
    await filtered_text(callback.message)


@dp.callback_query(MyCallback.filter(F.foo == "Ignore"))
async def callbacker(callback, callback_data):
    ignore(callback.message.chat.id, callback_data.id)
    await filtered_text(callback.message)


@dp.callback_query(MyCallback.filter(F.foo == "Decline"))
async def callbacker(callback, callback_data):
    ignore(callback.message.chat.id, callback_data.id)
    await filtered_text(callback.message)


@dp.callback_query(MyCallback.filter(F.foo == "Accept"))
async def callbacker(callback, callback_data):
    ignore(callback.message.chat.id, callback_data.id)
    await bot.send_message(callback.message.chat.id, "Request accepted! New friend's username: @" + callback_data.name)
    await bot.send_message(callback_data.id, "One of the users you have sent your friend request has accepted it! His user is @" + callback.from_user.username)
    await filtered_text(callback.message)


def file_edit(user_data_smh):
    file = open("users.txt", "w")
    for i in range(len(user_data_smh)):
        for j in range(len(user_data_smh[i]) - 1):
            file.write(str(user_data_smh[i][j]) + "/")
        for k in range(len(user_data_smh[i][6])):
            if k == len(user_data_smh[i][6]) - 1:
                file.write(str(user_data_smh[i][6][k]))
            else:
                file.write(str(user_data_smh[i][6][k]) + " ")
        file.write("\n")


@dp.callback_query(MyCallback.filter(F.foo == "name"))
async def callbacker(callback, callback_data, state):
    await callback.message.answer("What name do you want to change to?")
    await state.set_state(EditName.get_data)


@dp.callback_query(MyCallback.filter(F.foo == "second name"))
async def callbacker(callback, callback_data, state):
    await callback.message.answer("What second name do you want to change to?")
    await state.set_state(EditSecondName.get_data)


@dp.callback_query(MyCallback.filter(F.foo == "age"))
async def callbacker(callback, callback_data, state):
    await callback.message.answer("What age do you want to change to?")
    await state.set_state(EditAge.get_data)


@dp.callback_query(MyCallback.filter(F.foo == "interests"))
async def callbacker(callback, callback_data, state):
    await callback.message.answer("What do you want to change in your interests?")
    await state.set_state(EditInterests.get_data)


@dp.callback_query(MyCallback.filter(F.foo == "photo"))
async def callbacker(callback, callback_data, state):
    await callback.message.answer("Which photo do you want to switch to?")
    await state.set_state(EditPhoto.get_data)


@dp.message(EditName.get_data)
async def change(message, state):
    user_data_smh = lists()
    for i in range(len(user_data_smh)):
        if user_data_smh[i][4] == str(message.chat.id):
            user_data_smh[i][0] = message.text
            break
    file_edit(user_data_smh)
    await message.answer("The name change was successful. Your new name is " + message.text)


@dp.message(EditSecondName.get_data)
async def change(message, state):
    user_data_smh = lists()
    for i in range(len(user_data_smh)):
        if user_data_smh[i][4] == str(message.chat.id):
            user_data_smh[i][1] = message.text
            break
    file_edit(user_data_smh)
    await message.answer("The second name change was successful. Your new second name is " + message.text)


@dp.message(EditAge.get_data)
async def change(message, state):
    user_data_smh = lists()
    for i in range(len(user_data_smh)):
        if user_data_smh[i][4] == str(message.chat.id):
            user_data_smh[i][2] = message.text
            break
    file_edit(user_data_smh)
    await message.answer("The age change was successful. Your new age is " + message.text)


@dp.message(EditInterests.get_data)
async def change(message, state):
    user_data_smh = lists()
    for i in range(len(user_data_smh)):
        if user_data_smh[i][4] == str(message.chat.id):
            user_data_smh[i][3] = message.text
            break
    file_edit(user_data_smh)
    await message.answer("The interests list change was successful. Your new interests are " + message.text)


@dp.message(EditPhoto.get_data)
async def change(message, state):
    photos = message.photo[-1]
    await bot.download(photos, destination=f"photos/{message.chat.id}.jpg")
    await message.answer("The profile photo has been changed.")


async def main():
    await dp.start_polling(bot)

run(main())
