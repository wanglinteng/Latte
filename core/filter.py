from bs4 import BeautifulSoup

from util.common import url_decoder

"""
    各种爬取过滤器，直白说从一堆杂乱的数据中拿到你想要的！
    json 输入， json 输出 OR html 输出， json 输出
    NOT garbage in，garbage out

    search_001: 搜索结果解析器  IN(json)/OUT(json)
"""


def search_001(data):
    """
        搜索结果解析：

            zvideo  # 视频
                https://www.zhihu.com/zvideo/1386442207516278784

            wiki_box  # 话题
                https://api.zhihu.com/topics/19551455

            search_result # 搜索结果
                article https://api.zhihu.com/articles/362094095
                answer https://api.zhihu.com/answers/2051939405
                videoanswer https://www.zhihu.com/question/20008942/answer/1981804371  # 量少忽略

            relevant_query  # 搜索推荐
                 https://www.zhihu.com/search?q=%E6%96%B0%E6%B5%AA%E5%BE%AE%E5%8D%9A&utm_content=search_relatedsearch&type=content

            search_club // 不适合爬取

            knowledge_result // 不适合爬取
                电子书
                    https://www.zhihu.com/market/pub/119584018/manuscript/1071910337044873216
                带广告问答
                    https://www.zhihu.com/question/312456927/answer/1172171000

            knowledge_ad  // 不适合爬取
                盐选专栏
                     https://www.zhihu.com/remix/albums/1171945943569555456/tracks/1171947062626668544/content?km_channel=search&origin_label=search
                     https://www.zhihu.com/market/specials/1124754111790456832
                电子书
                    https://www.zhihu.com/pub/book/119571280
                Live讲座
                    https://www.zhihu.com/lives/913829452423774208

        链接转换

            # articles
            https://api.zhihu.com/articles/367168940 -> https://zhuanlan.zhihu.com/p/367168940

            # zvideo
            https://www.zhihu.com/zvideo/1363956955149594625

            # answer
            https://api.zhihu.com/answers/1969291425
            https://api.zhihu.com/questions/341407139 -> https://www.zhihu.com/question/341407139/answer/1969291425

            # relevant_query -- 直接存储
            list ['谈谈当代中国如何突破美国的核心技术封锁', '中核战略规划研究总院']

            # wiki_box -- 信息全面无需再次请求
            https://api.zhihu.com/topics/19551455
    """

    results = {"article": [], "relevant_query": [], "topic": [], "zvideo": [], "answer": []}
    for d in data:

        type = d.get('type', '')

        # search_result
        if type == 'search_result':
            object = d.get('object', {})
            object_type = object.get('type', '')

            # article
            if object_type == 'article':
                url = object.get('url', '')
                p_id = url.split('/')[-1]
                u = "https://zhuanlan.zhihu.com/p/{}".format(p_id)
                results['article'].append(u)

            # answer
            if object_type == 'answer':
                url = object.get('url', '')  # https://api.zhihu.com/answers/1721963692
                question_url = object.get('question', {}).get('url', '')  # https://api.zhihu.com/questions/442751850
                answer_id = url.split('/')[-1]
                question_id = question_url.split('/')[-1]
                u = "https://www.zhihu.com/question/{}/answer/{}".format(question_id, answer_id)
                results['answer'].append(u)

            # topic
            if object_type == 'topic':
                results['topic'].append(object)

        # wiki_box(topic)
        if type == 'wiki_box':
            object = d.get('object', {})
            object_type = object.get('type', '')
            if object_type == 'wiki_box':
                results['topic'].append(object)

        # relevant_query
        if type == 'relevant_query':
            query_list = d.get('query_list', {})
            query_list = [i.get('query') for i in query_list]
            results['relevant_query'] = query_list

        # zvideo
        if type == 'zvideo':
            object = d.get('object', {})
            zvideo_id = object.get('zvideo_id', '')
            u = "https://www.zhihu.com/zvideo/{}".format(zvideo_id)
            results['zvideo'].append(u)

    return results


def article_html_001(html):
    """ 文章网页解析 """
    soup = BeautifulSoup(html, 'lxml')

    title = soup.find('h1', class_='Post-Title')
    title = title.get_text() if title else ''

    content = soup.find('div', class_='Post-RichTextContainer')
    content = content.get_text() if content else ''

    topics = []
    links = soup.find_all('span', class_='Tag-content')
    for link in links:
        try:
            href = link.find('a', class_='TopicLink').get('href')
            topicId = href.split('/')[-1].strip(' ')
            topicName = link.find(id='null-toggle').get_text()
            topics.append({"topicId": topicId, "topicName": topicName})
        except:
            continue
    result = {"title": title, "content": content, "topics": topics}

    return result


def answer_html_001(html):
    """ 问答网页解析 """
    soup = BeautifulSoup(html, 'lxml')

    title = soup.find('h1', class_='QuestionHeader-title')
    title = title.get_text() if title else ''

    content = soup.find('div', class_='RichContent-inner')
    content = content.get_text() if content else ''

    topics = []
    links = soup.find_all('span', class_='Tag-content')
    for link in links:
        try:
            href = link.find('a', class_='TopicLink').get('href')
            topicId = href.split('/')[-1].strip(' ')
            topicName = link.find(id='null-toggle').get_text()
            topics.append({"topicId": topicId, "topicName": topicName})
        except:
            continue
    result = {"title": title, "content": content, "topics": topics}

    return result


def zvideo_html_001(html):
    """ 视频网页解析 """
    soup = BeautifulSoup(html, 'lxml')

    title = soup.find('h1', class_='ZVideo-title')
    title = title.get_text() if title else ''

    topics = []
    links = soup.find_all('a', class_='ZVideoTag')
    for link in links:
        try:
            href = link.get('href')
            topicId = href.split('/')[-2].strip(' ')
            topicName = link.get_text()
            topics.append({"topicId": topicId, "topicName": topicName})
        except:
            continue
    result = {"title": title, "content": "", "topics": topics}

    return result


def multi_html_001(url, html):
    """ 兼容001各类型解析，类型由url区分"""
    d = {}
    t = url_decoder(url)
    if t == 'article':
        d = article_html_001(html=html)
    if t == 'answer':
        d = answer_html_001(html=html)
    if t == 'zvideo':
        d = zvideo_html_001(html=html)
    d['url'] =url
    return d
