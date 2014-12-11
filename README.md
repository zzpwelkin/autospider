### 爬虫框架 
python实现的爬虫框架实现。此框架主要设计思想如下:

1. 爬虫的定义和流程分离
2. 原爬虫定义

这样设计的优点:
1. 无需再编码，只需配置即可
2. 原爬虫方便测试
3. 可以编排原爬虫实现复杂爬虫

### 待优化列表
1. 重新用异步请求方式优化框架效率
2. 设计并实现一套前端编排和工程管理界面
3. 设计适合分布式爬获
4. 引入网络Proxy应用的设计
5. 实现增量式爬取逻辑
6. 重复网页检测(基于队列)

### 使用方法
1. 从spiderflow包中导入ProcessNode类 
from spiderflow import ProcessNode

2. 集成ProcessNode创建一个子类，并在子类中添加elems属性。elems属性就是页面爬取的定义, 语义定义如下:

        elems:{
                ['base': <xpath>,]
                ['field_name':(<xpath>, <regex>, <process>)|subelem,...] 
                                    }
            subelem:{'field_name':elems}
            field_name: field name that defined in ``Item``
            xpath: xpath语法字符串|None(base不能为空.表示base获取的文档树）
            regex: 正则表达式字符串|None
            process: [<func>,...]|None
            func:[func_name[:param,...];...]. 元素的处理分为两个过程，1) 返回元素列表选取处理;2)字符串处理


3. 要链接其他爬取节点，就要添加nextnodes属性，语义定义如下:

        nextnodes = [(<node>, <urls>, <isdata>),...]
            node: ProcessNode子类. 下一个处理的节点
            urls:(<xpath>, <process>).传给下一个处理节点的url, 如果是相对xpath路径，则沿用
            xpath: xpath路径语法。如果是相对路径，则用``elems``属性中的``base``元素
            isdata: True/False, 是否需要当前节点处理的数据
            
4. save属性设置
       save:={'dirver':<name>, 'param':{params}, 'alias':{alias}}
            name:=str 驱动名称
            param:=dict 初始化driver的字典
            alias:=dict item中字段和保存时的字段重命名
            
            
 5. 爬虫测试和执行
