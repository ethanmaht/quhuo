import datetime as dt


def fixed_length(_s, length=2, fixed="0", behind=None):
    _s = str(_s)
    _len = length - len(_s)
    if _len > 0:
        _fixed = fixed * _len
        if behind:
            return _s + _fixed
        return _fixed + _s
    return _s


def timestamp_to_datetime(ts_date):
    if isinstance(ts_date, int):
        return dt.datetime.fromtimestamp(ts_date)
    if isinstance(ts_date, str):
        try:
            ts_date = int(ts_date)
        except:
            ts_date = 0
        return dt.datetime.fromtimestamp(ts_date)


def datetime_to_int(_dt, date_day=None, date_time=None, time_int=None):
    if date_day:
        return _dt.year * 10000 + _dt.month * 100 + _dt.day
    if date_time:
        return _dt.hour * 10000 + _dt.minute * 100 + _dt.second
    if time_int:
        return _dt.hour * 3600 + _dt.minute * 60 + _dt.second


def datetime_format(
        _dt, repair=1, date_day=None, date_month=None,
        date_time=None, date_hour=None, date_minute=None, format_sign="-"
):
    _year = _dt.year
    if repair:
        _month = fixed_length(_dt.month, )
        _day = fixed_length(_dt.day, )
        _hour = fixed_length(_dt.hour)
        _minute = fixed_length(_dt.minute)
        _second = fixed_length(_dt.second)
    else:
        _month, _day, _hour, _minute, _second = _dt.month, _dt.day, _dt.hour, _dt.minute, _dt.second
    if date_day:
        return "{Y}{si}{M}{si}{D}".format(Y=_year, M=_month, D=_day, si=format_sign)
    if date_month:
        return "{Y}{si}{M}".format(Y=_year, M=_month, si=format_sign)
    if date_time:
        return "{Y}{si}{M}{si}{D} {H}:{m}:{s}".format(
            Y=_year, M=_month, D=_day, H=_hour, m=_minute, s=_second, si=format_sign
        )
    if date_hour:
        return "{Y}{si}{M}{si}{D} {H}".format(
            Y=_year, M=_month, D=_day, H=_hour, si=format_sign
        )
    if date_minute:
        return "{Y}{si}{M}{si}{D} {H}:{m}".format(
            Y=_year, M=_month, D=_day, H=_hour, m=_minute, si=format_sign
        )
    return "--"


def datetime_format_code(_dt, repair=1, code='{Y}-{M}-{D}'):
    if not code:
        return _dt
    if isinstance(_dt, str):
        _dt = dt.datetime.strptime(_dt, "%Y-%m-%d")
    _year = _dt.year
    if repair:
        _month = fixed_length(_dt.month, )
        _day = fixed_length(_dt.day, )
        _hour = fixed_length(_dt.hour)
        _minute = fixed_length(_dt.minute)
        _second = fixed_length(_dt.second)
    else:
        _month, _day, _hour, _minute, _second = _dt.month, _dt.day, _dt.hour, _dt.minute, _dt.second
    wd, mw, nmw = _dt.weekday(), month_week(_dt), month_week(_dt, natural=1)
    yw, nyw = year_week(_dt), year_week(_dt, natural=1)
    return code.format(
        Y=_year, M=_month, D=_day, h=_hour, m=_minute, s=_second, wd=wd, mw=mw, nmw=nmw, yw=yw, nyw=nyw
    )


def date_num_dict(date, days):
    date = dt.datetime.strptime(str(date), "%Y-%m-%d")
    date_dict = {}
    for _ in range(days):
        _day = _ + 1
        _date = date + dt.timedelta(days=_day)
        date_dict.update({datetime_format_code(_date, code='{Y}-{M}-{D}'): str(_day+1)})
    return date_dict


def date_list(s_date, e_date=None, num=None, format_code=None, direction=0):
    if isinstance(s_date, str):
        s_date = dt.datetime.strptime(s_date.split(' ')[0], "%Y-%m-%d")
    if isinstance(e_date, str):
        e_date = dt.datetime.strptime(e_date.split(' ')[0], "%Y-%m-%d")
    _list, _ = [], s_date
    if num:
        if isinstance(num, list):
            num = num
        if isinstance(num, int):
            num = range(abs(num))
        if direction:
            for _num in num:
                _ = s_date + dt.timedelta(days=_num - 1)
                _dt = datetime_format_code(_, code=format_code)
                _list.append(_dt)
            return _list
        for _num in num:
            _ = s_date - dt.timedelta(days=_num-1)
            _dt = datetime_format_code(_, code=format_code)
            _list.append(_dt)
        return _list
    if e_date:
        while _ <= e_date:
            _dt = datetime_format_code(_, code=format_code)
            _list.append(_dt)
            _ = _ + dt.timedelta(days=1)
        return _list
    return [s_date]


def year_week(_dt, natural=0):
    year_s = dt.datetime(_dt.year, 1, 1)
    _day = (_dt - year_s).days
    if natural:
        return _day // 7 + 1
    year_s_wd = dt.datetime(_dt.year, 1, 1).weekday()
    return (_day - year_s_wd) // 7 + 1


def month_week(_dt, natural=0):
    month_s = dt.datetime(_dt.year, _dt.month, 1)
    _day = (_dt - month_s).days
    if natural:
        return _day // 7 + 1
    month_s_wd = dt.datetime(_dt.year, _dt.month, 1).weekday()
    return (_day - month_s_wd) // 7 + 1


def sub_date(s_date, e_date, types='day'):
    if isinstance(s_date, str):
        s_date = dt.datetime.strptime(s_date, '%Y-%m-%d')
    if isinstance(e_date, str):
        e_date = dt.datetime.strptime(e_date, '%Y-%m-%d')
    sub = e_date - s_date
    types_dict = {
        'hour': sub.total_seconds() / 3600,
        'minute': sub.total_seconds() / 60,
        'second': sub.total_seconds(),
        'day': sub.days
    }
    if types in types_dict.keys():
        return types_dict[types]
    return types_dict['day']
