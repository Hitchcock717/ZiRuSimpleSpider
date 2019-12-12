#!/usr/bin/env python
# -*-coding:utf-8-*-
'''
    爬取自如租房信息(海淀区)
'''

# 导入开发模块
import requests
from bs4 import BeautifulSoup
import csv

fw = open('Ziru.txt','w+', encoding='utf-8')

headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 '
        'Safari/537.36'
}

urls = []
detail_urls = []

for i in range(1,7):
    prefix = 'http://www.ziroom.com/z/z0-d23008618-p%s' %i # 列表解析式，需一一对应
    suffix = '/?qwd=%E5%8C%97%E4%BA%AC'
    src_url = prefix + suffix
    print(src_url)
    urls.append(src_url)

temp1 = []
# <......基本信息......> #
for url in urls:
    resp = requests.get(url, headers=headers)
    html_data = resp.text
    soup = BeautifulSoup(html_data, 'html.parser')
    # print(soup)
    list_box = soup.find('div', class_='Z_list-box')
    items = list_box.find_all('div', class_='item')
    li_box = soup.find_all('div', class_='info-box')
    for i in list(range(len(li_box))):
        title = li_box[i].find('h5').get_text()
        desc = li_box[i].find('div', class_='desc').get_text().replace('\n\n	                	                    ',' ')
        desc1 = desc.replace('\t                \t              \n','')
        tags = li_box[i].find('div', class_='tag').get_text()
        tip = li_box[i].find('div', class_='tips air-high')
        if tip:
            warning = tip.get_text()
        else:
            warning = 'N/A'

        temp1.append(title)
        temp1.append(desc1)
        temp1.append(tags)
        temp1.append(warning)

        h5 = li_box[i].find(''
                            'h5')
        durl = h5.find('a').attrs['href']
        new_url = 'http:' + durl
        detail_urls.append(new_url)

temp = []
# <......具体信息......> #
for du in detail_urls:
    resp = requests.get(du, headers=headers)
    html_data = resp.text
    soup = BeautifulSoup(html_data, 'html.parser')

    main_area = soup.find_all('section', class_='Z_container Z_main')
    # print(main_area[0])
    for i in list(range(len(main_area))):
        # <...右边栏 朝向 户型...> #
        home_desc = main_area[i].find('div', class_='Z_home_b clearfix')
        infos = home_desc.find_all('dd')
        direct = infos[1].get_text()
        design = infos[2].get_text()

        temp.append(direct)
        temp.append(design)

        # <...右边栏 位置 电梯 年限 暖气 绿化...> #
        home_detail = main_area[i].find('ul', class_='Z_home_o')
        lis = home_detail.find_all('li')
        d_loc = lis[0].find('span', class_='ad')

        if d_loc:
            loc = d_loc.get_text()
        else:
            loc = 'N/A'

        lift = lis[2].find('span', class_='va').get_text()
        age = lis[3].find('span', class_='va').get_text()

        temp.append(loc)
        temp.append(lift)
        temp.append(age)

        try:
            gas = lis[4].find('span', class_='va').get_text()
            temp.append(gas)
        except IndexError:
            print('cannot find \'gas\' entry!')

        try:
            green = lis[5].find('span', class_='va').get_text()
            temp.append(green)
        except IndexError:
            print('cannot find \'green\' entry!')

        # <...中间 简介...> #
        try:
            home_text_desc = main_area[i].find('div', {'id': 'homedesc'})
            paras = home_text_desc.find('div', class_='Z_rent_desc')

            if paras:
                words = paras.get_text().replace('\n					', ' ')
            else:
                words = 'N/A'

            temp.append(words)

        except AttributeError:
            print('cannot find \'desc\' entry!')

        # <...下方 是否空置 空置时长 空气检测报告...> #
        try:
            home_status = main_area[i].find('div', {'id': 'areacheck'})
            print(home_status)
            lis = home_status.find_all('li')
            vacation = lis[0].find('span', class_='info_value').get_text()
            temp.append(vacation)

            try:
                date = lis[1].find('span', class_='info_value').get_text()
                temp.append(date)
            except IndexError:
                print('cannot find \'date\' entry!')

            try:
                test = lis[2].find('a', class_='info_value_active text_underline')

                if test:
                    # <...报告链接 房间号 温度（实时） 湿度 空气质量...> #
                    report_url = test.attrs['href']
                    temp.append(report_url)

                    resp = requests.get(report_url, headers=headers)
                    html_data = resp.text
                    soup = BeautifulSoup(html_data, 'html.parser')

                    try:
                        item = soup.find('div', class_='item')
                        room = item.find('h1').get_text()

                        spans = item.find_all('span')
                        temper = spans[0].find('i').get_text()
                        humid = spans[1].find('i').get_text()

                        tds = item.find_all('td')
                        index = tds[0].get_text()
                        num = tds[1].get_text()
                        result = tds[2].get_text()

                        temp.append(room)
                        temp.append(temper)
                        temp.append(humid)
                        temp.append(index)
                        temp.append(num)
                        temp.append(result)

                    except AttributeError:
                        print('cannot find \'item\' entry!')

            except IndexError:
                print('cannot find \'test\' entry!')

            else:
                report_url = 'N/A'

        except AttributeError:
            print('cannot find \'home_status\' entry!')

        # <...下方 出租状态 出租时长...> #
        try:
            rent_info = main_area[i].find('div', {'id': 'rentinfo'})
            lis = rent_info.find_all('li')
            rentstatus = lis[0].find('span', class_='info_value').get_text()
            rentime = lis[1].find('span', class_='info_value').get_text()

            temp.append(rentstatus)
            temp.append(rentime)

            # <...下方 房间号 签约日期 室友...> #
            meet_info = main_area[i].find('div', {'id': 'meetinfo'})
            infos = meet_info.find_all('div', class_='info')

            for info in infos:
                house_name = info.find('span', class_='housename').get_text()
                person = info.find('p', class_='person mt10')
                temp.append(person)

                # <...室友性别/房屋大小 室友星座/房屋朝向 室友简介/房屋出租时间...> #
                spans = person.find_all('span')
                sex_or_size = spans[0]
                constel_or_direct = spans[1]

                temp.append(sex_or_size)
                temp.append(constel_or_direct)

                try:
                    info_or_rentime = spans[2]
                    temp.append(info_or_rentime)
                except IndexError:
                    print('cannot find \'info_or_rentime\' entry!')

                try:
                    sign_date = info.find('span', class_='time').get_text()
                    temp.append(sign_date)
                except AttributeError:
                    print('cannot find \'sign_date\' entry!')

        except AttributeError:
            print('cannot find \'rent_info\' entry!')

        # <...右下方 管家名称 联系方式...> #
        try:
            keeper_info = main_area[i].find('div', class_='Z_keeper_info')
            ps = keeper_info.find_all('p')
            keeper_name = ps[0].get_text()
            keeper_contact = ps[1].get_text()

            temp.append(keeper_name)
            temp.append(keeper_contact)

        except AttributeError:
            print('cannot find \'keeper_info\' entry!')

        try:
            # <...右方 收藏次数...> #
            collect = main_area[i].find('p', class_='collecttip').get_text()
            temp.append(collect)
        except AttributeError:
            print('cannot find \'collect\' entry!')
fw.write(str(temp1) + '\n')
fw.write(str(temp))
fw.flush()
fw.close()
