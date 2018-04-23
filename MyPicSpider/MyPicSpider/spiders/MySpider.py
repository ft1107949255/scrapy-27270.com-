# -*- coding: utf-8 -*-
import scrapy,os,urllib2
from scrapy.linkextractors import LinkExtractor   ##引入linkextractors  用于筛选链接和跟进链接，还有很多功能，可以去百度下
from scrapy.spiders import CrawlSpider, Rule     ##定义spider的模板，引入Rule规则
from MyPicSpider.items import PicspiderItem      ##引入定义的items.py
# 导入项目设置
from scrapy.utils.project import get_project_settings
from bs4 import BeautifulSoup
import time,pymysql
headers = {'User_agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'}
conn = pymysql.Connection(host="localhost", user="root", passwd="root", db='test1', charset="UTF8")
# 创建指针
cursor = conn.cursor()
class PicSpider(CrawlSpider):    ##继承模板CrawlSpider 普通模板继承Spider
	name = 'pic'     ###定义spider名    运行---$ scrapy crawl blog
	allowed_domains = ['www.27270.com']    ##  定义查找范围
	start_urls = ['http://www.27270.com/tag/513.html']   ###初始url
	####当有follow=True  则会跟进该页面
	####原理就是  spider在初始页面查找，同时查找帖子详情页的url和下一个分页，同时跟进下一个分页页面，继续查找下一个分页页面和上面的详情页url,详情页面使用回调函数进行采集
	rules = (
		###爬去索引页并跟踪其中链接
		###查找start_urls  所有的分页页面
		Rule(LinkExtractor(allow=r'/tag/[0-9]*_[0-9]*.html'),follow=True),
		###爬去items页面并将下载响应返回个头parse_item函数
		####查询每个分页页面的详情页
		Rule(LinkExtractor(allow=r'http://www.27270.com/ent/[a-z]*/[0-9]*/[0-9]*.html'), callback='parse_item', follow=False,),
		#Rule(LinkExtractor(allow=r'http://www.27270.com/zhuangxiusheji/[0-9]*/[0-9]*.html'), callback='parse_item', follow=False),
    )
	####详情页面回调函数
	def parse_item(self,response):
		start_url = response.url
		item = PicspiderItem()
		tag_name = response.xpath('//h1[@class="articleV4Tit"]/text()').extract()[0]
		# cursor.execute(u'select id from network_type  where PID=258 AND TYPENAME="{0}" limit 0,1'.format(tag_name))
		# old_id = cursor.fetchone()
		# if old_id:
		# 	exit()
		name = u'浴室'
		if name in tag_name:
			pass
		else:
			print u'----这是其他的分类----'
			return False
		li_list =  response.xpath('//ul[@class="articleV4Page l"]/li').extract()
		srcs = []
		for v in range(1, (len(li_list) - 3)):
			if v == 1:
				url_s = start_url
			else:
				url_s = start_url.replace('.html', '') + '_' + str(v) + '.html'
			try:
				request = urllib2.Request(url_s, headers=headers)
				response = urllib2.urlopen(request, timeout=200).read()
			except urllib2.URLError, err:
				print err, '错误的url' + url
			obj = BeautifulSoup(response, 'html.parser')
			try:
				pic_url = obj.find('center').find('img')['src']
			except:
				print u'----第一种获取方式失败----'
				try:
					pic_url = obj.find('div', {'id': 'picBody'}).find('img')['src']
				except:
					print u'----第二种方式获取失败----'
					try:
						pic_url = obj.find('p', attrs={"style": "text-align: center"}).find('img')['src']
					except:
						print u'----第三种获取方式失败----'
			srcs.append(pic_url)
		item['tag'] = tag_name
		item['file_path'] = '%s%s' %(get_project_settings().get('IMAGES_STORE'),tag_name)
		item['image_urls'] = srcs
		return item


