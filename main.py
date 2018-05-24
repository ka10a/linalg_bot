import json
import numpy as np
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import my_db


def start(bot, update):
    update.message.reply_text('Hi, @{}!'.format(update.effective_user.username))


class Example:
    def __init__(self):
        self.command_name = ""
        self.n, self.k, self.m = '1', '2', '1'
        self.matrix1 = "1 2"
        self.matrix2 = "3 4"
        self.ans = ""
        self.command_input = ""

    def write(self, bot, update):
        answer_string = "Пример ввода:\n{} {}\n\nОтвет на ваш запрос:\n{}".format(
            self.command_name,
            self.command_input,
            self.ans
        )
        update.message.reply_text(answer_string)


def transpose_example(bot, update):
    example = Example()
    example.command_name = "/transpose"
    example.command_input = "{} {} {}".format(
        example.n,
        example.k,
        example.matrix1
    )
    example.ans = "1\n2"
    example.write(bot, update)


def multimatrix_example(bot, update):
    example = Example()
    example.command_name = "/multimatrix"
    example.command_input = "{} {} {} {} {} {}".format(
        example.n,
        example.k,
        example.matrix1,
        example.k,
        example.m,
        example.matrix2
    )
    example.ans = "11"
    example.write(bot, update)


def multiscalar_example(bot, update):
    example = Example()
    example.command_name = "/multiscalar"
    example.command_input = "{} {} {}".format(
        example.k,
        example.matrix1,
        example.matrix2
    )
    example.ans = "3 8"
    example.write(bot, update)


def matrixsum_example(bot, update):
    example = Example()
    example.command_name = "/matrixsum"
    example.command_input = "{} {} {} {}".format(
        example.n,
        example.k,
        example.matrix1,
        example.matrix2
    )
    example.ans = "4 6"
    example.write(bot, update)


def bot_help(bot, update):
    help_answer = "Надеюсь, этот текст тебе поможет :)\n\n" +\
        "/help - функция, которой ты только что воспользовался. Далее она расскажет о более полезных командах.\n\n" +\
        "/transpose - транспонирование матрицы\n" +\
        "Чтобы посмотреть пример с её использованием, нажми: /transpose_example\n\n" +\
        "/multimatrix - перемножение матриц\n" +\
        "Пример с её использованием, жми: /multimatrix_example\n\n" +\
        "/matrixsum - сумма матриц\n" +\
        "Жми для примера: /matrixsum_example\n\n" +\
        "/multiscalar - скалярное произведение векторов\n" +\
        "Примерчик: /multiscalar_example\n\n" +\
        "/showhistory - команда для просмотра истории.\n" +\
        "Хранятся только последние 10 твоих запросов на высчисление ¯\(°_o)/¯\n" +\
        "Как надо набирать эту команду:\n" +\
        "/showhistory 5 - показать последние 5 запросов на вычисление\n\n" +\
        "Все матрицы записываются подряд построчно.\nНапример, матрица\n1 2\n3 4\nбудет выглядеть как 1 2 3 4"
    update.message.reply_text(help_answer)


def db_prepare(message, _type, fm, sm, ans):
    d = dict()
    d['chat_id'] = message['chat']['id']
    d['request_date'] = message['date'].__str__()
    d['request_type'] = _type
    d['first_matrix'] = json.dumps(fm)
    d['second_matrix'] = json.dumps(sm) if sm != "NULL" else sm
    d['answer'] = json.dumps(ans) if ans != "NULL" else ans
    return d


def format_answer(arr):
    # print(arr)
    answer = ''
    for elem in arr:
        for e in elem[:-1]:
            answer += str(e) + ' '
        answer += str(elem[-1]) + '\n'
    return answer


def answerer(bot, update):
    update.message.reply_text('Пожалуйста, введите ваши значения вместе с функцией, '
                              'которую вы хотите использовать')


class OpHandler:
    def __init__(self):
        self.super_answer = 'Пожалуйста, введите значения вместе с функцией, которую хотите использовать'
        self.args_fail_answer = "Аргументов нет"
        self.args_format_fail_answer = ""
        self.args_count_fail_answer = ""
        self.command_name = ""

    def read_args(self, bot, update, args):
        if len(args) == 0:
            update.message.reply_text(self.args_fail_answer)
            update.message.reply_text(self.super_answer)
            return None, None

        n = int(args[0])
        if self.command_name == '/showhistory':
            return [n], None

        try:
            if self.command_name == '/multiscalar':
                new_array1 = [[int(args[column]) for column in range(1, n + 1)]]
                new_array2 = [[int(args[column]) for column in range(n + 1, 2 * n + 1)]]
                i = 2 * n + 1
            else:
                k = int(args[1])
                new_array1 = [[int(args[2 + row * k + column]) for column in range(k)] for row in range(n)]
                if self.command_name == "/transpose":
                    new_array2 = None
                    i = 2 + n * k
                else:
                    i = n * k + 2
                    if self.command_name == "/multimatrix":
                        k1, m1 = int(args[i]), int(args[i + 1])
                        i += 2
                        if k1 != k:
                            update.message.reply_text(self.args_format_fail_answer)
                            return None, None
                    else:
                        k1 = n
                        m1 = k
                    new_array2 = [[int(args[i + row * m1 + column]) for column in range(m1)] for row in range(k1)]
                    i += m1 * k1
            if i != len(args):
                update.message.reply_text("Слишком много аргументов. Давай по новой.")
                return None, None
        except IndexError:
            update.message.reply_text(self.args_count_fail_answer)
            return None, None
        return new_array1, new_array2

    def make_operation(self, bot, update, mat1, mat2):
        if mat1 is None:
            return None

        if mat2 is None:
            val_dict = db_prepare(
                update.message,
                self.command_name,
                mat1,
                "NULL",
                "NULL"
            )
        else:
            val_dict = db_prepare(
                update.message,
                self.command_name,
                mat1,
                mat2,
                "NULL"
            )

        if self.command_name == '/showhistory':
            n = int(mat1[0])
            hist = my_db.select_history(min(n, 10), {'chat_id': update.message['chat']['id']})
            if not len(hist):
                update.message.reply_text(self.args_format_answer)
                return None
            if len(hist) == 10 and n > 10:
                update.message.reply_text('Простите, в вашей истории храняться'
                                          'только последние 10 записей.')

            arr = []
            for elem in hist:
                request_type = elem[1]
                matrix1 = format_answer(json.loads(elem[2]))
                if elem[3] is None:
                    matrix2 = None
                else:
                    matrix2 = format_answer(json.loads(elem[3]))
                answer = format_answer(json.loads(elem[4]))
                if matrix2 is None:
                    arr.append('{}\n\nМатрица:\n{}\nОтвет:\n{}'.format(
                        request_type,
                        matrix1,
                        answer
                    ))
                else:
                    arr.append('{}\n\nПервая матрица:\n{}\nВторая матрица:\n{}\nОтвет:\n{}'.format(
                        request_type,
                        matrix1,
                        matrix2,
                        answer
                    ))
            return arr

        ans = my_db.select_from_db(val_dict)
        if len(ans):
            arr = json.loads(ans[0][0])
            my_db.update_date(
                update.message['chat']['id'],
                ans[0][1],
                update.message['date'].__str__()
            )
        else:
            if self.command_name == '/multiscalar':
                arr = [[0]]
                for column in range(len(mat1[0])):
                    arr[0][0] += mat1[0][column] * mat2[0][column]
            elif self.command_name == '/transpose':
                arr = np.array(mat1).transpose().tolist()
            else:
                if self.command_name == '/matrixsum':
                    new_arr = np.array(mat1) + np.array(mat2)
                elif self.command_name == '/multimatrix':
                    new_arr = np.dot(np.array(mat1), np.array(mat2))
                arr = [[int(new_arr[row][column]) for column in range(len(new_arr[0]))]
                       for row in range(len(new_arr))]

            val_dict['answer'] = json.dumps(arr)
            my_db.insert_into_db(val_dict)

        return arr

    def answering(self, bot, update, answer):
        if answer is None:
            return
        if self.command_name == '/showhistory':
            for elem in answer:
                update.message.reply_text(elem)
        else:
            update.message.reply_text(format_answer(answer))

    def __call__(self, bot, update, args):
        matrix1, matrix2 = self.read_args(bot, update, args)
        result = self.make_operation(bot, update, matrix1, matrix2)
        self.answering(bot, update, result)


def show_history(bot, update, args):
    operator = OpHandler()
    operator.command_name = '/showhistory'
    operator.args_format_fail_answer = 'У Вас еще нет истории. Создайте её прямо сейчас!'
    operator.__call__(bot, update, args)


def scalar_multiplication(bot, update, args):
    operator = OpHandler()
    operator.command_name = '/multiscalar'
    operator.args_fail_answer = 'Введите размер вектора, а потом сами векторы'
    operator.args_count_fail_answer = 'Кажется, ващи вектора не того размера. Нужный размер - {}'
    operator.__call__(bot, update, args)


def matrix_sum(bot, update, args):
    operator = OpHandler()
    operator.command_name = '/matrixsum'
    operator.args_fail_answer = 'Введите размеры матрицы и саму матрицу, а потом вторую'
    operator.args_count_fail_answer = 'Ваши матрицы не соответствуют указанным размерам.'
    operator.__call__(bot, update, args)


def matrix_multiplication(bot, update, args):
    operator = OpHandler()
    operator.command_name = '/multimatrix'
    operator.args_fail_answer = 'Введите размеры матрицы и саму матрицу, а потом в таком же формате вторую'
    operator.args_count_fail_answer = 'Ваши матрицы не соответствуют указанным размерам.'
    operator.args_format_fail_answer = 'Нельзя перемножить ваши матрицы.'
    operator.__call__(bot, update, args)


def transpose(bot, update, args):
    operator = OpHandler()
    operator.command_name = '/transpose'
    operator.args_fail_answer = 'Введите размеры двумерной матрицы, а потом саму матрицу'
    operator.args_count_fail_answer = 'Ваша матрица не соответствуют указанным размерам.'
    operator.__call__(bot, update, args)


def main():
    updater = Updater(open('token.txt').read())
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", bot_help))
    dp.add_handler(CommandHandler("transpose", transpose, pass_args=True))
    dp.add_handler(CommandHandler("multimatrix", matrix_multiplication, pass_args=True))
    dp.add_handler(CommandHandler("matrixsum", matrix_sum, pass_args=True))
    dp.add_handler(CommandHandler("multiscalar", scalar_multiplication, pass_args=True))
    dp.add_handler(CommandHandler("showhistory", show_history, pass_args=True))
    dp.add_handler(CommandHandler("transpose_example", transpose_example))
    dp.add_handler(CommandHandler("multimatrix_example", multimatrix_example))
    dp.add_handler(CommandHandler("matrixsum_example", matrixsum_example))
    dp.add_handler(CommandHandler("multiscalar_example", multiscalar_example))

    # # on noncommand i.e message - answer the noncommand-message on Telegram
    dp.add_handler(MessageHandler(Filters.text, answerer))

    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    my_db.create_db()
    main()
