#coding:utf-8
import base64, copy, logging, os, sys, time, xlrd, json, datetime, configparser
from django.http import JsonResponse
from django.apps import apps
import numbers
from collections import defaultdict
from django.db.models.aggregates import Count,Sum
from django.db.models import Case, When, IntegerField, F
from django.forms import model_to_dict
import requests
from util.CustomJSONEncoder import CustomJsonEncoder
from .models import ecommercedata
from util.codes import *
from urllib.parse import unquote
from util.auth import Auth
from util.common import Common
import util.message as mes
from django.db import connection
import random
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect
from django.db.models import Q
from util.baidubce_api import BaiDuBce
from .config_model import config
import pandas as pd


def ecommercedata_default(request):

    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code,"msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")
        req_dict.update({"isdefault":"是"})
        data=ecommercedata.getbyparams(ecommercedata, ecommercedata, req_dict)
        if len(data)>0:
            msg['data']  = data[0]
        else:
            msg['data']  = {}
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def ecommercedata_page(request):
    '''
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code,  "data":{"currPage":1,"totalPage":1,"total":1,"pageSize":10,"list":[]}}
        req_dict = request.session.get("req_dict")
        global ecommercedata
        #当前登录用户信息
        tablename = Auth().getTokenInfo(request).get('tablename')

        msg['data']['list'], msg['data']['currPage'], msg['data']['totalPage'], msg['data']['total'], \
        msg['data']['pageSize']  =ecommercedata.page(ecommercedata, ecommercedata,req_dict, request)
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def ecommercedata_autoSort(request):
    '''
    ．智能推荐功能(表属性：[intelRecom（是/否）],新增clicktime[前端不显示该字段]字段（调用info/detail接口的时候更新），按clicktime排序查询)
主要信息列表（如商品列表，新闻列表）中使用，显示最近点击的或最新添加的5条记录就行
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code,  "data":{"currPage":1,"totalPage":1,"total":1,"pageSize":10,"list":[]}}
        req_dict = request.session.get("req_dict")
        if "clicknum"  in ecommercedata.getallcolumn(ecommercedata,ecommercedata):
            req_dict['sort']='clicknum'
        elif "browseduration"  in ecommercedata.getallcolumn(ecommercedata,ecommercedata):
            req_dict['sort']='browseduration'
        else:
            req_dict['sort']='clicktime'
        req_dict['order']='desc'
        msg['data']['list'], msg['data']['currPage'], msg['data']['totalPage'], msg['data']['total'], \
        msg['data']['pageSize']  = ecommercedata.page(ecommercedata,ecommercedata, req_dict)

        return JsonResponse(msg, encoder=CustomJsonEncoder)

#分类列表
def ecommercedata_lists(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code,  "data":[]}
        msg['data'],_,_,_,_  = ecommercedata.page(ecommercedata, ecommercedata, {})
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def ecommercedata_query(request):
    '''
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        try:
            query_result = ecommercedata.objects.filter(**request.session.get("req_dict")).values()
            msg['data'] = query_result[0]
        except Exception as e:

            msg['code'] = crud_error_code
            msg['msg'] = f"发生错误：{e}"
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def ecommercedata_list(request):
    '''
    前台分页
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code,  "data":{"currPage":1,"totalPage":1,"total":1,"pageSize":10,"list":[]}}
        req_dict = request.session.get("req_dict")
        #获取全部列名
        columns=  ecommercedata.getallcolumn( ecommercedata, ecommercedata)
        if "vipread" in req_dict and "vipread" not in columns:
          del req_dict["vipread"]
        #表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
        try:
            __foreEndList__=ecommercedata.__foreEndList__
        except:
            __foreEndList__=None
        try:
            __foreEndListAuth__=ecommercedata.__foreEndListAuth__
        except:
            __foreEndListAuth__=None

        #authSeparate
        try:
            __authSeparate__=ecommercedata.__authSeparate__
        except:
            __authSeparate__=None

        if __foreEndListAuth__ =="是" and __authSeparate__=="是":
            tablename=Auth().getTokenInfo(request).get('tablename')
            if tablename!="users" and Auth().getTokenInfo(request).get('params') is not None:
                req_dict['userid']=Auth().getTokenInfo(request).get('params').get("id")

        tablename = Auth().getTokenInfo(request).get('tablename')
        if tablename == "users" and req_dict.get("userid") != None:#判断是否存在userid列名
            del req_dict["userid"]
        else:
            __isAdmin__ = None

            allModels = apps.get_app_config('main').get_models()
            for m in allModels:
                if m.__tablename__==tablename:

                    try:
                        __isAdmin__ = m.__isAdmin__
                    except:
                        __isAdmin__ = None
                    break

            if __isAdmin__ == "是":
                if req_dict.get("userid"):
        # del req_dict["userid"]
                    pass
            else:
    #非管理员权限的表,判断当前表字段名是否有userid
                if "userid" in columns:
                    try:
                        pass
                    except:
                        pass
        #当列属性authTable有值(某个用户表)[该列的列名必须和该用户表的登陆字段名一致]，则对应的表有个隐藏属性authTable为”是”，那么该用户查看该表信息时，只能查看自己的
        try:
            __authTables__=ecommercedata.__authTables__
        except:
            __authTables__=None

        if __authTables__!=None and  __authTables__!={} and __foreEndListAuth__=="是":
            for authColumn,authTable in __authTables__.items():
                if authTable==tablename:
                    try:
                        del req_dict['userid']
                    except:
                        pass
                    params = Auth().getTokenInfo(request).get('params')
                    req_dict[authColumn]=params.get(authColumn)
                    username=params.get(authColumn)
                    break
        
        if ecommercedata.__tablename__[:7]=="discuss":
            try:
                del req_dict['userid']
            except:
                pass

        q = Q()
        msg['data']['list'], msg['data']['currPage'], msg['data']['totalPage'], msg['data']['total'], \
        msg['data']['pageSize']  = ecommercedata.page(ecommercedata, ecommercedata, req_dict, request, q)
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def ecommercedata_save(request):
    '''
    后台新增
    '''
    request.funname = __name__+"."+ecommercedata_save.__name__
    request.operation = "新增电商数据"
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")
        if 'clicktime' in req_dict.keys():
            del req_dict['clicktime']
        tablename=Auth().getTokenInfo(request).get('tablename')
        __isAdmin__ = None
        allModels = apps.get_app_config('main').get_models()
        for m in allModels:
            if m.__tablename__==tablename:

                try:
                    __isAdmin__ = m.__isAdmin__
                except:
                    __isAdmin__ = None
                break

        #获取全部列名
        columns=  ecommercedata.getallcolumn( ecommercedata, ecommercedata)
        if tablename!='users' and req_dict.get("userid")==None and 'userid' in columns  and __isAdmin__!='是':
            params=Auth().getTokenInfo(request).get('params')
            req_dict['userid']=params.get('id')


        if 'addtime' in req_dict.keys():
            del req_dict['addtime']

        idOrErr= ecommercedata.createbyreq(ecommercedata,ecommercedata, req_dict)
        if idOrErr is Exception:
            msg['code'] = crud_error_code
            msg['msg'] = idOrErr
        else:
            msg['data'] = idOrErr

        return JsonResponse(msg, encoder=CustomJsonEncoder)

def ecommercedata_add(request):
    '''
    前台新增
    '''
    request.funname = __name__+"."+ecommercedata_add.__name__
    request.operation = "新增电商数据"
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")
        tablename=Auth().getTokenInfo(request).get('tablename')

        #获取全部列名
        columns=  ecommercedata.getallcolumn( ecommercedata, ecommercedata)
        try:
            __authSeparate__=ecommercedata.__authSeparate__
        except:
            __authSeparate__=None

        if __authSeparate__=="是":
            tablename=Auth().getTokenInfo(request).get('tablename')
            if tablename!="users" and 'userid' in columns:
                try:
                    req_dict['userid']=Auth().getTokenInfo(request).get('params').get("id")
                except:
                    pass

        try:
            __foreEndListAuth__=ecommercedata.__foreEndListAuth__
        except:
            __foreEndListAuth__=None

        if __foreEndListAuth__ and __foreEndListAuth__!="否":
            tablename=Auth().getTokenInfo(request).get('tablename')
            if tablename!="users":
                req_dict['userid']=Auth().getTokenInfo(request).get('params').get("id")


        if 'addtime' in req_dict.keys():
            del req_dict['addtime']
        error= ecommercedata.createbyreq(ecommercedata,ecommercedata, req_dict)
        if error is Exception:
            msg['code'] = crud_error_code
            msg['msg'] = error
        else:
            msg['data'] = error
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def ecommercedata_thumbsup(request,id_):
    '''
     点赞：表属性thumbsUp[是/否]，刷表新增thumbsupnum赞和crazilynum踩字段，
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")
        id_=int(id_)
        type_=int(req_dict.get("type",0))
        rets=ecommercedata.getbyid(ecommercedata,ecommercedata,id_)

        update_dict={
        "id":id_,
        }
        if type_==1:#赞
            update_dict["thumbsupnum"]=int(rets[0].get('thumbsupnum'))+1
        elif type_==2:#踩
            update_dict["crazilynum"]=int(rets[0].get('crazilynum'))+1
        error = ecommercedata.updatebyparams(ecommercedata,ecommercedata, update_dict)
        if error!=None:
            msg['code'] = crud_error_code
            msg['msg'] = error
        return JsonResponse(msg, encoder=CustomJsonEncoder)


def ecommercedata_info(request,id_):
    '''
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}

        data = ecommercedata.getbyid(ecommercedata,ecommercedata, int(id_))
        if len(data)>0:
            msg['data']=data[0]
            if msg['data'].__contains__("reversetime"):
                if isinstance(msg['data']['reversetime'], datetime.datetime):
                    msg['data']['reversetime'] = msg['data']['reversetime'].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    if msg['data']['reversetime'] != None:
                        reversetime = datetime.datetime.strptime(msg['data']['reversetime'], '%Y-%m-%d %H:%M:%S')
                        msg['data']['reversetime'] = reversetime.strftime("%Y-%m-%d %H:%M:%S")

        #浏览点击次数
        try:
            __browseClick__= ecommercedata.__browseClick__
        except:
            __browseClick__=None

        if __browseClick__=="是"  and  "clicknum"  in ecommercedata.getallcolumn(ecommercedata,ecommercedata):
            try:
                clicknum=int(data[0].get("clicknum",0))+1
            except:
                clicknum=0+1
            click_dict={"id":int(id_),"clicknum":clicknum,"clicktime":datetime.datetime.now()}
            ret=ecommercedata.updatebyparams(ecommercedata,ecommercedata,click_dict)
            if ret!=None:
                msg['code'] = crud_error_code
                msg['msg'] = ret
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def ecommercedata_detail(request,id_):
    '''
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}

        data =ecommercedata.getbyid(ecommercedata,ecommercedata, int(id_))
        if len(data)>0:
            msg['data']=data[0]
            if msg['data'].__contains__("reversetime"):
                if isinstance(msg['data']['reversetime'], datetime.datetime):
                    msg['data']['reversetime'] = msg['data']['reversetime'].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    if msg['data']['reversetime'] != None:
                        reversetime = datetime.datetime.strptime(msg['data']['reversetime'], '%Y-%m-%d %H:%M:%S')
                        msg['data']['reversetime'] = reversetime.strftime("%Y-%m-%d %H:%M:%S")

        #浏览点击次数
        try:
            __browseClick__= ecommercedata.__browseClick__
        except:
            __browseClick__=None

        if __browseClick__=="是"   and  "clicknum"  in ecommercedata.getallcolumn(ecommercedata,ecommercedata):
            try:
                clicknum=int(data[0].get("clicknum",0))+1
            except:
                clicknum=0+1
            click_dict={"id":int(id_),"clicknum":clicknum,"clicktime":datetime.datetime.now()}

            ret=ecommercedata.updatebyparams(ecommercedata,ecommercedata,click_dict)
            if ret!=None:
                msg['code'] = crud_error_code
                msg['msg'] = ret
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def ecommercedata_update(request):
    '''
    '''
    request.funname = __name__+"."+ecommercedata_update.__name__
    request.operation = "更新电商数据"
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")
        if 'clicktime' in req_dict.keys() and req_dict['clicktime']=="None":
            del req_dict['clicktime']
        if req_dict.get("mima") and "mima" not in ecommercedata.getallcolumn(ecommercedata,ecommercedata) :
            del req_dict["mima"]
        if req_dict.get("password") and "password" not in ecommercedata.getallcolumn(ecommercedata,ecommercedata) :
            del req_dict["password"]
        try:
            del req_dict["clicknum"]
        except:
            pass


        error = ecommercedata.updatebyparams(ecommercedata, ecommercedata, req_dict)
        if error!=None:
            msg['code'] = crud_error_code
            msg['msg'] = error

        return JsonResponse(msg)


def ecommercedata_delete(request):
    '''
    批量删除
    '''
    request.funname = __name__+"."+ecommercedata_delete.__name__
    request.operation = "删除电商数据"
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")

        error=ecommercedata.deletes(ecommercedata,
            ecommercedata,
             req_dict.get("ids")
        )
        if error!=None:
            msg['code'] = crud_error_code
            msg['msg'] = error
        return JsonResponse(msg)


def ecommercedata_vote(request,id_):
    '''
    浏览点击次数（表属性[browseClick:是/否]，点击字段（clicknum），调用info/detail接口的时候后端自动+1）、投票功能（表属性[vote:是/否]，投票字段（votenum）,调用vote接口后端votenum+1）
统计商品或新闻的点击次数；提供新闻的投票功能
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code}


        data= ecommercedata.getbyid(ecommercedata, ecommercedata, int(id_))
        for i in data:
            votenum=i.get('votenum')
            if votenum!=None:
                params={"id":int(id_),"votenum":votenum+1}
                error=ecommercedata.updatebyparams(ecommercedata,ecommercedata,params)
                if error!=None:
                    msg['code'] = crud_error_code
                    msg['msg'] = error
        return JsonResponse(msg)

def ecommercedata_importExcel(request):
    request.funname = __name__+"."+ecommercedata_importExcel.__name__
    request.operation = "导入电商数据"
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": {}}

        excel_file = request.FILES.get("file", "")
        if excel_file.size > 100 * 1024 * 1024:  # 限制为 100MB
            msg['code'] = 400
            msg["msg"] = '文件大小不能超过100MB'
            return JsonResponse(msg)

        file_type = excel_file.name.split('.')[1]
        
        if file_type in ['xlsx', 'xls']:
            data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())
            table = data.sheets()[0]
            rows = table.nrows
            
            try:
                for row in range(1, rows):
                    row_values = table.row_values(row)
                    req_dict = {}
                    if '.0' in str(row_values[0]):
                        req_dict['yh'] = str(row_values[0]).split('.')[0]
                    elif str(row_values[0]) != '':
                        req_dict['yh'] = row_values[0]
                    else:
                        req_dict['yh'] = None
                    if '.0' in str(row_values[1]):
                        req_dict['sp'] = str(row_values[1]).split('.')[0]
                    elif str(row_values[1]) != '':
                        req_dict['sp'] = row_values[1]
                    else:
                        req_dict['sp'] = None
                    if '.0' in str(row_values[2]):
                        req_dict['behaviortype'] = str(row_values[2]).split('.')[0]
                    elif str(row_values[2]) != '':
                        req_dict['behaviortype'] = row_values[2]
                    else:
                        req_dict['behaviortype'] = None
                    if '.0' in str(row_values[3]):
                        req_dict['behaviortime'] = str(row_values[3]).split('.')[0]
                    elif str(row_values[3]) != '':
                        req_dict['behaviortime'] = row_values[3]
                    else:
                        req_dict['behaviortime'] = None
                    if '.0' in str(row_values[4]):
                        req_dict['primarycategoryofgoods'] = str(row_values[4]).split('.')[0]
                    elif str(row_values[4]) != '':
                        req_dict['primarycategoryofgoods'] = row_values[4]
                    else:
                        req_dict['primarycategoryofgoods'] = None
                    if '.0' in str(row_values[5]):
                        req_dict['secondarycategoryofgoods'] = str(row_values[5]).split('.')[0]
                    elif str(row_values[5]) != '':
                        req_dict['secondarycategoryofgoods'] = row_values[5]
                    else:
                        req_dict['secondarycategoryofgoods'] = None
                    if '.0' in str(row_values[6]):
                        req_dict['productbrand'] = str(row_values[6]).split('.')[0]
                    elif str(row_values[6]) != '':
                        req_dict['productbrand'] = row_values[6]
                    else:
                        req_dict['productbrand'] = None
                    if str(row_values[7]) != '':
                        req_dict['commodityprice'] = float(row_values[7])
                    else:
                        req_dict['commodityprice'] = None
                    if str(row_values[8]) != '':
                        req_dict['productdiscountrate'] = float(row_values[8])
                    else:
                        req_dict['productdiscountrate'] = None
                    if '.0' in str(row_values[9]):
                        req_dict['userage'] = str(row_values[9]).split('.')[0]
                    elif str(row_values[9]) != '':
                        req_dict['userage'] = row_values[9]
                    else:
                        req_dict['userage'] = None
                    if '.0' in str(row_values[10]):
                        req_dict['usergender'] = str(row_values[10]).split('.')[0]
                    elif str(row_values[10]) != '':
                        req_dict['usergender'] = row_values[10]
                    else:
                        req_dict['usergender'] = None
                    if '.0' in str(row_values[11]):
                        req_dict['yhdys'] = str(row_values[11]).split('.')[0]
                    elif str(row_values[11]) != '':
                        req_dict['yhdys'] = row_values[11]
                    else:
                        req_dict['yhdys'] = None
                    if '.0' in str(row_values[12]):
                        req_dict['yhdycsjb'] = str(row_values[12]).split('.')[0]
                    elif str(row_values[12]) != '':
                        req_dict['yhdycsjb'] = row_values[12]
                    else:
                        req_dict['yhdycsjb'] = None
                    if '.0' in str(row_values[13]):
                        req_dict['usermembershiplevel'] = str(row_values[13]).split('.')[0]
                    elif str(row_values[13]) != '':
                        req_dict['usermembershiplevel'] = row_values[13]
                    else:
                        req_dict['usermembershiplevel'] = None
                    if '.0' in str(row_values[14]):
                        req_dict['userregistrationdays'] = str(row_values[14]).split('.')[0]
                    elif str(row_values[14]) != '':
                        req_dict['userregistrationdays'] = row_values[14]
                    else:
                        req_dict['userregistrationdays'] = None
                    if str(row_values[15]) != '':
                        req_dict['orderamount'] = float(row_values[15])
                    else:
                        req_dict['orderamount'] = None
                    if '.0' in str(row_values[16]):
                        req_dict['purchasequantity'] = str(row_values[16]).split('.')[0]
                    elif str(row_values[16]) != '':
                        req_dict['purchasequantity'] = row_values[16]
                    else:
                        req_dict['purchasequantity'] = None
                    if '.0' in str(row_values[17]):
                        req_dict['paymentchannel'] = str(row_values[17]).split('.')[0]
                    elif str(row_values[17]) != '':
                        req_dict['paymentchannel'] = row_values[17]
                    else:
                        req_dict['paymentchannel'] = None
                    if '.0' in str(row_values[18]):
                        req_dict['devicetype'] = str(row_values[18]).split('.')[0]
                    elif str(row_values[18]) != '':
                        req_dict['devicetype'] = row_values[18]
                    else:
                        req_dict['devicetype'] = None
                    if str(row_values[19]) != '':
                        req_dict['repurchaserate'] = float(row_values[19])
                    else:
                        req_dict['repurchaserate'] = None
                    ecommercedata.createbyreq(ecommercedata, ecommercedata, req_dict)
                    
            except:
                pass
                
        else:
            msg = {
                "msg": "文件类型错误",
                "code": 500
            }
                
        return JsonResponse(msg)

def ecommercedata_autoSort2(request):
    return JsonResponse({"code": 0, "msg": '',  "data":{}})



def ecommercedata_count(request):
    '''
    总数接口
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": {}}
        req_dict = request.session.get("req_dict")
        where = ' where 1 = 1 '
        for key in req_dict:
            if req_dict[key] != None:
                where = where + " and key like '{0}'".format(req_dict[key])
        
        sql = "SELECT count(*) AS count FROM ecommercedata {0}".format(where)
        count = 0
        cursor = connection.cursor()
        cursor.execute(sql)
        desc = cursor.description
        data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()] 
        for online_dict in data_dict:
            count = online_dict['count']
        msg['data'] = count

        return JsonResponse(msg, encoder=CustomJsonEncoder)

#对日期进行排序
def order_time(data,type,xColumnName,rev):
    if type=="日":
        result_data = sorted(
            data,
            key=lambda x: (
                int(x[xColumnName].split("-")[0]),
                int(x[xColumnName].split("-")[1]),
                int(x[xColumnName].split("-")[2]),
            ),
            reverse=rev  # 设置排列
        )
    elif type=="月":
        result_data = sorted(
            data,
            key=lambda x: (
                int(x[xColumnName].split("-")[0]),
                int(x[xColumnName].split("-")[1])
            ),
            reverse=rev  # 设置排列
        )
    elif type=="年":
        result_data = sorted(
            data,
            key=lambda x: (
                int(x[xColumnName].split("-")[0]),  # 提取年份并转为整数
            ),
            reverse=rev  # 设置排列
        )
    else:
        result_data = sorted(data, key=lambda x: x[xColumnName], reverse=rev)
    return result_data

# （按值统计）时间统计类型
def ecommercedata_value(request, xColumnName, yColumnName, timeStatType):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": {}}
        where = ' where 1 = 1 '
        raw_query_string = request.META.get('QUERY_STRING', '')
        raw_query_string = unquote(raw_query_string)
        conditionColumn = ""
        conditionValue = ""
        if "conditionColumn=" in raw_query_string:
            conditionColumn = raw_query_string.split("conditionColumn=")[1].split("&")[0]
        if "conditionValue=" in raw_query_string:
            conditionValue = raw_query_string.split("conditionValue=")[1].split("&")[0]
        if conditionColumn != "":
            for index, value in enumerate(conditionColumn.split(";")):
                if ',' in value:
                    where = where + f''' and {value.split(',')[0]} >= \'{conditionValue.split(";")[index].split(",")[0]}\''''
                    where = where + f''' and {value.split(',')[1]} <= \'{conditionValue.split(";")[index].split(",")[1]}\''''
                else:
                    where = where + f''' and {value} = \'{conditionValue.split(";")[index]}\''''
        req_dict = request.session.get("req_dict")
        statistics_func = "SUM"
        func_params = req_dict.get("func")
        if func_params == "平均":
            statistics_func = "AVG"
        elif func_params == "最大":
            statistics_func = "MAX"
        elif func_params == "最小":
            statistics_func = "MIN"
        elif func_params == "总和":
            statistics_func = "COUNT"
        try:
            del req_dict["func"]
        except:
            pass
        # 定义查询统计语句
        for key, value in req_dict.items():
            if key != "limit" and key != "order" and key != "orderType" and key != "yColumnNameMul" and key != "conditionColumn" and key != "conditionValue":
                where = where + " and {0} ='{1}' ".format(key, value)
        sql = ''
        if timeStatType == '日':
            sql = "SELECT DATE_FORMAT({0}, '%Y-%m-%d') {0}, ROUND({1}({2}),2) total FROM ecommercedata {3} GROUP BY DATE_FORMAT({0}, '%Y-%m-%d')".format(xColumnName,statistics_func, yColumnName, where, '%Y-%m-%d')

        if timeStatType == '月':
            sql = "SELECT DATE_FORMAT({0}, '%Y-%m') {0}, ROUND({1}({2}),2) total FROM ecommercedata {3} GROUP BY DATE_FORMAT({0}, '%Y-%m')".format(xColumnName,statistics_func, yColumnName, where, '%Y-%m')

        if timeStatType == '季':
            sql = "SELECT CONCAT(YEAR(MIN({0})), '-Q', QUARTER(MIN({0}))) AS {0}, {1}({2}) AS total FROM orders {3} GROUP BY YEAR({0}), QUARTER({0})".format(xColumnName,statistics_func, yColumnName, where)

        if timeStatType == '年':
            sql = "SELECT DATE_FORMAT({0}, '%Y') {0}, ROUND({1}({2}),2) total FROM ecommercedata {3} GROUP BY DATE_FORMAT({0}, '%Y')".format(xColumnName,statistics_func, yColumnName, where, '%Y')

        L = []
        cursor = connection.cursor()
        cursor.execute(sql)
        desc = cursor.description
        data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
        for online_dict in data_dict:
            for key in online_dict:
                if 'datetime.datetime' in str(type(online_dict[key])):
                    online_dict[key] = online_dict[key].strftime(
                        "%Y-%m-%d %H:%M:%S")
                else:
                    pass
            L.append(online_dict)
        msg['data'] = L
        req_dict = request.session.get("req_dict")
        #对结果进行排序
        order = req_dict.get('order')
        orderType = req_dict.get('orderType')
        if orderType=='x' :
            if order == "desc":
                msg['data'] = order_time(msg['data'], timeStatType, xColumnName, True)
            else:
                msg['data'] = order_time(msg['data'], timeStatType, xColumnName, False)
        else:
            if order == "desc":
                msg['data'] = sorted((x for x in msg['data'] if x['total'] is not None), key=lambda x: x['total'],
                                     reverse=True)
            else:
                msg['data'] = sorted((x for x in msg['data'] if x['total'] is not None), key=lambda x: x['total'])

        if "limit" in req_dict and int(req_dict["limit"]) < len(L):
            msg['data'] = msg['data'][:int(req_dict["limit"])]
        return JsonResponse(msg, encoder=CustomJsonEncoder)

# 按值统计
def ecommercedata_o_value(request, xColumnName, yColumnName):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": {}}
        where = ' where 1 = 1 '
        raw_query_string = request.META.get('QUERY_STRING', '')
        raw_query_string = unquote(raw_query_string)
        conditionColumn = ""
        conditionValue = ""
        if "conditionColumn=" in raw_query_string:
            conditionColumn = raw_query_string.split("conditionColumn=")[1].split("&")[0]
        if "conditionValue=" in raw_query_string:
            conditionValue = raw_query_string.split("conditionValue=")[1].split("&")[0]
        if conditionColumn != "":
            for index, value in enumerate(conditionColumn.split(";")):
                if "," in value:
                    where = where + f''' and {value.split(',')[0]} >= \'{conditionValue.split(";")[index].split(",")[0]}\''''
                    where = where + f''' and {value.split(',')[1]} <= \'{conditionValue.split(";")[index].split(",")[1]}\''''
                else:
                    where = where + f''' and {value} = \'{conditionValue.split(";")[index]}\''''
        req_dict = request.session.get("req_dict")
        statistics_func = "SUM"
        func_params = req_dict.get("func")
        if func_params == "平均":
            statistics_func = "AVG"
        elif func_params == "最大":
            statistics_func = "MAX"
        elif func_params == "最小":
            statistics_func = "MIN"
        elif func_params == "总和":
            statistics_func = "COUNT"
        try:
            del req_dict["func"]
        except:
            pass
        sql = "SELECT {0}, ROUND({1}({2}),2) AS total FROM ecommercedata {3} GROUP BY {0}".format(xColumnName,statistics_func, yColumnName, where)
        L = []
        cursor = connection.cursor()
        cursor.execute(sql)
        desc = cursor.description
        data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
        for online_dict in data_dict:
            for key in online_dict:
                if 'datetime.datetime' in str(type(online_dict[key])):
                    online_dict[key] = online_dict[key].strftime(
                        "%Y-%m-%d %H:%M:%S")
                else:
                    pass
            L.append(online_dict)
        msg['data'] = L
        req_dict = request.session.get("req_dict")
        if "order" in req_dict:
            order = req_dict["order"]
            if order == "desc":
                msg['data'] = sorted((x for x in msg['data'] if x['total'] is not None),key=lambda x: x['total'],reverse=True)
            else:
                msg['data'] = sorted((x for x in msg['data'] if x['total'] is not None),key=lambda x: x['total'])

        if "limit" in req_dict and int(req_dict["limit"]) < len(L):
            msg['data'] = msg['data'][:int(req_dict["limit"])]
        return JsonResponse(msg, encoder=CustomJsonEncoder)

# （按值统计）时间统计类型(多)
def ecommercedata_valueMul(request, xColumnName, timeStatType):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": []}
        req_dict = request.session.get("req_dict")
        where = ' where 1 = 1 '
        raw_query_string = request.META.get('QUERY_STRING', '')
        raw_query_string = unquote(raw_query_string)
        conditionColumn = ""
        conditionValue = ""
        if "conditionColumn=" in raw_query_string:
            conditionColumn = raw_query_string.split("conditionColumn=")[1].split("&")[0]
        if "conditionValue=" in raw_query_string:
            conditionValue = raw_query_string.split("conditionValue=")[1].split("&")[0]
        if conditionColumn != "":
            for index, value in enumerate(conditionColumn.split(";")):
                if "," in value:
                    where = where + f''' and {value.split(',')[0]} >= \'{conditionValue.split(";")[index].split(",")[0]}\''''
                    where = where + f''' and {value.split(',')[0]} <= \'{conditionValue.split(";")[index].split(",")[1]}\''''
                else:
                    where = where + f''' and {value} = \'{conditionValue.split(";")[index]}\''''

        statistics_func = "SUM"
        func_params = req_dict.get("func")
        if func_params == "平均":
            statistics_func = "AVG"
        elif func_params == "最大":
            statistics_func = "MAX"
        elif func_params == "最小":
            statistics_func = "MIN"
        elif func_params == "总和":
            statistics_func = "COUNT"
        try:
            del req_dict["func"]
        except:
            pass
        # 定义查询统计语句
        for key, value in req_dict.items():
            if key != "limit" and key != "order" and key != "orderType" and key != "yColumnNameMul" and key != "conditionColumn" and key != "conditionValue":
                where = where + " and {0} ='{1}' ".format(key, value)

        for item in req_dict['yColumnNameMul'].split(','):
            sql = ''
            if timeStatType == '日':
                sql = "SELECT DATE_FORMAT({0}, '%Y-%m-%d') {0}, ROUND({1}({2}),2) total FROM ecommercedata {3} GROUP BY DATE_FORMAT({0}, '%Y-%m-%d')".format(xColumnName, statistics_func,item, where, '%Y-%m-%d')

            if timeStatType == '月':
                sql = "SELECT DATE_FORMAT({0}, '%Y-%m') {0}, ROUND({1}({2}),2) total FROM ecommercedata {3} GROUP BY DATE_FORMAT({0}, '%Y-%m')".format(xColumnName,statistics_func, item, where, '%Y-%m')

            if timeStatType == '季':
                sql = "SELECT CONCAT(YEAR(MIN({0})), '-Q', QUARTER(MIN({0}))) {0}, {1}({2}) total FROM ecommercedata {3} GROUP BY YEAR({0}), QUARTER({0})".format(xColumnName, statistics_func,item, where)

            if timeStatType == '年':
                sql = "SELECT DATE_FORMAT({0}, '%Y') {0}, ROUND({1}({2}),2) total FROM ecommercedata {3} GROUP BY DATE_FORMAT({0}, '%Y')".format(xColumnName,statistics_func, item, where, '%Y')

            L = []
            cursor = connection.cursor()
            cursor.execute(sql)
            desc = cursor.description
            data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
            for online_dict in data_dict:
                for key in online_dict:
                    if 'datetime.datetime' in str(type(online_dict[key])):
                        online_dict[key] = online_dict[key].strftime(
                            "%Y-%m-%d %H:%M:%S")
                    else:
                        pass
                L.append(online_dict)
                # 结果进行排序
                order = req_dict.get('order')
                orderType = req_dict.get('orderType')
                if orderType == 'x':
                    if order == "desc":
                        L = order_time(L, timeStatType, xColumnName, True)
                    else:
                        L = order_time(L, timeStatType, xColumnName, False)
                else:
                    if order == "desc":
                        L = sorted((x for x in L if x['total'] is not None),
                                   key=lambda x: x['total'],
                                   reverse=True)
                    else:
                        L = sorted((x for x in L if x['total'] is not None),
                                   key=lambda x: x['total'])
                # 截取列表个数
                if "limit" in req_dict and int(req_dict["limit"]) < len(msg['data']):
                    L = L[:int(req_dict["limit"])]
            msg['data'].append(L)
        return JsonResponse(msg, encoder=CustomJsonEncoder)

# （按值统计(多)）
def ecommercedata_o_valueMul(request, xColumnName):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": []}

        req_dict = request.session.get("req_dict")
        where = ' where 1 = 1 '
        raw_query_string = request.META.get('QUERY_STRING', '')
        raw_query_string = unquote(raw_query_string)
        conditionColumn = ""
        conditionValue = ""
        if "conditionColumn=" in raw_query_string:
            conditionColumn = raw_query_string.split("conditionColumn=")[1].split("&")[0]
        if "conditionValue=" in raw_query_string:
            conditionValue = raw_query_string.split("conditionValue=")[1].split("&")[0]
        if conditionColumn != "":
            for index, value in enumerate(conditionColumn.split(";")):
                if "," in value:
                    where = where + f''' and {value.split(',')[0]} >= \'{conditionValue.split(";")[index].split(",")[0]}\''''
                    where = where + f''' and {value.split(',')[0]} <= \'{conditionValue.split(";")[index].split(",")[1]}\''''
                else:
                    where = where + f''' and {value} = \'{conditionValue.split(";")[index]}\''''
        statistics_func = "SUM"
        func_params = req_dict.get("func")
        if func_params == "平均":
            statistics_func = "AVG"
        elif func_params == "最大":
            statistics_func = "MAX"
        elif func_params == "最小":
            statistics_func = "MIN"
        elif func_params == "总和":
            statistics_func = "COUNT"
        try:
            del req_dict["func"]
        except:
            pass
        for item in req_dict['yColumnNameMul'].split(','):
            sql = "SELECT {0}, ROUND({1}({2}),2) AS total FROM ecommercedata {3} GROUP BY {0}".format(xColumnName, statistics_func,item, where)
            L = []
            cursor = connection.cursor()
            cursor.execute(sql)
            desc = cursor.description
            data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
            for online_dict in data_dict:
                for key in online_dict:
                    if 'datetime.datetime' in str(type(online_dict[key])):
                        online_dict[key] = online_dict[key].strftime(
                            "%Y-%m-%d %H:%M:%S")
                    else:
                        pass
                L.append(online_dict)
            msg['data'].append(L)
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def ecommercedata_group(request, columnName):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": {}}

        where = ' where 1 = 1 '
        raw_query_string = request.META.get('QUERY_STRING', '')
        raw_query_string = unquote(raw_query_string)
        conditionColumn = ""
        conditionValue = ""
        if "conditionColumn=" in raw_query_string:
            conditionColumn = raw_query_string.split("conditionColumn=")[1].split("&")[0]
        if "conditionValue=" in raw_query_string:
            conditionValue = raw_query_string.split("conditionValue=")[1].split("&")[0]
        if conditionColumn != "":
            for index, value in enumerate(conditionColumn.split(";")):
                if ',' in value:
                    where = where + f''' and {value.split(',')[0]} >= \'{conditionValue.split(";")[index].split(",")[0]}\''''
                    where = where + f''' and {value.split(',')[1]} <= \'{conditionValue.split(";")[index].split(",")[1]}\''''
                else:
                    where = where + f''' and {value} = \'{conditionValue.split(";")[index]}\''''
        sql = "SELECT COUNT(*) AS total, " + columnName + " FROM ecommercedata " + where + " GROUP BY " + columnName
        L = []
        cursor = connection.cursor()
        cursor.execute(sql)
        desc = cursor.description
        data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
        for online_dict in data_dict:
            for key in online_dict:
                if 'datetime.datetime' in str(type(online_dict[key])):
                    online_dict[key] = online_dict[key].strftime("%Y-%m-%d")
                else:
                    pass
            L.append(online_dict)
        msg['data'] = L
        req_dict = request.session.get("req_dict")
        if "order" in req_dict:
            order = req_dict["order"]
            if order == "desc":
                msg['data'] = sorted((x for x in msg['data'] if x['total'] is not None),key=lambda x: x['total'],reverse=True)
            else:
                msg['data'] = sorted((x for x in msg['data'] if x['total'] is not None),key=lambda x: x['total'])

        if "limit" in req_dict and int(req_dict["limit"]) < len(L):
            msg['data'] = msg['data'][:int(req_dict["limit"])]
        return JsonResponse(msg, encoder=CustomJsonEncoder)




import math

def ecommercedata_cleanse(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": {}}
        try:
            list, _, _, total,_ = ecommercedata.page(ecommercedata, ecommercedata, {})
            df = pd.DataFrame(list,dtype=object)
#随机填充
            df['yh'].replace([None, '' ], pd.NA,inplace = True)
            yh_non_na = df['yh'].dropna()  # 获取非空值
            for i in df.index:
                if pd.isna(df.loc[i, 'yh']):
                    df.loc[i, 'yh'] = yh_non_na.sample(n=1,replace=True).values[0]
#随机填充
            df['sp'].replace([None, '' ], pd.NA,inplace = True)
            sp_non_na = df['sp'].dropna()  # 获取非空值
            for i in df.index:
                if pd.isna(df.loc[i, 'sp']):
                    df.loc[i, 'sp'] = sp_non_na.sample(n=1,replace=True).values[0]
#随机填充
            df['behaviortype'].replace([None, '' ], pd.NA,inplace = True)
            behaviortype_non_na = df['behaviortype'].dropna()  # 获取非空值
            for i in df.index:
                if pd.isna(df.loc[i, 'behaviortype']):
                    df.loc[i, 'behaviortype'] = behaviortype_non_na.sample(n=1,replace=True).values[0]
#随机填充
            df['behaviortime'].replace([None, '' ], pd.NA,inplace = True)
            behaviortime_non_na = df['behaviortime'].dropna()  # 获取非空值
            for i in df.index:
                if pd.isna(df.loc[i, 'behaviortime']):
                    df.loc[i, 'behaviortime'] = behaviortime_non_na.sample(n=1,replace=True).values[0]
#随机填充
            df['primarycategoryofgoods'].replace([None, '' ], pd.NA,inplace = True)
            primarycategoryofgoods_non_na = df['primarycategoryofgoods'].dropna()  # 获取非空值
            for i in df.index:
                if pd.isna(df.loc[i, 'primarycategoryofgoods']):
                    df.loc[i, 'primarycategoryofgoods'] = primarycategoryofgoods_non_na.sample(n=1,replace=True).values[0]
#随机填充
            df['secondarycategoryofgoods'].replace([None, '' ], pd.NA,inplace = True)
            secondarycategoryofgoods_non_na = df['secondarycategoryofgoods'].dropna()  # 获取非空值
            for i in df.index:
                if pd.isna(df.loc[i, 'secondarycategoryofgoods']):
                    df.loc[i, 'secondarycategoryofgoods'] = secondarycategoryofgoods_non_na.sample(n=1,replace=True).values[0]
#随机填充
            df['productbrand'].replace([None, '' ], pd.NA,inplace = True)
            productbrand_non_na = df['productbrand'].dropna()  # 获取非空值
            for i in df.index:
                if pd.isna(df.loc[i, 'productbrand']):
                    df.loc[i, 'productbrand'] = productbrand_non_na.sample(n=1,replace=True).values[0]
#随机填充
            df['commodityprice'].replace([None, '' ], pd.NA,inplace = True)
            commodityprice_non_na = df['commodityprice'].dropna()  # 获取非空值
            for i in df.index:
                if pd.isna(df.loc[i, 'commodityprice']):
                    df.loc[i, 'commodityprice'] = commodityprice_non_na.sample(n=1,replace=True).values[0]
#随机填充
            df['productdiscountrate'].replace([None, '' ], pd.NA,inplace = True)
            productdiscountrate_non_na = df['productdiscountrate'].dropna()  # 获取非空值
            for i in df.index:
                if pd.isna(df.loc[i, 'productdiscountrate']):
                    df.loc[i, 'productdiscountrate'] = productdiscountrate_non_na.sample(n=1,replace=True).values[0]
#随机填充
            df['userage'].replace([None, '' ], pd.NA,inplace = True)
            userage_non_na = df['userage'].dropna()  # 获取非空值
            for i in df.index:
                if pd.isna(df.loc[i, 'userage']):
                    df.loc[i, 'userage'] = userage_non_na.sample(n=1,replace=True).values[0]
#随机填充
            df['usergender'].replace([None, '' ], pd.NA,inplace = True)
            usergender_non_na = df['usergender'].dropna()  # 获取非空值
            for i in df.index:
                if pd.isna(df.loc[i, 'usergender']):
                    df.loc[i, 'usergender'] = usergender_non_na.sample(n=1,replace=True).values[0]
#随机填充
            df['yhdys'].replace([None, '' ], pd.NA,inplace = True)
            yhdys_non_na = df['yhdys'].dropna()  # 获取非空值
            for i in df.index:
                if pd.isna(df.loc[i, 'yhdys']):
                    df.loc[i, 'yhdys'] = yhdys_non_na.sample(n=1,replace=True).values[0]
#随机填充
            df['yhdycsjb'].replace([None, '' ], pd.NA,inplace = True)
            yhdycsjb_non_na = df['yhdycsjb'].dropna()  # 获取非空值
            for i in df.index:
                if pd.isna(df.loc[i, 'yhdycsjb']):
                    df.loc[i, 'yhdycsjb'] = yhdycsjb_non_na.sample(n=1,replace=True).values[0]
#随机填充
            df['usermembershiplevel'].replace([None, '' ], pd.NA,inplace = True)
            usermembershiplevel_non_na = df['usermembershiplevel'].dropna()  # 获取非空值
            for i in df.index:
                if pd.isna(df.loc[i, 'usermembershiplevel']):
                    df.loc[i, 'usermembershiplevel'] = usermembershiplevel_non_na.sample(n=1,replace=True).values[0]
#随机填充
            df['userregistrationdays'].replace([None, '' ], pd.NA,inplace = True)
            userregistrationdays_non_na = df['userregistrationdays'].dropna()  # 获取非空值
            for i in df.index:
                if pd.isna(df.loc[i, 'userregistrationdays']):
                    df.loc[i, 'userregistrationdays'] = userregistrationdays_non_na.sample(n=1,replace=True).values[0]
#随机填充
            df['orderamount'].replace([None, '' ], pd.NA,inplace = True)
            orderamount_non_na = df['orderamount'].dropna()  # 获取非空值
            for i in df.index:
                if pd.isna(df.loc[i, 'orderamount']):
                    df.loc[i, 'orderamount'] = orderamount_non_na.sample(n=1,replace=True).values[0]
#随机填充
            df['purchasequantity'].replace([None, '' ], pd.NA,inplace = True)
            purchasequantity_non_na = df['purchasequantity'].dropna()  # 获取非空值
            for i in df.index:
                if pd.isna(df.loc[i, 'purchasequantity']):
                    df.loc[i, 'purchasequantity'] = purchasequantity_non_na.sample(n=1,replace=True).values[0]
#随机填充
            df['paymentchannel'].replace([None, '' ], pd.NA,inplace = True)
            paymentchannel_non_na = df['paymentchannel'].dropna()  # 获取非空值
            for i in df.index:
                if pd.isna(df.loc[i, 'paymentchannel']):
                    df.loc[i, 'paymentchannel'] = paymentchannel_non_na.sample(n=1,replace=True).values[0]
#随机填充
            df['devicetype'].replace([None, '' ], pd.NA,inplace = True)
            devicetype_non_na = df['devicetype'].dropna()  # 获取非空值
            for i in df.index:
                if pd.isna(df.loc[i, 'devicetype']):
                    df.loc[i, 'devicetype'] = devicetype_non_na.sample(n=1,replace=True).values[0]
#随机填充
            df['repurchaserate'].replace([None, '' ], pd.NA,inplace = True)
            repurchaserate_non_na = df['repurchaserate'].dropna()  # 获取非空值
            for i in df.index:
                if pd.isna(df.loc[i, 'repurchaserate']):
                    df.loc[i, 'repurchaserate'] = repurchaserate_non_na.sample(n=1,replace=True).values[0]
            data_list = df.to_dict(orient='records')
            ecommercedata.deletes(ecommercedata,ecommercedata,ids=[i["id"] for i in list])
            batchList = []
            for dl in data_list:
                filtered_data = {k: v for k, v in dl.items() if v not in [None, '', float('nan')] and (not isinstance(v, float) or not math.isnan(v))}
                batchList.append(ecommercedata(**filtered_data))
            ecommercedata.objects.bulk_create(batchList)
        except Exception as e:
            msg["code"] = other_code
            msg["msg"] = e.__str__()

        return JsonResponse(msg)




