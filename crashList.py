# coding=utf-8
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

# java崩溃类型：Crash，native崩溃类型: Native
def getIssueList(crashType, start = 0):
    url = "https://bugly.qq.com/v4/api/old/get-issue-list?start=" + str(start) + "&searchType=errorType&exceptionTypeList=" + crashType + "&pid=1&platformId=1&date=last_7_day&sortOrder=desc&version=" + needVersion + "&rows=" + crashListLimit +"&sortField=uploadTime&appId=" + appId + "&fsn=" + fsn
    response = requests.get(url, headers=headers)
    content = json.loads(response.content)
    checkData(content, 'getIssueList')
    return content


# 只要多拉几条记录必定会遇到500错误, 需要多重试几次
def getIssueListWithRetry(crashType):
    content = getIssueList(crashType)
    while content['code'] != 200:
        time.sleep(1)
        content = getIssueList(crashType)
    return content

#校验数据, 并打印错误数据
def checkData(data, tag):
    if data["code"] != 200:
        print ("[" + tag + "]", data)

# 获取聚合的崩溃列表记录
def getCrashList(issueId, rows):
    url = "https://bugly.qq.com/v4/api/old/get-crash-list?start=0&searchType=detail&exceptionTypeList=Crash,Native,ExtensionCrash&pid=1&crashDataType=unSystemExit&platformId=1&issueId=" + issueId + "&rows=" + rows + "&appId=" + appId + "&fsn=" + fsn
    response = requests.get(url, headers=headers)
    return response.content

# 计算聚合的崩溃数量
def getCrashNum(issueId):
    content = getCrashList(issueId, crashListLimit)
    crashList = json.loads(content)
    checkData(crashList, 'getCrashNum')
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

# 只要多拉几条记录必定会遇到500错误, 需要多重试几次
def getCrashNumWithTry(issueId):
    count = getCrashNum(issueId)
    while(count < 0):
        time.sleep(1)
        print ("try again getCrashNum")
        count = getCrashNum(issueId)

    print ({"issueId": issueId, "count": count})
    return count

# 时间戳转换成指定格式时间
def convertTime(timeStamp):
    time_local = time.localtime(timeStamp)
    dt = time.strftime("%Y-%m-%d", time_local)
    return dt


def converDataToTime(startTime, type):
    if (type == 1):
        format = '%Y-%m-%d %H:%M:%S %f'
    else:
        format = '%Y-%m-%d'

    # 转换成时间数组
    startTimeArray = time.strptime(startTime, format)
    # 转换成时间戳,单位秒
    startTimeStamp = time.mktime(startTimeArray)
    return startTimeStamp

# 计算指定时间间隔后的日期
def calucateTime(startTime, days):
    startTimeStamp = converDataToTime(startTime)
    return convertTime(startTimeStamp + (days * 24 * 60 * 60))

# 计算某个类型崩溃的数量
def getCrashTotalNum(crashType):
    crashTotalList = getIssueListWithRetry(crashType)
    issueTotalList = crashTotalList['data']['issueList']
    count = 0
    for issue in issueTotalList:
        # 过滤查询崩溃时间之前的崩溃
        lastestUploadTime = issue['lastestUploadTime']
        if converDataToTime(lastestUploadTime, 1) < converDataToTime(needUploadTime, 2):
            continue

        # print 'lastestUploadTime:' + lastestUploadTime
        count += getCrashNumWithTry(issue['issueId'])

    return count


javaCount = getCrashTotalNum("Crash")
nativeCount = getCrashTotalNum("Native")
print ("===============统计结果===================")
print ("nativeCount" + str(nativeCount) + ",java:" + str(javaCount))
print ({"NativeCrashNum": nativeCount,  "JavaCrashNum": javaCount, "TotalNum": nativeCount + javaCount, "time": needUploadTime, "version": needVersion })
