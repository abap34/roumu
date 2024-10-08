import datetime
import json
import re

# import doctest
import sys
import uuid
import warnings
from typing import Callable, Union

import dateutil.relativedelta

ABSOLUTE_TIME_PETTERNS = [
    # 2020/01/02 23:59:59
    r"(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2}) (?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2})",
    # 2020/01/02
    r"(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})",
    # 01/02 23:59:59
    r"(?P<month>\d{1,2})/(?P<day>\d{1,2}) (?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2})",
    # 01/02
    r"(?P<month>\d{1,2})/(?P<day>\d{1,2})",
    # 23:59:59
    r"(?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2})",
    # 23:59
    r"(?P<hour>\d{1,2}):(?P<minute>\d{1,2})",
]


def find_absolute_time(
    body: str,
    current_time_getter: Callable[[], datetime.datetime] = datetime.datetime.now,
) -> Union[datetime.datetime, None]:
    """
    find_absolute_time(body: str) -> datetime.datetime

    body から絶対時刻表現を抽出する. 絶対時刻表現が見つからない場合は None を返す.

    Input
    -----
    body: str
        コメントの本文

    current_time_getter: Callable[[], datetime.datetime]
        現在時刻を取得する関数

    Output
    ------
    time: datetime.datetime
        絶対時刻

    Examples
    --------
    >>> find_absolute_time("2020/01/02 23:59:59", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    datetime.datetime(2020, 1, 2, 23, 59, 59)

    >>> find_absolute_time("2020/01/02", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    datetime.datetime(2020, 1, 2, 0, 0)

    >>> find_absolute_time("01/02 23:59:59", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    datetime.datetime(2004, 1, 2, 23, 59, 59)

    >>> find_absolute_time("01/02", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    datetime.datetime(2004, 1, 2, 0, 0)

    >>> find_absolute_time("23:59:59", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    datetime.datetime(2004, 3, 4, 23, 59, 59)

    >>> find_absolute_time("23:59", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    datetime.datetime(2004, 3, 4, 23, 59)

    >>> find_absolute_time("あああ", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    """

    for pattern in ABSOLUTE_TIME_PETTERNS:
        match = re.search(pattern, body)
        if match:
            current_time = current_time_getter()
            # 分まで 0 にする
            current_time = current_time.replace(minute=0, second=0, microsecond=0)
            for k in ["year", "month", "day", "hour", "minute", "second"]:
                if k in match.groupdict():
                    current_time = current_time.replace(**{k: int(match.group(k))})
            return current_time

    return None


def find_relative_time(
    body: str, current_time_getter=datetime.datetime.now
) -> Union[datetime.datetime, None]:
    """
    find_relative_time(body: str) -> datetime.datetime

    body から相対時刻表現を抽出する. 相対時刻表現が見つからない場合は None を返す.


    Input
    -----
    body: str
        コメントの本文

    current_time_getter: Callable[[], datetime.datetime]
        現在時刻を取得する関数

    Output
    ------
    time: datetime.datetime
        相対時刻

    Examples
    --------
    >>> find_relative_time("今日", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    datetime.datetime(2004, 3, 4, 23, 59, 59)

    >>> find_relative_time("明日", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    datetime.datetime(2004, 3, 5, 23, 59, 59)

    >>> find_relative_time("明後日", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    datetime.datetime(2004, 3, 6, 23, 59, 59)

    >>> find_relative_time("今週", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    datetime.datetime(2004, 3, 7, 23, 59, 59)

    >>> find_relative_time("来週", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    datetime.datetime(2004, 3, 14, 23, 59, 59)

    >>> find_relative_time("今月", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    datetime.datetime(2004, 3, 31, 23, 59, 59)

    >>> find_relative_time("3日後", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    datetime.datetime(2004, 3, 7, 23, 59, 59)

    >>> find_relative_time("あああ", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    """
    current_time = current_time_getter()
    end_of_today = current_time.replace(hour=23, minute=59, second=59, microsecond=0)

    if "今日" in body:
        # 今日の 23:59:59. 明日の 0:00:00 から 1秒引いたものを返す
        return end_of_today

    if "明日" in body:
        # 明日の 23:59:59
        return end_of_today + dateutil.relativedelta.relativedelta(days=1)

    if "明後日" in body:
        # 明後日の 23:59:59
        return end_of_today + dateutil.relativedelta.relativedelta(days=2)
    if "今週" in body:
        # 今週の日曜日の 23:59:59
        return end_of_today + dateutil.relativedelta.relativedelta(
            weekday=dateutil.relativedelta.SU
        )

    if "来週" in body:
        return end_of_today + dateutil.relativedelta.relativedelta(
            weekday=dateutil.relativedelta.SU, weeks=1
        )

    if "今月" in body:
        return (
            end_of_today.replace(day=1)
            + dateutil.relativedelta.relativedelta(months=1)
            - dateutil.relativedelta.relativedelta(days=1)
        )

    match = re.search(r"(\d+)日後", body)

    if match:
        return end_of_today + dateutil.relativedelta.relativedelta(
            days=int(match.group(1))
        )

    return None


def find_weekday_week(
    body: str, current_time_getter=datetime.datetime.now
) -> Union[datetime.datetime, None]:
    """
    find_weekday(body: str, current_time_getter=datetime.datetime.now) -> Union[datetime.datetime, None]

    body から曜日 + 週指定 (e.g. 来週の月曜日) を抽出する.
    木曜日に 「今週の水曜日」のような表現は不正とみなして無視する.

    Input
    -----
    body: str
        コメントの本文

    current_time_getter: Callable[[], datetime.datetime]
        現在時刻を取得する関数

    Output
    ------
    time: int
        曜日 + 週指定された時刻

    Examples
    --------
    >>> find_weekday_week("今週の金曜日", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0)) # 2004/3/4 は木曜日
    datetime.datetime(2004, 3, 5, 23, 59, 59)

    >>> find_weekday_week("今週の月曜日", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))

    >>> find_weekday_week("来週の月曜日", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    datetime.datetime(2004, 3, 15, 23, 59, 59)

    >>> find_weekday_week("来週の火曜日", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    datetime.datetime(2004, 3, 16, 23, 59, 59)

    >>> find_weekday_week("来週の水曜日", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    datetime.datetime(2004, 3, 17, 23, 59, 59)

    >>> find_weekday_week("来週の木曜日", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    datetime.datetime(2004, 3, 18, 23, 59, 59)

    >>> find_weekday_week("2週後の金曜日", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    datetime.datetime(2004, 3, 19, 23, 59, 59)

    >>> find_weekday_week("金曜日", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))

    >>> find_weekday_week("あああ", current_time_getter=lambda: datetime.datetime(2004, 3, 4, 0, 0, 0))
    """
    current_time = current_time_getter()

    # まず曜日表現を抽出
    weekday = None
    for i, w in enumerate(["月", "火", "水", "木", "金", "土", "日"]):
        if w in body:
            weekday = i
            break

    if weekday is None:
        return None

    for expression in ["今週", "来週", "再来週"]:
        if expression in body:
            if expression == "今週" and weekday < current_time.weekday():
                warnings.warn(
                    "今週の過去の曜日を指定しています. 過去の曜日を指定することはできません.スキップします."
                )
                continue
            end_of_today = current_time.replace(
                hour=23, minute=59, second=59, microsecond=0
            )

            weeks = ["今週", "来週", "再来週"].index(expression)

            if weekday == current_time.weekday():
                weeks += 1

            return end_of_today + dateutil.relativedelta.relativedelta(
                weekday=dateutil.relativedelta.weekday(weekday),
                weeks=weeks,
            )

    # 「n週」 が含まれている場合
    match = re.search(r"(\d+)週", body)
    if match:
        current_time = current_time_getter()
        end_of_today = current_time.replace(
            hour=23, minute=59, second=59, microsecond=0
        )
        return end_of_today + dateutil.relativedelta.relativedelta(
            weekday=dateutil.relativedelta.weekday(weekday), weeks=int(match.group(1))
        )

    return None


def extract_deadline(
    body: str, current_time_getter=datetime.datetime.now
) -> datetime.datetime:
    """
        extract_deadline(body: str, current_time_getter=datetime.datetime.now) -> datetime.datetime

        body からタスクの期限を抽出する.
        発見されなかったら 3000/01/01 00:00:00 を返す.

    Input
    -----
    body: str
        コメントの本文

    current_time_getter: Callable[[], datetime.datetime]
        現在時刻を取得する関数

    Output
    ------
    deadline: datetime.datetime
        タスクの期限

    Examples
    --------
    >>> extract_deadline("今日")
    datetime.datetime(2004, 3, 4, 23, 59, 59)

    >>> extract_deadline("あああ")
    datetime.datetime(3000, 1, 1, 0, 0)
    """

    # 絶対時刻表現を抽出
    time = find_absolute_time(body, current_time_getter)
    if time:
        return time

    # 曜日 + 週指定を抽出
    time = find_weekday_week(body, current_time_getter)
    if time:
        return time

    # 相対時刻表現を抽出
    time = find_relative_time(body, current_time_getter)
    if time:
        return time

    return datetime.datetime(3000, 1, 1, 0, 0)


class AnyValue:
    def __str__(self):
        return "*"
    
class MultipleValue:
    def __init__(self, n: int):
        self.n = n

    def __str__(self):
        return f"*/{self.n}"


class CronElement:
    def __init__(self, value: Union[int, AnyValue, MultipleValue]):
        self.value = value

    def __str__(self):
        return str(self.value)


class CronSetting:
    def __init__(
        self,
        minute: CronElement,
        hour: CronElement,
        day: CronElement,
        month: CronElement,
    ):
        self.minute = minute
        self.hour = hour
        self.day = day
        self.month = month

    def __str__(self):
        return f"{self.minute} {self.hour} {self.day} {self.month}"


def extract_remind(body: str, current_time_getter=datetime.datetime.now) -> CronSetting:
    """
    extract_remind(body: str, current_time_getter=datetime.datetime.now) -> str

    body からリマインドの間隔を抽出する。

    今は 期日までの毎日朝 8:00 にリマインドするという形式のみ対応
    """
    return CronSetting(
        CronElement(0),
        CronElement(8),
        CronElement(AnyValue()),
        CronElement(AnyValue()),
    )


def gen_reminder(body: str, issue_number: int) -> None:
    """
        gen_reminder(body: str, issue_number: int) -> None

        issue_number についた中身が body のリマインドコメントのリマインド用 json を生成する

    Input
    -----
    issue_number: int
        コメントがついた issue の番号
    body: str
        リマインドの内容

    Output
    ------
    None

    """
    task, deadline, remind, _ = body.split("\n")

    if not "/remind" in body:
        return

    with open("reminds/tasks.json", "r") as f:
        tasks = json.load(f)

    tasks.append(
        {
            "id": str(uuid.uuid4()),
            "task": task,
            "issue_number": issue_number,
            "deadline": extract_deadline(deadline).isoformat(),
            "remind": str(extract_remind(remind)),
        }
    )

    with open("reminds/tasks.json", "w") as f:
        json.dump(tasks, f, indent=4)


if __name__ == "__main__":
    # doctest.testmod()
    # body = sys.argv[1]
    # issue_number = int(sys.argv[2])
    # gen_reminder(body, issue_number)

    gen_reminder(
        "タスク\n今日\n/remind\n",
        1,
    )
