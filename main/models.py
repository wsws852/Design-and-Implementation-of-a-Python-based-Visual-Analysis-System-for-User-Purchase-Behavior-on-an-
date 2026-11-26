#coding:utf-8
from django.db import models

from .model import BaseModel

from datetime import datetime



class yunyingrenyuan(BaseModel):
    __doc__ = u'''yunyingrenyuan'''
    __tablename__ = 'yunyingrenyuan'

    __loginUser__='yunyingzhanghao'


    __authTables__={}
    __authPeople__='是'#用户表，表属性loginUserColumn对应的值就是用户名字段，mima就是密码字段
    __loginUserColumn__='yunyingzhanghao'#用户表，表属性loginUserColumn对应的值就是用户名字段，mima就是密码字段
    __sfsh__='否'#表sfsh(是否审核，”是”或”否”)字段和sfhf(审核回复)字段，后台列表(page)的操作中要多一个”审核”按钮，点击”审核”弹出一个页面，包含”是否审核”和”审核回复”，点击确定调用update接口，修改sfsh和sfhf两个字段。
    __authSeparate__='否'#后台列表权限
    __thumbsUp__='否'#表属性thumbsUp[是/否]，新增thumbsupnum赞和crazilynum踩字段
    __intelRecom__='否'#智能推荐功能(表属性：[intelRecom（是/否）],新增clicktime[前端不显示该字段]字段（调用info/detail接口的时候更新），按clicktime排序查询)
    __browseClick__='否'#表属性[browseClick:是/否]，点击字段（clicknum），调用info/detail接口的时候后端自动+1）、投票功能（表属性[vote:是/否]，投票字段（votenum）,调用vote接口后端votenum+1
    __foreEndListAuth__='否'#前台列表权限foreEndListAuth[是/否]；当foreEndListAuth=是，刷的表新增用户字段userid，前台list列表接口仅能查看自己的记录和add接口后台赋值userid的值
    __foreEndList__='否'#表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
    __isAdmin__='否'#表属性isAdmin=”是”,刷出来的用户表也是管理员，即page和list可以查看所有人的考试记录(同时应用于其他表)
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    yunyingzhanghao=models.CharField ( max_length=255,null=False,unique=True, verbose_name='运营账号' )
    mima=models.CharField ( max_length=255,null=False, unique=False, verbose_name='密码' )
    yunyingxingming=models.CharField ( max_length=255,null=False, unique=False, verbose_name='运营姓名' )
    xingbie=models.CharField ( max_length=255, null=True, unique=False, verbose_name='性别' )
    idcard=models.CharField ( max_length=255, null=True, unique=False, verbose_name='身份证' )
    age=models.IntegerField  (  null=True, unique=False, verbose_name='年龄' )
    shoujihao=models.CharField ( max_length=255, null=True, unique=False, verbose_name='手机号' )
    touxiang=models.TextField   (  null=True, unique=False, verbose_name='头像' )
    '''
    yunyingzhanghao=VARCHAR
    mima=VARCHAR
    yunyingxingming=VARCHAR
    xingbie=VARCHAR
    idcard=VARCHAR
    age=Integer
    shoujihao=VARCHAR
    touxiang=Text
    '''
    class Meta:
        db_table = 'yunyingrenyuan'
        verbose_name = verbose_name_plural = '运营人员'
class ecommercedata(BaseModel):
    __doc__ = u'''ecommercedata'''
    __tablename__ = 'ecommercedata'



    __authTables__={}
    __authPeople__='否'#用户表，表属性loginUserColumn对应的值就是用户名字段，mima就是密码字段
    __sfsh__='否'#表sfsh(是否审核，”是”或”否”)字段和sfhf(审核回复)字段，后台列表(page)的操作中要多一个”审核”按钮，点击”审核”弹出一个页面，包含”是否审核”和”审核回复”，点击确定调用update接口，修改sfsh和sfhf两个字段。
    __authSeparate__='否'#后台列表权限
    __thumbsUp__='否'#表属性thumbsUp[是/否]，新增thumbsupnum赞和crazilynum踩字段
    __intelRecom__='否'#智能推荐功能(表属性：[intelRecom（是/否）],新增clicktime[前端不显示该字段]字段（调用info/detail接口的时候更新），按clicktime排序查询)
    __browseClick__='否'#表属性[browseClick:是/否]，点击字段（clicknum），调用info/detail接口的时候后端自动+1）、投票功能（表属性[vote:是/否]，投票字段（votenum）,调用vote接口后端votenum+1
    __foreEndListAuth__='否'#前台列表权限foreEndListAuth[是/否]；当foreEndListAuth=是，刷的表新增用户字段userid，前台list列表接口仅能查看自己的记录和add接口后台赋值userid的值
    __foreEndList__='否'#表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
    __isAdmin__='否'#表属性isAdmin=”是”,刷出来的用户表也是管理员，即page和list可以查看所有人的考试记录(同时应用于其他表)
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    yh=models.IntegerField  (  null=True, unique=False, verbose_name='用户ID' )
    sp=models.IntegerField  (  null=True, unique=False, verbose_name='商品ID' )
    behaviortype=models.CharField ( max_length=255, null=True, unique=False, verbose_name='行为类型' )
    behaviortime=models.IntegerField  (  null=True, unique=False, verbose_name='行为时间戳' )
    primarycategoryofgoods=models.CharField ( max_length=255, null=True, unique=False, verbose_name='商品一级类目' )
    secondarycategoryofgoods=models.CharField ( max_length=255, null=True, unique=False, verbose_name='商品二级类目' )
    productbrand=models.CharField ( max_length=255, null=True, unique=False, verbose_name='商品品牌' )
    commodityprice=models.FloatField   (  null=True, unique=False, verbose_name='商品价格' )
    productdiscountrate=models.FloatField   (  null=True, unique=False, verbose_name='商品折扣率' )
    userage=models.IntegerField  (  null=True, unique=False, verbose_name='用户年龄' )
    usergender=models.CharField ( max_length=255, null=True, unique=False, verbose_name='用户性别' )
    yhdys=models.CharField ( max_length=255, null=True, unique=False, verbose_name='用户地域-省' )
    yhdycsjb=models.CharField ( max_length=255, null=True, unique=False, verbose_name='用户地域-城市级别' )
    usermembershiplevel=models.IntegerField  (  null=True, unique=False, verbose_name='用户会员等级' )
    userregistrationdays=models.IntegerField  (  null=True, unique=False, verbose_name='用户注册天数' )
    orderamount=models.FloatField   (  null=True, unique=False, verbose_name='订单金额' )
    purchasequantity=models.IntegerField  (  null=True, unique=False, verbose_name='购买数量' )
    paymentchannel=models.CharField ( max_length=255, null=True, unique=False, verbose_name='支付渠道' )
    devicetype=models.CharField ( max_length=255, null=True, unique=False, verbose_name='设备类型' )
    repurchaserate=models.FloatField   (  null=True, unique=False, verbose_name='复购率' )
    '''
    yh=Integer
    sp=Integer
    behaviortype=VARCHAR
    behaviortime=Integer
    primarycategoryofgoods=VARCHAR
    secondarycategoryofgoods=VARCHAR
    productbrand=VARCHAR
    commodityprice=Float
    productdiscountrate=Float
    userage=Integer
    usergender=VARCHAR
    yhdys=VARCHAR
    yhdycsjb=VARCHAR
    usermembershiplevel=Integer
    userregistrationdays=Integer
    orderamount=Float
    purchasequantity=Integer
    paymentchannel=VARCHAR
    devicetype=VARCHAR
    repurchaserate=Float
    '''
    class Meta:
        db_table = 'ecommercedata'
        verbose_name = verbose_name_plural = '电商数据'
class ecommercedataforecast(BaseModel):
    __doc__ = u'''ecommercedataforecast'''
    __tablename__ = 'ecommercedataforecast'



    __authTables__={}
    __authPeople__='否'#用户表，表属性loginUserColumn对应的值就是用户名字段，mima就是密码字段
    __sfsh__='否'#表sfsh(是否审核，”是”或”否”)字段和sfhf(审核回复)字段，后台列表(page)的操作中要多一个”审核”按钮，点击”审核”弹出一个页面，包含”是否审核”和”审核回复”，点击确定调用update接口，修改sfsh和sfhf两个字段。
    __authSeparate__='否'#后台列表权限
    __thumbsUp__='否'#表属性thumbsUp[是/否]，新增thumbsupnum赞和crazilynum踩字段
    __intelRecom__='否'#智能推荐功能(表属性：[intelRecom（是/否）],新增clicktime[前端不显示该字段]字段（调用info/detail接口的时候更新），按clicktime排序查询)
    __browseClick__='否'#表属性[browseClick:是/否]，点击字段（clicknum），调用info/detail接口的时候后端自动+1）、投票功能（表属性[vote:是/否]，投票字段（votenum）,调用vote接口后端votenum+1
    __foreEndListAuth__='否'#前台列表权限foreEndListAuth[是/否]；当foreEndListAuth=是，刷的表新增用户字段userid，前台list列表接口仅能查看自己的记录和add接口后台赋值userid的值
    __foreEndList__='否'#表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
    __isAdmin__='否'#表属性isAdmin=”是”,刷出来的用户表也是管理员，即page和list可以查看所有人的考试记录(同时应用于其他表)
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    primarycategoryofgoods=models.CharField ( max_length=255, null=True, unique=False, verbose_name='商品一级类目' )
    secondarycategoryofgoods=models.CharField ( max_length=255, null=True, unique=False, verbose_name='商品二级类目' )
    productbrand=models.CharField ( max_length=255, null=True, unique=False, verbose_name='商品品牌' )
    commodityprice=models.FloatField   (  null=True, unique=False, verbose_name='商品价格' )
    yhdys=models.CharField ( max_length=255, null=True, unique=False, verbose_name='用户地域-省' )
    repurchaserate=models.FloatField   (  null=True, unique=False, verbose_name='复购率' )
    '''
    primarycategoryofgoods=VARCHAR
    secondarycategoryofgoods=VARCHAR
    productbrand=VARCHAR
    commodityprice=Float
    yhdys=VARCHAR
    repurchaserate=Float
    '''
    class Meta:
        db_table = 'ecommercedataforecast'
        verbose_name = verbose_name_plural = '复购率预测'
class syslog(BaseModel):
    __doc__ = u'''syslog'''
    __tablename__ = 'syslog'



    __authTables__={}
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    username=models.CharField ( max_length=255,null=False, unique=False, verbose_name='用户名' )
    operation=models.CharField ( max_length=255,null=False, unique=False, verbose_name='用户操作' )
    method=models.CharField ( max_length=255, null=True, unique=False, verbose_name='请求方法' )
    params=models.TextField   (  null=True, unique=False, verbose_name='请求参数' )
    time=models.BigIntegerField  (  null=True, unique=False, verbose_name='请求时长(毫秒)' )
    ip=models.CharField ( max_length=255, null=True, unique=False, verbose_name='IP地址' )
    '''
    username=VARCHAR
    operation=VARCHAR
    method=VARCHAR
    params=Text
    time=BigInteger
    ip=VARCHAR
    '''
    class Meta:
        db_table = 'syslog'
        verbose_name = verbose_name_plural = '系统日志'
class users(BaseModel):
    __doc__ = u'''users'''
    __tablename__ = 'users'



    __authTables__={}
    __authPeople__ = '是'
    __isAdmin__ = '是'
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    username=models.CharField ( max_length=255,null=False, unique=False, verbose_name='用户名' )
    password=models.CharField ( max_length=255,null=False, unique=False, verbose_name='密码' )
    role=models.CharField ( max_length=255, null=True, unique=False,default='管理员', verbose_name='角色' )
    image=models.TextField   (  null=True, unique=False, verbose_name='头像' )
    '''
    username=VARCHAR
    password=VARCHAR
    role=VARCHAR
    image=Text
    '''
    class Meta:
        db_table = 'users'
        verbose_name = verbose_name_plural = '管理员'
