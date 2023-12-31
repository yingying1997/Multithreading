import requests # 导入 requests 库，用于发送 HTTP 请求
from lxml import etree # 导入 lxml 库，用于解析 HTML
import re # 导入 re 库，用于正则表达式操作
import threading # 导入 threading 库，用于多线程编程
from queue import Queue # 导入 Queue 类，用于创建队列

# 请求头
head = {
    'Referer':'https://www.fabiaoqing.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
}

# 生产者类，用于获取图片链接
class Producer(threading.Thread):
    # 初始化方法
    def __init__(self, page_queue, img_queue):
        # 必须要执行父类当中的 init 方法完成初始化
        super().__init__()
        # 设置页码队列属性
        self.page_queue = page_queue
        # 设置图片队列属性
        self.img_queue = img_queue

    # 重写 run 方法
    def run(self):
        # 循环取队列里面的数据，直到队列数据为空
        while True:
            # 如果页码队列为空
            if self.page_queue.empty():
                # 退出循环
                break
            # 从页码队列中获取 url
            url = self.page_queue.get()
            # 打印 url
            # print(url)
            # 调用 parse_html 方法解析页面
            self.parse_html(url)

    # 定义解析页面的方法
    def parse_html(self, url):
        # 发送 get 请求，获取响应对象
        res = requests.get(url, headers=head)
        # 设置响应编码为 utf-8
        res.encoding = 'utf-8'
        # 打印响应内容
        # print(res.text)
        # 解析响应内容
        html = etree.HTML(res.text)
        # 获取所有的 img 标签
        images = html.xpath('//div[@class="tagbqppdiv"]/a/img')
        # 遍历循环每一个 img 标签
        for img in images:
            # 获取图片 url
            img_url = img.xpath('@data-original')[0]
            # 获取图片标题
            img_title = img.xpath('@alt')[0]
            # 使用正则表达式替换标题中的特殊字符
            title = re.sub(r'[<>:？.()/\\]', '', img_title)
            # 将图片 url 和标题作为元组放入图片队列中
            self.img_queue.put((img_url, title))
            # 打印图片队列的大小
            # print(self.img_queue.qsize())

# 消费者类，用于下载图片
class consumer(threading.Thread):
    # 初始化方法
    def __init__(self, img_queue):
        # 必须要执行父类当中的 init 方法完成初始化
        super().__init__()
        # 设置图片队列属性
        self.img_queue = img_queue

    # 重写 run 方法
    def run(self):
        # 循环取队列里面的数据，直到队列数据为空
        while True:
            # 打印图片队列的大小
            print(self.img_queue.qsize())
            # # 如果图片队列为空
            # if self.img_queue.empty():
            #     # 退出循环
            #     break
            # 从图片队列中获取图片数据
            img_data = self.img_queue.get()
            # 将图片数据解包为 url 和标题
            url, title = img_data
            # 发送 get 请求，获取图片响应
            res = requests.get(url, headers=head)
            # 打开文件，将图片内容写入到文件中
            with open(f'pictures/{title}.jpg', 'wb') as f:
                f.write(res.content)
            print(f'{title}正在下载')

# 主程序
if __name__ == '__main__':
    # 存放 url 的队列
    page_queue = Queue()
    # 创建图片队列
    img_queue = Queue()
    # 循环页码
    for i in range(1, 5, 1):
        # 创建 url
        url = f'https://www.fabiaoqing.com/biaoqing/lists/page/{i}.html'
        # url 放入页码队列
        page_queue.put(url)

    # 创建空列表
    lst = []

    # 创建生产者
    for i in range(3):
        # 将存放的 url 队列传递给生产者
        t = Producer(page_queue, img_queue)
        # 开启线程
        t.start()
        # 添加线程到列表
        lst.append(t)
    # # join：等子线程结束了才会执行主线程的代码
    # # 加 join 是生产完了再下载，不加是边生产边下载
    # # 如消费者 run 方法里判断图片队列为空，就需要加 join
    # for i in lst:
    #     i.join()

    # 创建消费者
    for i in range(3):
        # 将图片队列传递给消费者
        t1 = consumer(img_queue)
        # 开启线程
        t1.start()