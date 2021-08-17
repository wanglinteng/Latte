#### Latte 是什么？
```
无聊的七夕情人节，帝都下了两天雨，在星巴克咖啡续命，大杯冰拿铁哇！ (¬‿¬)

走错片场了，重来

Latte 是一个灵活[简易]知乎爬虫啦！(→_→)
```


#### Latte 有什么功能？
```
1. 爬取知乎话题及话题树结构

2. 爬取文章、问答、视频及其对应的话题

3. 其他功能开发中，如果实现了其他模块，欢迎 Pull Request
```

####  Latte 如何使用？
```
1. 安装 python 及其 requirements.txt

2. 知乎搜索请求 header 中需要携带 x-zse-96，此参数值需依赖 nodejs 生成

    cd util/x-zse-96/
    npm install jsdom

3. 设置 config.ini 中 storage_redis_*(存储) redis 配置以及 proxy_redis_*(代理) redis 配置

4. cd example 可以执行example_1.py
```

#### Latte 结果示例~
```
以下示例采用filter.py中*_001过滤器，可根据需求改造，欢迎提交更多过滤器模板

文件存储目录结构

    output
    └── 20210816
        ├── answer
        ├── article
        ├── relevant_query
        └── zvideo
    
        1. answer  # 问答
            
            {"title": "请问今天武汉具体天气咋样？", "content": "谢邀，不过这个问题也值得发知乎吗 ", "topics": [{"topicId": "19553158", "topicName": "天气"}, {"topicId": "19570564", "topicName": "武汉"}], "url": "https://www.zhihu.com/question/330263558/answer/721334870"}
        
        2. article  # 文章
        
            {"title": "郑州已发现多起家庭聚集性感染", "content": "从已公布的119个确诊病例和无症状感染者活动轨迹分析，郑州已发现多起家庭聚集性感染，均属于一人感染、全家中招。郑州市疾控中心工作人员建议，请市民尽量减少不必要外出，不扎堆聚会，遵守“咳嗽礼仪”，保持手部卫生。", "topics": [], "url": "https://zhuanlan.zhihu.com/p/397488064"}
        
        3. relevant_query  # 搜索推荐
        
            {"我省发布雷暴大风蓝色预警": ["暴雨蓝色预警", "台风蓝色预警", "雷雨大风黄色预警", "雷暴天气", "湖南发布暴雨预警", "雷雨风"]}
        
        4. zvideo  # 视频
        
            {"title": "教育新动态:31省市延迟开学", "content": "", "topics": [{"topicId": "19589820", "topicName": "学校"}], "url": "https://www.zhihu.com/zvideo/1221074157909598208"}
        
redis存储

    # https://www.zhihu.com/topic/19610713/hot

    1. 话题树 

        19610713 {19563616, 19585537, 19904358, 19710321, 21302866, 19770870}  # 官方显示是有向无环图，实际存在自环

    2. 话题信息
        	
        19915165 {'name': '时尚配饰', 'introduction': '', 'questions_count': 837, 'best_answers_count': 436, 'followers_count': 1019305, 'best_answerers_count': 38}
```

#### npm 安装
```
1. 如何在CentOS 7上安装Node.js和npm?

    https://www.myfreax.com/how-to-install-node-js-on-centos-7/
```


#### 捐赠支持~
```
帮我脱单 OR 微信/支付宝赞助一杯
```
|  微信支付 [WeChat Pay]  |  支付宝支付 [Alipay] |
|----------|-------------|  
| <img src="other/Wechat.jpeg" width="200px" height="200px"/> | <img src="other/Alipay.jpeg" width="200px" height="200px"/>|

    
