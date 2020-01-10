#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# version: 1.2

import logging

import time
from telegram.ext import Updater, CommandHandler, InlineQueryHandler, MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardMarkup
from info import *
from database import *

import pathlib as pl
import itertools as itl


# Клавиатуры:
keybstart = ReplyKeyboardMarkup([['Зарегистрироваться и разделить'], ['Инструкция']], resize_keyboard=True)
keybreg = ReplyKeyboardMarkup([['Мой профиль'], ['Удалить профиль'], ['Инструкция', 'Отзыв']], resize_keyboard=True)


"""Переобозначения"""


updater = Updater(token=token, use_context=True)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
dispatcher = updater.dispatcher


"""Program"""


# Старт + проверка на валидность пользователей
def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text='Ты в главном меню. Для поиска напарника необходимо пройти регистрацию.',
                             reply_markup=keybstart)
    old_users(update, context)


# Link on services
def link(update, context, serv_name):
    for i in ls:
        if serv_name == i:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=f"['{serv_name}']('{lslink[i][0]}')",
                parse_mode='Markdown')


# Админ
def admin(update, context):
    iduser = update.message.from_user.id
    idchat = update.message.chat.id
    passwlocal = context.args
    if not passwlocal:
        return
    if password == int(passwlocal[0]):
        admin_check(update, context, iduser, idchat)


# Проверка в списке админов для добавления админа
def admin_check(update, context, iduser, idchat):
    if iduser == idchat:
        if iduser not in admins['admins']:
            admins['admins'].append(iduser)
            admins.save()
            context.bot.send_message(chat_id=iduser, text=f"Тебя внесли в список админов.")
        else:
            context.bot.send_message(chat_id=idchat, text=f"Ты уже состоишь в списке админов.")
    if iduser != idchat:
        if iduser not in admins['admins']:
            admins['admins'].append(iduser)
            admins.save()
            context.bot.send_message(chat_id=iduser, text=f"Тебя внесли в список админов.")
        else:
            context.bot.send_message(chat_id=idchat, text=f"Ты уже состоишь в списке админов.")
        if idchat not in admins['chat_for_admins']:
            admins['chat_for_admins'].append(idchat)
            admins.save()
            context.bot.send_message(chat_id=idchat, text=f"Чат внесли список админов.")
        else:
            context.bot.send_message(chat_id=idchat, text=f"Чат уже состоит в списке админов.")


# /help
def help(update, context):
    iduser = update.message.from_user.id
    if iduser in admins['admins']:
        context.bot.send_message(chat_id=iduser, text='Список команд:'
                                                      '\n/start'
                                                      '\n/admin <password>'
                                                      '\n/check'
                                                      '\n/ls .'
                                                      '\n/download <nothing or filename>')
    else:
        instruction(update, context)


# Скачать базы данных
def download(update, context):
    iduser = update.message.from_user.id
    if iduser not in admins['admins']:
        return update.message.reply_text(
            text='You do not have enough permissions to execute this')
    if len(context.args) == 0:
        for i in datafile:
            context.bot.send_document(
                chat_id=update.message.chat.id,
                document=open(f'{i}', 'rb'))
        return
    for p in filter(
        lambda p: p.is_file(),
        itl.chain(*[
            pl.Path('.').glob(pattern)
            for pattern in context.args])):
        update.message.reply_document(document=p.open('rb'))


def ls_dir(update, context):
    if update.message.from_user.id not in admins['admins']:
        return update.message.reply_text(
            text='You do not have enough permissions to execute this')
    if len(context.args) != 1:
        return update.message.reply_markdown(
            text='Usage: `/ls <path>`\n  E.g.: `/ls .`')
    path = pl.Path(context.args[0])
    if not path.exists():
        return update.message.reply_markdown(
            text='f`{path}` does not exist')
    if not path.is_dir():
        return update.message.reply_markdown(
            text='f`{path}` is not a directory')
    update.message.reply_markdown(
        text='```' + '\n'.join(str(p) for p in path.iterdir()) + '```')


# Проверка наполненности сервисов для админов
def check_for_admins(update, context):
    iduser = update.message.from_user.id
    if iduser in admins['admins']:
        msg = []
        for i in serv:
            msg.append(f"{i}:")
            for k in serv[i]:
                counter = len(serv[i][k])
                msg.append(f"{counter}/{k}")
        context.bot.send_message(chat_id=iduser, text=msg)
    else:
        unknown(update, context)


# Бан пользователя
def ban(update, context):
    iduser = update.message.from_user.id
    if iduser in admins['admins']:
        try:
            ban = context.args
            for i in prof:
                if prof[i]['username'] == ban[0]:
                    prof[i]['ban'] = 1
                    context.bot.send_message(chat_id=iduser,
                                                text=f"Пользователь с username @{ban[0]} забанен")
                    prof.save()
                elif i == ban[0]:
                    prof[i]['ban'] = 1
                    context.bot.send_message(chat_id=iduser,
                                                text=f"Пользователь с id {ban[0]} забанен")
                    prof.save()
                else:
                    context.bot.send_message(chat_id=iduser,
                                             text="Пользователя не существует")
        except:
            context.bot.send_message(chat_id=iduser,
                                     text="Введи id пользователя или username в виде \n"
                                          "/ban <id or username(without @)>")


# Удалить профиль
def delete(update, context, iduser):
    if iduser in prof:
        serv_name, num = list(prof[iduser]['services'].items())[0]
        prof[iduser]['state'] = 'del'
        for i in prof[iduser]['services']:
            prof[iduser]['services'][i] = None
        # del prof[iduser]
        prof.save()
        if iduser in serv[serv_name][num]:
            serv[serv_name][num].remove(iduser)
        serv.save()
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Твой профиль удалён!', reply_markup=keybstart)
    else:
        errnothing(update, context)
    # delete_from_bdfinder(iduser)  # Удаляет профиль из serv


# Перенос старых пользователей в архив
def old_users(update, context):
    for i in list(prof):
        i = int(i)
        if (time.time() - prof[i]['date']) > 2628000:
            archive[i] = {}
            for i1 in prof[i]:
                archive[i][i1] = prof[i][i1]
            del prof[i]
            for k in serv:
                for d in serv[k]:
                    for l in range(len(serv[k][d])):
                        if i == serv[k][d][l]:
                            del serv[k][d][l]
    prof.save()
    serv.save()
    archive.save()


# Инструкция
def instruction(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text='Не с кем разделить подписку на Netflix и другие популярные платные сервисы?'
                                  'Тогда ты по адресу! Чтобы найти товарища, готового помочь тебе в столь '
                                  'непростом деле, пройди регистрацию, а все остальное алгоритм сделает за тебя!\n'
                                  'Если по какой-то причине бот работает неправильно, введи команду /start')


# Отзыв
def feedback(update, context, iduser):
    keyb = ReplyKeyboardMarkup([['В начало']], resize_keyboard=True)
    context.bot.send_message(chat_id=iduser, text="Здесь вы можете оставить свои пожелания,"
                                                                  " сообщить о проблеме или просто пожелать"
                                                                  " разработчикам хорошего дня:", reply_markup=keyb)
    prof[iduser]['state'] = 'fdb'
    save(iduser)


def send_feedback(update, context, iduser, sms):
    for i in admins['chat_for_admins']:
        context.bot.send_message(chat_id=f'{i}', text=f"{prof[iduser]['name']}"
                                                        f" {'@' if update.message.from_user.username else ''}"
                                                        f"{update.message.from_user.username or update.message.from_user.id} "
                                                        f"написал:\n"
                                                        f"{sms}")
    if not admins['chat_for_admins']:
        for i in admins['admins']:
            context.bot.send_message(chat_id=f'{i}', text=f"{prof[iduser]['name']}"
                                                          f" {'@' if update.message.from_user.username else ''}"
                                                          f"{update.message.from_user.username or update.message.from_user.id} "
                                                          f"написал:\n"
                                                          f"{sms}")


# Ответ на отзыв
def feedback_reply(update, context, iduser):
    if iduser in admins['admins']:
        reply = update.message.text
        reply_msg = update.message.reply_to_message.text
        try:
            username = reply_msg.split('\n', 1)[0].rsplit(' ', 2)[1]
            if '@' in username:
                index = 0
                username = username[:index] + username[index + 1:]
                for i in prof:
                    if prof[i]['username'] == username:
                        context.bot.send_message(chat_id=i, text=f"Ответ разработчика:\n"
                                                                 f"{reply}")
            else:
                context.bot.send_message(chat_id=int(username), text=f"Ответ разработчика:\n"
                                                                 f"{reply}")
        except:
            pass


# Неизвестная команда/сообщение
def unknown(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Сори, я вас не понял...")


# Еще не зарегитсрирован
def errnothing(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text='Ты ещё не зарегистрировался.',
                             reply_markup=keybstart)


# Уже зарегистрирован
def errreg(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text='Ты уже зарегистрировался.',
                             reply_markup=keybreg)


"""MainStart"""


def main(update, context):
    iduser = update.message.from_user.id  # id переписки
    sms1 = update.message
    sms = sms1.text
    if iduser in prof and prof[iduser]['ban'] == 1:
        context.bot.send_message(chat_id=iduser, text="Действие невозможно. Ты забанен за плохое поведение.")
        for k in serv:
            for d in serv[k]:
                for l in range(len(serv[k][d])):
                    if iduser == serv[k][d][l]:
                        del serv[k][d][l]
    elif sms == 'Мой профиль':
        myprof(update, context, iduser)
    elif sms == 'Удалить профиль':
        delete(update, context, iduser)
    elif sms == 'Инструкция':
        instruction(update, context)
    elif sms == 'В начало':
        try:
            if prof[iduser]['state'] == 'fdb':
                start(update, context)
                prof[iduser]['state'] = 'reg2'
                save(iduser)
            else:
                start(update, context)
        except:
            start(update, context)
    # reg0, начало регистрации
    elif sms == "Зарегистрироваться и разделить":
        reg00(update, context, iduser)
    # reg1, выбор сервиса
    elif iduser not in prof:
        unknown(update, context)
    elif prof[iduser]['state'] == 'reg0':
        reg1(update, context, sms, iduser)
    # reg2, выбор количества человек
    elif prof[iduser]['state'] == 'reg1':
        reg2(update, context, sms, iduser)
        serv_name, num = list(prof[iduser]['services'].items())[0]
        add_in_bdfinder(iduser, num, serv_name, update, context)
    elif sms == 'Отзыв' and iduser in prof:
            if prof[iduser]['state'] == 'reg2':
                feedback(update, context, iduser)
    elif prof[iduser]['state'] == 'fdb':
        send_feedback(update, context, iduser, sms)
        prof[iduser]['state'] = 'reg2'
        save(iduser)
        context.bot.send_message(chat_id=iduser, text='Отзыв отправлен',
                                 reply_markup=keybreg)
    elif update.message.reply_to_message.text is not None:
        feedback_reply(update, context, iduser)
    else:
        unknown(update, context)


"""MainEnd"""


"""FinderStart"""


# Finder
def finder(update, context):
    for serv_name in sum(ls, []):
        for user_id in prof:
            if serv_name not in prof[user_id]['services']:
                continue
            # print(f"{user_id}: {prof[user_id]['services'][serv]}: {serv}")
            add_in_bdfinder(
                user_id, prof[user_id]['services'][serv_name],
                serv_name, update, context)


def add_in_bdfinder(user_id, p, serv_name, update, context):
    team = serv[serv_name][p]
    # Проверка на наполненность
    if len(team) + 1 == p:
        team.append(user_id)
        msg = 'Все в сборе!\n' + '\n'.join(prof[j]['user_link'] for j in team)
        msg1 = f'Если тебе понравился наш бот, можешь [поддержать](https://money.yandex.ru/to/410016404557682) проект' \
               f' и подписаться на [группу ВК]({VK}.)'
        for i in team:
            context.bot.send_message(chat_id=i, text=msg, disable_web_page_preview=True)
            context.bot.send_message(chat_id=i, text=msg1, parse_mode='Markdown', disable_web_page_preview=True)
            link(update, context, serv_name)
        serv[serv_name][p] = []
    else:
        msg = f'Собрано {len(team) + 1}/{p}'
        team.append(user_id)
        for i in team:
            try:
                context.bot.send_message(chat_id=i, text=msg)
            except:
                print('Chat not found')


    serv.save()


"""FinderEnd"""


# Начало регистрации
def reg00(update, context, iduser):
    if iduser in prof:
        if prof[iduser]['state'] == 'reg2':
            errreg(update, context)
        else:
            reg01(update, context, iduser)
    else:
        prof[iduser] = {}
        reg01(update, context, iduser)


# Продолжение reg00
def reg01(update, context, iduser):
    prof[iduser]['state'] = 'reg0'
    prof[iduser]['name'] = update.message.from_user.full_name
    prof[iduser]['ban'] = None
    prof[iduser]['username'] = update.message.from_user.username
    prof[iduser]['user_link'] = update.message.from_user.link
    save(iduser)
    btn_services(update, context)


# Кнопки для выбора сервиса
def btn_services(update, context):
    keyboard = ReplyKeyboardMarkup([[i[0] for i in ls], ['В начало']], resize_keyboard=True)
    context.bot.send_message(chat_id=update.message.chat_id, text='Выбери сервис:',
                             reply_markup=keyboard)


# Проверка ввода сервиса и выполнение "btn_ls"
def reg1(update, context, sms, iduser):
    flat = sum(ls, [])
    if sms not in flat:
        return
    prof[iduser]['state'] = 'reg1'
    prof[iduser]['services'] = {sms: None}
    save(iduser)
    btn_ls(update, context, flat.index(sms))


# Кнопки для выбора количества человек
def btn_ls(update, context, sss):
    keyboard = ReplyKeyboardMarkup([lscount[sss], ['В начало']], resize_keyboard=True)
    abc1 = []
    abc2 = []
    for i in serv[ls[sss][0]]:
        abc1.append(int(len(serv[ls[sss][0]][i])))
    for i in range(len(lscount[sss])):
        abc2.append(f"{lscount[sss][i]} чел.: {abc1[i]}/{lscount[sss][i]}")
    msg = 'На сколько человек разделить подписку?' \
          '\nСобрано на данный момент:\n' + '\n'.join(abc2)
    context.bot.send_message(chat_id=update.message.chat_id, text=msg, reply_markup=keyboard)


# Проверка ввода количества человек, сохранение количества человек и "btn_end"
def reg2(update, context, sms, iduser):
    serv_name = list(prof[iduser]['services'].keys())[0]
    prof[iduser]['services'][serv_name] = int(sms)
    prof[iduser]['state'] = 'reg2'
    save(iduser)
    btn_end(update, context)


# Фраза по звершении регистрации
def btn_end(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text='Поздравляю, ты зарегистрировался! '
                                                                  'Как только найдется напарник, я тебе сообщу!',
                             reply_markup=keybreg)


# надо переделать
def myprof(update, context, iduser):
    if iduser in prof:
        for i in range(len(ls[:])):
            if ls[i][0] in prof[iduser]['services']:
                serv_name = ls[i][0]
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text='Твой профиль:'
                                 f'\nСервис: {serv_name}'
                                 f"\nКоличество человек: {prof[iduser]['services'][serv_name]}"
                                 f"\nНа данный момент собрано:  "
                                      f"{len(serv[serv_name][prof[iduser]['services'][serv_name]])}"
                                      f"/{prof[iduser]['services'][serv_name]}",
                                 reply_markup=keybreg)
    else:
        errnothing(update, context)


# Сохранение prof + date
def save(iduser):
    prof[iduser]['date'] = float(time.time())
    prof.save()


# Пересылка смс
def inline(update, context):
    query = update.inline_query.query
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query,
            title='Отправить',
            input_message_content=InputTextMessageContent(query)
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)


dispatcher.add_handler(InlineQueryHandler(inline))
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('admin', admin))
dispatcher.add_handler(CommandHandler('check', check_for_admins))
dispatcher.add_handler(CommandHandler('ls', ls_dir))
dispatcher.add_handler(CommandHandler('download', download))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('ban', ban))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))
dispatcher.add_handler(MessageHandler(Filters.all, main))


updater.start_polling()
updater.idle()


"""Какая-то дичь с командами"""
# delete_handler = CommandHandler('delete', delete)
# dispatcher.add_handler(delete_handler)
# help_handler = CommandHandler('help', help)
# dispatcher.add_handler(help_handler)



