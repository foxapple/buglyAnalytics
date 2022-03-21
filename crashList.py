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

f=open(r'bugly_cookie.txt','r')#打开所保存的cookies内容文件
headers = {
    'Cookie': f.readlines()[0]
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
