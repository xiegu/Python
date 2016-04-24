#!/usr/bin/python
# encoding: utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import requests
from bs4 import BeautifulSoup
import MySQLdb
import time
import re

class MovieCrawler:
    def __init__(self):
    	 #fake browser, preventing from 403 error
         '''self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0',
                'Host': 'book.douban.com', 'Connection': 'keep-alive',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3'}
         '''
         self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0',
                'Connection': 'keep-alive',
                'Referer': 'http://book.douban.com/tag/?view=cloud',
                'Cookie': '	bid="kxpJWb9tjVo"; __utma=30149280.603118853.1413707596.1432436432.1432464641.30; __utmz=30149280.1432436432.29.22.utmcsr=bing|utmccn=(organic)|utmcmd=organic|utmctr=mysql%20%E6%8F%92%E5%85%A5%E4%B8%AD%E6%96%87; viewed="25913058_5921328_1281964_1054685_4770297_19952400_1473329_1103015_1041482_4242172"; __utmv=30149280.6944; ll="118159"; ap=1; ue="345881709@qq.com"; push_noty_num=0; push_doumail_num=2; pgv_pvi=5017648128; __utmb=30149280.5.10.1432464641; __utmc=30149280'}
         self.tag_list = []
        #movie list under each tag, set to empty after movie import is done
         self.movie_list = []
         #connect to database
         self.conn = MySQLdb.connect(host='localhost', user='root', passwd='292773', charset='utf8')
         self.cur = self.conn.cursor()
         self.conn.select_db('doubanmovie')
    def doCrawling(self):
    	 self.initTags()
    	 for tag in self.tag_list:
    		 try:
    			 self.getInfoWithTag(tag, 14)
    		 except Exception as e:
    			 print "error: %s" % (e)
    			 exit(-1)
    		 finally:
    			 self.conn.commit()
    	 self.cur.close()
    	 self.conn.close()
    def initTags(self):
    	 url = 'http://movie.douban.com/tag/?view=cloud'
    	 self.session = requests.Session()
    	 source_code = self.session.get(url, headers=self.headers)
    	 plain_text = source_code.text
    	 soup = BeautifulSoup(plain_text)
    	 print soup
    	 tags_soup = soup.find('div', {'class': 'indent tag_cloud'})
    	 for tag in tags_soup.findAll('a'):
    		 tag_name = tag.string.strip()
    		 self.tag_list.append(tag_name)
    	 sql = "INSERT INTO movie_tags (tag) VALUES(%s)"
    	 for t in self.tag_list:
    		 self.cur.execute(sql, (t,))
    	 self.conn.commit()
    def getInfoWithTag(self, tag, max_num=5000):
    	 index = 0
    	 step = 15
    	 while index <= max_num:
    		 time.sleep(5)
    		 url = 'http://www.douban.com/tag/%s/movie?start=%d' % (tag, index)
    		 try:
    			 source_code = self.session.get(url, headers=self.headers)
    			 plain_text = source_code.text
    			 soup = BeautifulSoup(plain_text)
    			 movie_soup = soup.find('div', {'class': 'mod movie-list'})
    			 index += step
    			 print tag, index
    			 #get movie information
    			 for movie_info in movie_soup.findAll('dd'):
    				 desc_raw = movie_info.find('div', {'class': 'desc'})
    				 rating_raw = movie_info.find('span', {'class': 'rating_nums'})
    				 desc = [ s.strip() for s in desc_raw.string.split('/') ]
    				 if desc_raw == None or rating_raw == None or len(desc) < 4 or desc[-2].isdigit():
    					 continue
    				 title_raw = movie_info.find('a')
    				 title = title_raw.string.strip()
    				 movie_id = title_raw['href'].strip().split('/')[-2]
    				 country = desc[0]
    				 year = [x.strip() for x in desc if re.match(ur'\d{4}', x.strip())][0]
    				 rating = rating_raw.string.strip()
    				 self.movie_list.append((movie_id, tag, title, country, year, rating))
    		 except IndexError:
    			 pass
    		 except Exception as e:
    			 print type(e), e
    			 time.sleep(60)
    		 sql = "INSERT INTO movies (id, tag, title, country, year, rating) VALUES(%s, %s, %s, %s, %s ,%s)"
    		 self.cur.executemany(sql, self.movie_list)
    		 self.movie_list = []


crawler = MovieCrawler()
crawler.doCrawling()























