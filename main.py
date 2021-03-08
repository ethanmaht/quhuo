# coding=utf8
from emtools import read_database as rd
from algorithm import retained


def syn_shard_user_day_work(s_date=None):
    print(1)
    work = rd.DataBaseWork()
    if s_date:
        work.date = s_date
    work.loop_all_database()


def syn_market_keep_day(s_date=None):
    work = retained.KeepTableDay(list_day=[1, 2, 3, 7, 14, 30])
    if s_date:
        work.s_date = s_date
    work.count_keep_table_day_run()


if __name__ == '__main__':
    print('Start work:')
    syn_market_keep_day('2021-01-20')
