# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import scrapy,os,datetime
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import shutil,os,pymysql
# 导入项目设置
from scrapy.utils.project import get_project_settings
#conn = pymysql.Connection(host="localhost", user="root", passwd="root", db='test', charset="UTF8")
#cursor = conn.cursor()
class MyImagesPipeline(ImagesPipeline):
    # 从项目设置文件中导入图片下载路径
    img_store = get_project_settings().get('IMAGES_STORE')
    def get_media_requests(self, item, info):
        ''' 多个url'''
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url)

    def item_completed(self, results, item, info, ):
        image_paths = [x["path"] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        file_path = item['file_path']
        # 定义分类保存的路径
        if os.path.exists(file_path) == False:
            os.mkdir(file_path)
        print image_paths
        ## pic  ==  full/80dd7db02e4da4e63f05d9d49c1092fc7fdcb43e.jpg
        pic_list = []
        for v in image_paths:
            pic_name = v.replace('full/','')
            pic_small_name =pic_name.replace('.jpg','')+'_s.jpg'
            pic_big_name = pic_name.replace('.jpg', '') + '_b.jpg'
            ##获取创建的图片名字
            # 将文件从默认下路路径移动到指定路径下
            # 移动图片
            shutil.move(self.img_store + 'full\\'+pic_name, file_path + "\\" + pic_name)
            # 移动缩略图
            #shutil.move(self.img_store + 'thumbs\\small\\'+ pic_name, file_path + "\\" + pic_small_name)
            shutil.move(self.img_store + 'thumbs\\big\\' + pic_name, file_path + "\\" + pic_big_name)
            #img_path_dict['img_path'] = file_path + "\\" + pic_name
            #img_path_dict['img_small_path'] = file_path + "\\" + pic_small_name
            #img_path_dict['img_big_path'] = file_path + "\\" + pic_big_name
            img_path_dict = ('picture/meinv/yushi/'+item['tag']+"/" + pic_name,'picture/meinv/yushi/'+item['tag']+"/" +pic_big_name)
            pic_list.append(img_path_dict)
        item["img_path"] = pic_list
        return item


class MysqlPipeline(object):
    def __init__(self):
        self.conn = pymysql.Connection(host="localhost", user="root", passwd="root", db='test1', charset="UTF8")
        # 创建指针
        self.cursor = self.conn.cursor()
    def process_item(self, item, spider):
        ###组装数据
        list = []
        datetime_now  =datetime.datetime.now()
        datetime_now = datetime.datetime.now()
        datetime_str = '{0}-{1}-{2} {3}:{4}:{5}'.format(datetime_now.year, datetime_now.month, datetime_now.day,datetime_now.hour, datetime_now.minute, datetime_now.second)
        ##增加type
        result = self.cursor.execute(u"select id from network_type where RESOURCETYPE ='p' and TYPENAME='{0}'".format(item['tag']))
        if result==0:
            self.cursor.execute("insert into network_type(PID,RESOURCETYPE,TYPENAME)values(%s,%s,%s) ",(3008,'p',item['tag']))
            typeid = self.cursor.lastrowid
            self.conn.commit()
        else:
            #tag_id = self.cursor.fetchall()
            #typeid = tag_id[0][0]
            return False

        types = ','+str(typeid)+','
        #print item['img_path']
        self.cursor.execute('select  id from network_picture order by cast(id as SIGNED INTEGER) desc limit 0,1')
        old_id = self.cursor.fetchone()
        if old_id:
            id_n = str(int(old_id[0]) + 1)
        else:
            id_n = str(1)
        for v in item['img_path']:
            path1 = v[0]
            path2 = v[1]
            self.cursor.execute(u'select  id from network_picture where FILEPATH="{0}" and fileScalPath="{1}"'.format(path1,path2))
            data = self.cursor.fetchone()
            if data:
                print u'该数据已经存在'
            else:
                a = (str(id_n),'',path1,'',types,0,datetime_str,path2)
            list.append(a)
            id_n = int(id_n) + 1
        print list
        self.cursor.executemany("insert into network_picture(ID,NAME,FILEPATH,FILESIZE,TYPES,STATUS,DATETIME,fileScalPath)values(%s,%s,%s,%s,%s,%s,%s,%s)", list)
        self.conn.commit()
        return item

