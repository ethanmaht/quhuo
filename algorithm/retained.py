# coding=utf8
import pandas as pd
from pandas import DataFrame as df
from emtools import sql_code
from emtools import currency_means as cm
from emtools import read_database as rd
from emtools import emdate
import datetime as dt


def retain_date_day(conn, db_name, table, date):
    date_dict = emdate.date_num_dict(date, 30)
    first_day, last_day = list(date_dict.keys())[0], list(date_dict.keys())[-1]
    one_day = pd.read_sql(
        sql_code.sql_retain_date_day.format(
            db=db_name, tab=table, date=date,
        ),
        conn
    )
    day_30 = pd.read_sql(
        sql_code.sql_retain_date_day_30.format(
            db=db_name, tab=table, s_date=first_day, e_date=last_day,
        ),
        conn
    )
    day_30['user_id'].astype(int)
    day_30['_'] = 1
    day_30 = day_30.pivot_table(
        index='user_id', columns='date_day', values='_', fill_value=0
    ).reset_index()
    day_30['user_id'] = day_30['user_id'].astype(int)
    one_day['user_id'] = one_day['user_id'].astype(int)
    one_day = pd.merge(one_day, day_30, on='user_id', how='left')
    one_day.rename(columns=date_dict, inplace=True)
    one_day = cm.pad_col(one_day)
    one_day.fillna(0, inplace=True)
    return one_day


class KeepTableDay:
    def __init__(self, list_day):
        self.host = '172.16.0.248'
        self.table_ = 'user_day'
        self.s_date = None
        self.list_day = list_day
        self.write_db = 'market_read'
        self.write_tab = 'keep_table_day'

    def count_keep_table_day_run(self, process_num=16):
        if self.s_date:
            _date = self.s_date
        else:
            conn = rd.connect_database_host(self.host, 'root', 'Qiyue@123')
            _date = rd.read_last_date(conn, self.write_db, self.write_tab, date_type_name='date_day')
            conn.close()
        date_list = []
        tar_date_list = emdate.date_list(_date, e_date=dt.datetime.now(), format_code='{Y}-{M}-{D}')
        for _date in tar_date_list:
            date_list += emdate.date_list(_date, num=self.list_day, format_code='{Y}-{M}-{D}')
        date_list = list(set(date_list))
        date_list.sort()
        for _day in date_list:
            print('****** Start to run: {d} - count_keep_table_day ******'.format(d=_day))
            tars = [_ for _ in range(512)]
            cm.thread_work(self.one_day_run, _day, tars=tars, process_num=process_num, interval=0.03, step=1)

    def one_day_run(self, date, num):
        print('======> is run keep_table_day to date:', date, ' num:', num)
        conn = rd.connect_database_host(self.host, 'root', 'Qiyue@123')
        one_day_dict = {'date_day': date, 'tab_num': num}
        table_name = self.table_ + '_' + str(num)
        data_one = retain_date_day(conn, 'happy_seven', table_name, date)
        one_day_dict.update(count_keep_table_day_logon(data_one))
        one_day_dict.update(count_keep_table_day_active(data_one))
        one_day_dict.update(count_keep_table_day_order(data_one))
        one_day_dict = df(one_day_dict, index=[num])
        one_day_dict.fillna(0, inplace=True)
        one_day_dict['ud_id'] = one_day_dict.apply(lambda x: cm.user_date_id(x['date_day'], x['tab_num']), axis=1)
        one_day_dict['month_natural_week'] = one_day_dict['date_day'].apply(
            lambda x: emdate.datetime_format_code(x, code='{nmw}'))
        one_day_dict['year_month'] = one_day_dict['date_day'].apply(
            lambda x: emdate.datetime_format_code(x, code='{Y}-{M}'))
        rd.insert_to_data(one_day_dict, conn, self.write_db, self.write_tab)
        conn.close()


def count_keep_table_day_logon(_data):
    _data['logon'] = _data['logon'].astype(int)
    _logon = _data.loc[_data['logon'] > 0]
    all_logon = sum(_logon['logon'])
    logon_2 = sum(_logon['2'])
    logon_3 = sum(_logon['3'])
    logon_7 = sum(_logon['7'])
    logon_14 = sum(_logon['14'])
    logon_30 = sum(_logon['30'])
    return {
        'all_logon': all_logon,
        'logon_2': logon_2,
        'logon_3': logon_3,
        'logon_7': logon_7,
        'logon_14': logon_14,
        'logon_30': logon_30,
    }


def count_keep_table_day_active(_data):
    _active = _data
    all_active = _active.index.size
    active_2 = sum(_active['2'])
    active_3 = sum(_active['3'])
    active_7 = sum(_active['7'])
    active_14 = sum(_active['14'])
    active_30 = sum(_active['30'])
    return {
        'all_active': all_active,
        'active_2': active_2,
        'active_3': active_3,
        'active_7': active_7,
        'active_14': active_14,
        'active_30': active_30,
    }


def count_keep_table_day_order(_data):
    _data['order_success'] = _data['order_success'].astype(int)
    _order = _data.loc[_data['order_success'] > 0]
    all_order = _order.index.size
    order_2 = sum(_order['2'])
    order_3 = sum(_order['3'])
    order_7 = sum(_order['7'])
    order_14 = sum(_order['14'])
    order_30 = sum(_order['30'])
    return {
        'all_order': all_order,
        'order_2': order_2,
        'order_3': order_3,
        'order_7': order_7,
        'order_14': order_14,
        'order_30': order_30,
    }


class RunCount:
    def __init__(self, func, write_tab, date_col, extend='continue'):
        self.host = {'host': '172.16.0.248', 'user': 'root', 'pw': 'Qiyue@123'}
        self.s_date = None
        self.write_db = 'market_read'
        self.write_tab = write_tab
        self.date_col = date_col
        self.func = func
        self.extend = extend

    def step_run(self, process_num=16, run_num=512, interval=0.03, step=1):
        tar_date_list = [0]
        if self.extend == 'list':
            tar_date_list = self.read_last_date()
        if self.extend == 'continue':
            tar_date_list = self.read_last_date(is_list=0)
        if self.extend == 'delete':
            tar_date_list = self.read_last_date(is_list=0)
            self.delete_last_date(tar_date_list)
        for _day in tar_date_list:
            print('****** Start to run: {d} - {tab} ******'.format(d=_day, tab=self.write_tab))
            tars = [_ for _ in range(run_num)]
            cm.thread_work(
                self.func, self.host, self.write_db, self.write_tab, _day,
                tars=tars, process_num=process_num, interval=interval, step=step
            )

    def direct_run(self, func, *args):
        tar_date_list = self.read_last_date(is_list=0)[0]
        func(self.host, self.write_db, self.write_tab, self.date_col, tar_date_list, *args)

    def read_last_date(self, is_list=1, date_format='{Y}-{M}-{D}'):
        if self.s_date:
            _date = self.s_date
        else:
            conn = rd.connect_database_host(self.host['host'], self.host['user'], self.host['pw'])
            _date = rd.read_last_date(conn, self.write_db, self.write_tab, date_type_name=self.date_col)
            conn.close()
            # _date = '2019-01-01'
        if is_list:
            _date = emdate.date_list(_date, e_date=dt.datetime.now(), format_code=date_format)
            _date.sort()
        else:
            _date = [_date]
        return _date

    def delete_last_date(self, del_date):
        del_db, del_tab, del_types = self.write_db, self.write_tab, self.date_col
        conn = rd.connect_database_host(self.host['host'], self.host['user'], self.host['pw'])
        for _type in del_types:
            conn = rd.connect_database_host(self.host['host'], self.host['user'], self.host['pw'])
            _date = rd.delete_last_date(conn, del_db, del_tab, _type, del_date)
        conn.close()


def count_order_logon_conversion(host, write_db, write_tab, date, num):
    print('======> is start to run {db}.{tab} - {num} ===> start time:'.format(
        db=write_db, tab=write_tab, num=num), dt.datetime.now())
    conn = rd.connect_database_host(host['host'], host['user'], host['pw'])
    first_order = pd.read_sql(sql_code.analysis_first_order.format(num=num, date=date), conn)
    repeat_order = pd.read_sql(sql_code.analysis_repeat_order.format(num=num, date=date), conn)
    logon_book_admin = pd.read_sql(sql_code.analysis_logon_book_admin.format(num=num, date=date), conn)
    one_num = pd.concat([logon_book_admin, first_order, repeat_order])
    one_num = one_num.fillna(0)
    rd.insert_to_data(one_num, conn, write_db, write_tab)
    conn.close()


def compress_order_logon_conversion(host, write_db, write_tab, date_type_name, date):
    conn = rd.connect_database_host(host['host'], host['user'], host['pw'])
    compress_date = pd.read_sql(
        sql_code.analysis_compress_order_logon_conversion.format(
            db=write_db, tab=write_tab, date=date
        ),
        conn
    )
    compress_date['date_sub'] = compress_date.apply(lambda x: emdate.sub_date(x['logon_day'], x['order_day']), axis=1)
    compress_date = compress_date.fillna(0)
    rd.delete_last_date(conn, write_db, write_tab, date_type_name, date)
    rd.insert_to_data(compress_date, conn, write_db, date_type_name)
    conn.close()


def count_order_test(num):
    sql = 'SELECT count(*) user_num FROM user_info.user_info_{num};'.format(num=num)
