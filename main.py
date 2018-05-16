import json
import numpy as np
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import my_db


def start(bot, update):
    update.message.reply_text('Hi, '
                              '@{}!'.format(update.effective_user.username))


def db_prepare(message, _type, fm, sm, ans):
    d = dict()
    d['chat_id'] = message['chat']['id']
    d['request_date'] = message['date'].__str__()
    d['request_type'] = _type
    d['first_matrix'] = json.dumps(fm)
    d['second_matrix'] = json.dumps(sm) if sm != "NULL" else sm
    d['answer'] = json.dumps(ans) if ans != "NULL" else ans
    return d


def make_ans(arr):
    answer = ''
    for elem in arr:
        for e in elem[:-1]:
            answer += str(e) + ' '
        answer += str(elem[-1]) + '\n'
    return answer


def answerer(bot, update):
    update.message.reply_text('Пожалуйста, введите ваши значения вместе с функцией, '
                              'которую вы хотите использовать')


def transpose(bot, update, args):
    if len(args) == 0:
        answerer()
        update.message.reply_text('Введите размеры '
                                  'двумерной матрицы, '
                                  'а потом саму матрицу')
    else:
        if len(args) == 2:
            update.message.reply_text('Введите саму матрицу')
        else:
            n, m = int(args[0]), int(args[1])
            if len(args) != (2 + n * m):
                update.message.reply_text('Ваша матрица не соответствует'
                                          ' указанным размерам. {} - '
                                          'количество строк, {} - '
                                          'количество столбцов'.format(n, m))
            else:
                new_array = [[int(args[2 + row * m + column])
                              for column in range(m)] for row in range(n)]
                val_dict = db_prepare(update.message,
                                      '/transpose',
                                      new_array,
                                      "NULL",
                                      "NULL"
                                      )
                ans = my_db.select_from_db(val_dict)
                if len(ans):
                    arr = json.loads(ans[0][0])
                    my_db.update_date(update.message['chat']['id'],
                                      ans[0][1],
                                      update.message['date'].__str__()
                                      )
                else:
                    arr = np.array(new_array).transpose().tolist()
                    val_dict['answer'] = json.dumps(arr)
                    my_db.insert_into_db(val_dict)
                update.message.reply_text(make_ans(arr))


def matrix_multiplication(bot, update, args):
    if len(args) == 0:
        answerer()
        update.message.reply_text('Введите размеры матрицы'
                                  ' и саму матрицу, '
                                  'а потом в таком же формате вторую')
    else:
        n, k = int(args[0]), int(args[1])
        try:
            k1, m = int(args[2 + n * k]), int(args[2 + n * k + 1])
            flag = False
        except IndexError:
            update.message.reply_text('Упс. Кажется, вы ввели не всё :(')
            flag = True

        if flag:
            pass
        elif k != k1:
            update.message.reply_text('Нельзя перемножить ваши матрицы.')
        elif len(args) != 4 + (n + m) * k:
            update.message.reply_text('Ваши матрицы не соответствуют'
                                      ' указанным размерам.')
        else:

            new_array1 = [[int(args[2 + row * k + column]) for column in range(k)]
                          for row in range(n)]
            new_array2 = [[int(args[4 + n * k + row * m + column])
                           for column in range(m)] for row in range(k)]

            val_dict = db_prepare(update.message,
                                  '/multimatrix',
                                  new_array1,
                                  new_array2,
                                  "NULL"
                                  )
            ans = my_db.select_from_db(val_dict)
            if len(ans):
                arr = json.loads(ans[0][0])
                my_db.update_date(update.message['chat']['id'],
                                  ans[0][1],
                                  update.message['date'].__str__()
                                  )
            else:
                new_arr = np.dot(np.array(new_array1), np.array(new_array2))
                arr = [[int(new_arr[row][column]) for column in range(m)]
                       for row in range(n)]
                val_dict['answer'] = json.dumps(arr)
                my_db.insert_into_db(val_dict)
            update.message.reply_text(make_ans(arr))


def matrix_sum(bot, update, args):
    if len(args) == 0:
        answerer()
        update.message.reply_text('Введите размеры матрицы'
                                  ' и саму матрицу, а потом вторую')
    else:
        n, k = int(args[0]), int(args[1])
        if len(args) != 2 + 2 * n * k:
            update.message.reply_text('Ваши матрицы не соответствуют'
                                      ' указанным размерам.')
        else:
            new_array1 = [[int(args[2 + row * k + column])
                           for column in range(k)] for row in range(n)]
            new_array2 = [[int(args[2 + n * k + row * k + column])
                           for column in range(k)] for row in range(n)]
            val_dict = db_prepare(update.message,
                                  '/matrixsum',
                                  new_array1,
                                  new_array2,
                                  "NULL"
                                  )
            ans = my_db.select_from_db(val_dict)
            if len(ans):
                arr = json.loads(ans[0][0])
                my_db.update_date(update.message['chat']['id'],
                                  ans[0][1],
                                  update.message['date'].__str__()
                                  )
            else:
                new_arr = np.array(new_array1) + np.array(new_array2)
                arr = [[int(new_arr[row][column]) for column in range(k)]
                       for row in range(n)]
                val_dict['answer'] = json.dumps(arr)
                my_db.insert_into_db(val_dict)
            update.message.reply_text(make_ans(arr))


def scalar_multiplication(bot, update, args):
    if len(args) == 0:
        answerer()
        update.message.reply_text('Введите размер вектора,'
                                  ' а потом сами векторы')
    else:
        n = int(args[0])
        if len(args) != 2 * n + 1:
            update.message.reply_text('Кажется, ващи вектора'
                                      'не того размера.'
                                      'Нужный размер - {}'.format(n))
        else:
            try:
                new_array1 = [int(args[column + 1]) for column in range(n)]
                new_array2 = [int(args[column + n + 1]) for column in range(n)]
                val_dict = db_prepare(update.message,
                                      '/multiscalar',
                                      new_array1,
                                      new_array2,
                                      "NULL"
                                      )
                ans = my_db.select_from_db(val_dict)
                if len(ans):
                    arr = json.loads(ans[0][0])
                    my_db.update_date(update.message['chat']['id'],
                                      ans[0][1],
                                      update.message['date'].__str__()
                                      )
                else:
                    arr = [0]
                    for column in range(n):
                        arr[0] += new_array1[column] * new_array2[column]
                    val_dict['answer'] = json.dumps(arr)
                    print(val_dict)
                    my_db.insert_into_db(val_dict)
            except Exception as err:
                print(err.__str__())
            update.message.reply_text(make_ans([arr]))


def show_history(bot, update, args):
    if len(args) == 0:
        answerer(bot, update)
    else:
        n = int(args[0])
        hist = my_db.select_history(min(n, 10), {'chat_id': update.message['chat']['id']})
        if not len(hist):
            update.message.reply_text('У Вас еще нет истории. Создайте её прямо сейчас!')
        else:
            if len(hist) == 10 and n > 10:
                update.message.reply_text('Простите, в вашей истории храняться'
                                          'только последние 10 записей.')
            for elem in hist:
                update.message.reply_text('Первая матрица:\n{}\n\nВторая матрица:\n{}'
                                          '\n\nОтвет:\n{}'.format(make_ans(json.loads(elem[2])),
                                                                  make_ans(json.loads(elem[3])),
                                                                  make_ans(json.loads(elem[4])))
                                          )


def main():
    updater = Updater(open('token').read())
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("transpose", transpose, pass_args=True))
    dp.add_handler(CommandHandler("multimatrix", matrix_multiplication, pass_args=True))
    dp.add_handler(CommandHandler("matrixsum", matrix_sum, pass_args=True))
    dp.add_handler(CommandHandler("multiscalar", scalar_multiplication, pass_args=True))
    dp.add_handler(CommandHandler("showhistory", show_history, pass_args=True))

    # # on noncommand i.e message - answer the noncommand-message on Telegram
    dp.add_handler(MessageHandler(Filters.text, answerer))

    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    my_db.main()
    main()
