### 爬虫框架 
python实现的爬虫框架实现。此框架主要设计思想如下:

1. 爬虫的定义和流程分离
2. 元爬虫定义

这样设计的优点:
1. 无需再编码，只需配置即可
2. 元爬虫方便测试
3. 可以基于元爬虫进行编排实现复杂网络内容的获取

### 待优化列表
1. 重新用异步请求方式优化框架效率(DONE)
2. 设计并实现一套前端编排和工程管理界面
3. 设计适合分布式爬获
4. 引入网络Proxy应用的设计
5. 实现增量式爬取逻辑
6. 重复网页检测(基于队列)(DONE)

### 使用方法
1. 从spiderflow包中导入爬虫的基类`SpiderNode` 

```from spiderflow import SpiderNode```

2. 不同结构的页面对应一个SpiderNode的子类，也即为不同页面创建一个Spider类并继承SpiderNode，在Spider类中添加elems属性。 
elems属性是页面爬取规则的定义, 语义定义如下:

```
        elems:{
                ['base': <xpath>,]
                ['field_name':(<xpath>, <regex>, <process>)|subelem,...] 
                                    }
            subelem:{'field_name':elems}
            field_name: str
            xpath: xpath语法字符串|None(base不能为空.表示base获取的文档树）
            regex: 正则表达式字符串|None
            process: [<func>,...]|None
            func:[func_name[:param|(param1,[param2,]),...];...]
```

注意: elems中非base的元素的处理分为两个过程, 1) 从元素列表中选取元素; 2)元素处理


3. 爬虫编排. 在Spider中添加后向处理规则。 
 在Spider中添加nextnodes属性，其定义如下:

        nextnodes = [(<node>, <urls>, <isdata>),...]
            node: SpiderNode子类(名称路径或类).  下一个处理的Spider节点. 
            urls:(<xpath>, <process>).传给下一个处理节点的url, 如果xpath是相对路径，则元素的前置路径为elems属性中base路径定义.
            xpath: xpath路径. 如果是相对路径，则用``elems``属性中的``base``元素
            isdata: True/False. 下一个节点是否需要该Spider获取的内容.
            
4. save属性设置
       save:={'dirver':<name>, 'param':{params}, 'alias':{alias}}
            name:=str 驱动名称
            param:=dict 初始化driver的字典
            alias:=dict item中字段和保存时的字段重命名
            
            
 5. 爬虫测试和执行
    * 方法1
    
```
    spd = SpiderExample(url)
    spd.pipeline_process()
```

    * 方法2
```
    from spiderflow import AsyncSpiderProcess, MemoryQueue
    asp = AsyncSpiderProcess(start_urls=[(SpiderExample, url),], queue=q)
    asp.start()
```
