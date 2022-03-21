# coding=utf-8
# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import requests
import json
import time


# 查询的崩溃时间
needUploadTime = "2022-03-17"
# 筛选目标版本
needVersion = "11.5.0"
# 聚合的崩溃列表一页的数量, 官方接口支持, 前100基本可以算出当天当前崩溃数量
crashListLimit = '100'

appId = "900003680"
fsn = "a290e7d4-e2bf-48d7-acd9-8ed78d22e8bf"
# cookie需要自己更新
headers = {
    'Cookie': 'RK=bdLVRJHrQc; ptcz=9834a1b98a93eafca235d7834b29eeb1cba7816ce8724749564f75f0e77280fc; pgv_pvid=2430764280; sd_userid=71921623320981549; sd_cookie_crttime=1623320981549; btcu_id=3abf56e28926d97c8700d0cb4bbbea4e60cc4552c350e; pac_uid=0_feb7af1038474; ptui_loginuin=361197128; uin=o0361197128; pgv_info=ssid=s1776488448; skey=@VVhv9nPrE; bugly-session=s%3A0Y75LZvjpkL-EUTCSz1TqpSl5n_Lsbxy.HJeNo7yrZy3fgFk9y46u6DRvDhavzni1nWbUz%2FK0Zcc; connect.sid=s%3AAouz8hY8VzHa5edTVQr9vcC5tVSRGzyZ.RF4HSpQWLc1qc8EFvfFYW%2FEqlk6tAgzSy6HrXj9G4m4; vc=vc-95eb4832-c369-411e-90d6-582b9abcaf85; btcu_id=1dbf8d54-59ba-4bcd-b55c-2bbd65bd7dc0; token-skey=4a2ea2d4-14df-7131-6e49-14cbe6479d6c; token-lifeTime=1647609295; referrer=eyJpdiI6IkErQjBSaWJRSkVTaWg1XC9nSzYyTnhRPT0iLCJ2YWx1ZSI6IkE3WmdrUEFhTGxvdm5oWXN3MDI5d2lyc2twdkVsY3IzU2ZsN0RvVFdoVjNYK2FiVXAySUszWVl1R01nSkJabDhGbWkyMTB0ZWRRRXNEa2Z4bjgyWENIaXVuUGZpQ2ZTa1NwQmFBUkRLOTVONlJZUGJvRUROS2MrRHd1aDNcL1ljM3l5R2R1Z1J5WklEYzBra2M5Q1BXTE14YnpkYWdQcGJHZENxeWtKV2ZNakhcL2QrNk5FQ05ZTnBNZEc4N2I2VG9xbm5idHZKOUc0elZLeE1taElsNEhMZXhwVWVkWTZSZ2RzK1dzVkF0SlVCMD0iLCJtYWMiOiJlZWU1NjEzNWI5ZWRlNjIxZmNiYmExNmQ5ZjdkODU0ZmE0YjIwZjc3MmZhOWRlOWI5NjFmMTRjNmNhY2ZlYmYyIn0%3D; bugly_session=eyJpdiI6Ijk4YmJZUlFtRlpjancyUUFYNGE2eGc9PSIsInZhbHVlIjoiR05TV282OHpmV0NHTnpwemVRYWI2THpFUE5HWXJPWjRjWnhDQVFXbXZoWXQ4SWttZVZ1ZFRxdlJMdHlkbGRyeHg2a1UrVjVLcVJmRlpLWnB0NjBWV0E9PSIsIm1hYyI6IjIzZDJhNmMzYWRkYTY5NTQ0YmM3YmRiYTA1MWUzN2I0OGUwMjRmOWMwMTRjMTNiYWEzMGE0YzcxMzBiMDIxYjAifQ%3D%3D; _dd_s=logs=1&id=3c61d8e6-2c76-4c04-a354-60df3145817c&created=1647588882246&expire=1647595753431'
}

# 获取聚合的崩溃列表记录
def getCrashList(issueId, rows):
    url = "https://bugly.qq.com/v4/api/old/get-crash-list?start=0&searchType=detail&exceptionTypeList=Crash,Native,ExtensionCrash&pid=1&crashDataType=unSystemExit&platformId=1&issueId=" + issueId + "&rows=" + rows + "&appId=c0f5bcfee9&fsn=6db6d0ba-6874-4f58-875b-3de08f52eb87"
    response = requests.get(url, headers=headers)
    return response.content


# 计算聚合的崩溃数量
def getCrashNum(issueId):
    content = getCrashList(issueId, crashListLimit)
    crashList = json.loads(content)
    # print content
    print ("getCrashNum before:" + issueId)
    if crashList["code"] != 200:
        print (content)
        return -1

    data = crashList["data"]
    crashIdList = data["crashIdList"]
    crashDatas = data["crashDatas"]

    count = 0
    for list in crashIdList:
        crashDataItem = crashDatas[list]
        productVersion = crashDataItem["productVersion"]
        uploadTime = crashDataItem["uploadTime"]
        if (productVersion == needVersion) & (needUploadTime in uploadTime):
            count += 1

    return count

#获取当天Top的崩溃堆栈
def getTopCrashList(limit):
    url = "https://bugly.qq.com/v4/api/old/get-top-issue?appId=" + appId + "&pid=1&version=4.4.8.0&type=crash&date=20211206&limit=" + limit + "&topIssueDataType=unSystemExit&fsn=" + fsn
    response = requests.get(url, headers=headers)
    return response.content

# 只要多拉几条记录必定会遇到500错误, 需要多重试几次
def getCrashNumWithTry(issueId):
    count = getCrashNum(issueId)
    while(count < 0):
        time.sleep(1)
        print ("try again getCrashNum")
        count = getCrashNum(issueId)
    return count

#获取当天Top80的崩溃数量
def getTopCrashTotalNum():
    topData = getTopCrashList(crashTopLimit)
    topData = json.loads(topData)
    topIssueList = topData["data"]["data"]["topIssueList"]
    totalNum = 0
    nativeNum = 0
    javaNum = 0
    print ("=========topIssueList size: " + str(len(topIssueList)) + "============")
    for issue in topIssueList:
        issueId = issue["issueId"]
        exceptionName = issue["exceptionName"]
        keyStack = issue["keyStack"]
        num = getCrashNumWithTry(str(issueId))
        totalNum += num
        # 分别计算native和java崩溃数量
        if exceptionName.startswith("SIG"):
            nativeNum += num
        else:
            javaNum += num
        print ("nativeNum: " + str(nativeNum))
        result = {"issueId": issueId, "exceptionName": exceptionName, "keyStack": keyStack, "crashNum": num}
        print (result)

    return {"totalNum": totalNum, "nativeNum": nativeNum, "javaNum": javaNum}

totalNum = getTopCrashTotalNum()

print ("===============统计结果===================")
print (str(totalNum) + ",time: " + needUploadTime + ",version: " + needVersion)