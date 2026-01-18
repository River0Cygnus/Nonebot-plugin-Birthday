from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="BdayAlert",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

from nonebot import require
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler
from nonebot import on_command
from nonebot.rule import to_me,is_type
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message
from nonebot import get_driver

import csv
import os
from datetime import datetime
from nonebot import get_bot
from nonebot.adapters.onebot.v11.bot import Bot

csv_list = ["Bday.csv","KeyBday.csv"]
my_qqnumber = 3531397447

def get_file_path(file_name) :
    # 获取当前工作目录
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # 拼接完整的文件路径
    file_path = os.path.join(current_directory, file_name)
    return file_path

# csv对象初始化
async def csv_init(file_name):
    file_path = get_file_path(file_name)
    if os.path.exists(file_path):
        return
    else:
        fieldnames = ['Name','Bday_time']
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            # 写入列名
            writer.writeheader()
            return
driver = get_driver()
# 初始化csv
@driver.on_startup
async def on_start():
    for csvi in csv_list:
        await csv_init(csvi)


async def Bday_enable() -> bool:
    # Bday功能是否开启
    return config.Bday_plugin_enabled


Bday = on_command("Bday",rule=Bday_enable,aliases={"生日","bday"},permission=SUPERUSER)
# Bday生日列表功能实现
@Bday.handle()
async def BdayAlert(args:Message = CommandArg()):
    command_arg = args.extract_plain_text().split()
    if "list" == command_arg[0]:
        # list功能实现
        file_path=get_file_path("Bday.csv")
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            current_time = datetime.now()
            current_year = current_time.year
            reader = csv.reader(file)
            next(reader)
            rows = list(reader)
            result = []
            # 将生日信息转换成日期对象
            for row in rows:
                Name = row[0]
                Bday_time = row[1]
                bday = datetime.strptime(Bday_time, "%Y.%m.%d")
                next_birthday = bday.replace(year=current_year)
                if next_birthday < current_time:
                    next_birthday = next_birthday.replace(year=current_year + 1)
                age_at_next_birthday = next_birthday.year - bday.year
                days_until_next_birthday = (next_birthday - current_time).days

                result.append({
                    "name": Name,
                    "next_birthday": next_birthday.strftime("%Y.%m.%d"),
                    "age_at_next_birthday": age_at_next_birthday,
                    "days_until_next_birthday": days_until_next_birthday
                })

                # 按照下一个生日的日期排序
                sorted_result = sorted(result, key=lambda x: datetime.strptime(x["next_birthday"], "%Y.%m.%d"))

                # 发送结果
                output = "\n".join([f"{person['name']}的{person['age_at_next_birthday']}岁生日是{person['next_birthday']},还有{person['days_until_next_birthday']}天"for person in sorted_result])

        await Bday.send(output)
        return
    if "add" == command_arg[0]:
        if len(command_arg)!=3:
            await Bday.send("指令格式发送错误！参数不等于2，请输入/Bday add Name xxxx.xx.xx")
            return

        Name = command_arg[1]
        Bday_time = command_arg[2]
        file_path = get_file_path("Bday.csv")
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:  # 使用 'a' 模式追加数据
            writer = csv.writer(file)
            # 写入一行数据
            writer.writerow([Name, Bday_time])
            await Bday.send(f"成功写入生日记录！\n{Name} {Bday_time}")
        return
    if "del" == command_arg[0]:
        Name = command_arg[1]
        file_path=get_file_path("Bday.csv")
        with open(file_path,mode='r',newline='',encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)
        rows_to_keep = [row for row in rows if row[0] != Name]
        if len(rows_to_keep)==len(rows):
            await Bday.send(f"未找到名称为{Name}的对象！")
            return
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(rows_to_keep)
        await Bday.send(f"{Name}已经成功从生日列表中删除！")
        return
    if "help" == command_arg[0]:
        help_data = "指令列表\n"
        help_data += "输入/bday 或/Bday 或/生日 以开始指令\n"
        help_data += "输入/bday list查看生日列表\n"
        help_data += "输入/bday add Name xxxx.xx.xx加入一个生日\n"
        help_data += "输入/bday del Name以删除一个生日\n"
        await Bday.send(help_data)

        return
async def Bday_caculation(file_name,bot:Bot):
    file_path = get_file_path(file_name)
    current_time = datetime.now()
    current_year = current_time.year
    exist_bday = 0
    result = ""
    with open(file_path,mode='r',newline='',encoding='utf-8')as file:
        reader = csv.reader(file)
        next(reader)
        rows = list(reader)
        for row in rows:
            Name = row[0]
            Bday_time = row[1]
            bday = datetime.strptime(Bday_time, "%Y.%m.%d")
            next_birthday = bday.replace(year=current_year)
            if next_birthday < current_time:
                next_birthday = next_birthday.replace(year=current_year + 1)
            days_until_next_birthday = (next_birthday - current_time).days
            if days_until_next_birthday <= 7:
                exist_bday = 1
                result+=f"{Name}的生日还剩{days_until_next_birthday}！快去准备祝福他吧！"

    if exist_bday ==0:
        return
    else:
        await bot.send_friend_message(target= my_qqnumber,message=result)
        return

@scheduler.scheduled_job("cron", hour="8", minute="0",second="0", id=f"job_every_day")
async def run_every_day_8_clock():
    bot: Bot = get_bot()
    await Bday_caculation("Bday.csv",bot)
    await bot.send_friend_message(target=my_qqnumber,message="主人，新的一天开始了！")
