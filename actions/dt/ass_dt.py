from datetime import date, datetime, timedelta
import time
import arrow
import dateparser


def get_day_delta(inquire_date):

    lookups = {'大前天': -3, '前天': -2, '昨天': -1,
               '今天': 0, '明天': 1, '后天': 2, '大后天': 3}

    day_delta = lookups.get(inquire_date, None)
    return day_delta


def get_date_by_entity(inquire_date=None):
    '''
    function: 给定实体,如果在lookups中则返回字符串格式的日期
    input: inquire_date in ['大前天', '前天', ...]
    output: strftime(string类型)的时间
    '''
    day_delta = get_day_delta(inquire_date)
    today_date = date.today()
    inquire_date = date(today_date.year, today_date.month,
                        today_date.day+day_delta)
    # inquire_week = inquire_date.weekday()
    # return (f'{inquire_date.year}年{inquire_date.month}月{inquire_date.day}日 星期{week_zh[inquire_week]}')
    return inquire_date.strftime('%Y-%m-%d %H:%M:%S %A')


def get_datetime(value):
    '''
    function:
        使用字符串格式的时间生成datetime格式
    input:
        datetime_str: "2021-03-02T00:00:00.000+08:00"
    output:
        datetime()
    '''
    if isinstance(value, str):
        value = value[:19]
        inquire_date = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
        return inquire_date
    else:
        return datetime.now()


def get_date_by_value(value, mode='datetime'):
    '''
    function: 生成'年-月-日 时:分:秒 星期'格式的字符串数据
    input: 输入str或者dict{'to': str, 'from': str}
    output: "2021-03-02 00:00:00 monday"
    '''
    if mode == 'datetime':
        fmt_res = '%Y-%m-%d %H:%M:%S %A'
    elif mode == 'date':
        fmt_res = '%Y-%m-%d'
    if isinstance(value, str):
        inquire_date = get_datetime(value)
    elif isinstance(value, dict):
        date_from = get_datetime(value['from'])
        date_to = get_datetime(value['to'])
        if date_from < datetime.today():  # n天前
            inquire_date = date_from
        else:
            inquire_date = date_to
    else:
        return datetime.now().strftime(fmt_res)

    return inquire_date.strftime(fmt_res)


city_db = {
    '伦敦': 'Europe/Dublin',
    '里斯本': 'Europe/Lisbon',
    '阿姆斯特丹': 'Europe/Amsterdam',
    '西雅图': 'US/Pacific',
    '上海': 'Asia/Shanghai',
    '纽约': 'America/New_York',
    '曼谷': 'Asia/Bangkok',
    '平壤': 'Asia/Pyongyang',
    '首尔': 'Asia/Seoul',
    '新加坡': 'Asia/Singapore',
    '台北': 'Asia/Taipei',
    '东京': 'Asia/Tokyo',
    '悉尼': 'Australia/Sydney',
    '雅典': 'Europe/Athens',
    '柏林': 'Europe/Berlin',
    '布鲁塞尔': 'Europe/Brussels',
    '罗马': 'Europe/Rome',
    '苏黎世': 'Europe/Zurich',
    '复活节岛': 'Chile/EasterIsland',
    '华沙': 'Europe/Warsaw',
    '巴黎': 'Europe/Paris',
    '布拉格': 'Europe/Prague',
    '马德里': 'Europe/Madrid',
    '太平洋': 'US/Pacific'
}

chinese_city = ['中国', '北京', '武汉', '上海', '沈阳', '重庆',
                '深圳', '广州', '杭州', '南京', '香港', '哈尔滨', '合肥', '宁波']


def normalize_city(city_name):
    if city_name in chinese_city:
        return '上海'
    else:
        return city_name


def get_time_by_entity(entity_place):
    '''
    function: 根据地区或国家名获取当地时间
    input: str 地区或国家名
    output: string
    '''
    print('entity is ', entity_place)
    zone_area = city_db.get(normalize_city(entity_place), None)

    if not zone_area:
        msg = f'非常抱歉，目前不支持{entity_place}地区的时间查询。'
    else:
        utc = arrow.utcnow()
        print(zone_area)
        area_time = utc.to(zone_area).format('YYYY-MM-DD HH:mm:ss dddd')
        msg = f"{entity_place}现在是 {area_time}"

    return msg


def get_time_by_value(value, mode='datetime'):
    '''
    function: 字符串类型时间转datetime格式
    input: string  "2021-03-02T00:00:00.000+08:00"
    output: datetime
    '''
    if mode == 'datetime':
        fmt_res = '%Y-%m-%d %H:%M:%S %A'
    elif mode == 'date':
        fmt_res = '%Y-%m-%d'

    if isinstance(value, str):
        inquire_date = get_datetime(value)
    elif isinstance(value, dict):
        date_from = get_datetime(value['from'])
        date_to = get_datetime(value['to'])

        if date_from < datetime.now():  # n天前
            inquire_date = date_from
        else:
            inquire_date = date_to
    else:
        return datetime.now().strftime(fmt_res)

    return inquire_date.strftime(fmt_res)


def get_place_time_different(place_list):
    if len(place_list) != 2:
        msg = f'您只提供了一个地理位置，无法进行时间差异的比较。'
    else:
        place0 = city_db.get(normalize_city(place_list[0]), None)
        place1 = city_db.get(normalize_city(place_list[1]), None)
        if place0 and place1:
            t0 = arrow.utcnow().to(place0)
            t1 = arrow.utcnow().to(place1)
            (max_t, min_t) = (t0, t1) if t0 > t1 else (t1, t0)
            diff_seconds = dateparser.parse(
                str(max_t)[:19]) - dateparser.parse(str(min_t)[:19])
            diff_hours = int(diff_seconds.seconds/3600)
            if t0 <= t1:
                msg = f"{place_list[0]}比{place_list[1]}晚{min(diff_hours, 24-diff_hours)}小时。"
            else:
                msg = f"{place_list[1]}比{place_list[0]}晚{min(diff_hours, 24-diff_hours)}小时。"
        else:
            msg = f'目前查询不到您所说的地理位置的时间'

    return msg


if __name__ == '__main__':
    print(get_date_by_value(None))
