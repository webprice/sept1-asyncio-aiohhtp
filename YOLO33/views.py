from django.shortcuts import render,redirect
from django.conf import settings
from django.http import JsonResponse
from YOLO33.models import Data
import requests, random
import concurrent.futures
from bs4 import BeautifulSoup
from asgiref.sync import sync_to_async
import time
# #################################################################################################################
import asyncio
import aiohttp
import time
from bs4 import BeautifulSoup
LINKS_COUNTER = 0
LINKS_LIST = []
start_time = time.time()
NUMBER = 0
LOOP = True
DB_DATA_LIST = []
DB_DATA_OBJECT =[]
PAGES = 0

''' Scrapper functions code next '''

BASE_URL = 'https://www.olx.ua'
UA_LIST = [
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
]


def headers():
    # Pick a random user agent
    user_agent = random.choice(UA_LIST)
    # Set the headers

    headers = {'User-Agent': user_agent}
    return  headers

#
# #global var for counting number of items that will be scrapped from the OLX
# COUNTER = 0
# DATALOAD = []
# TITLE_URLS = []
# #Before start scraping - form the list of links of pages' links
# #hardcoded
# #this list will be set to run in the threadpoolexecutor and send as an argument to the next function:"get_ad_list"
# def get_links(group):
#     global TITLE_URLS
#     global COUNTER
#     TITLE_URLS.clear()
#     DATALOAD.clear()
#     url_list = []
#     pages = 0
#     if group == "hundred":
#         pages = 3
#         COUNTER = 100
#     if group == "twohundred":
#         pages = 5
#         COUNTER = 200
#     if group == "threehundred":
#         pages = 7
#         COUNTER = 300
#     for each in range(pages):
#         #print(each)
#         url_list.append(f'https://www.olx.ua/d/uk/transport/?page={each+1}')
#     print(url_list)
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         executor.map(get_ad_list, url_list)
#     # with concurrent.futures.ThreadPoolExecutor() as executor3:
#     #     executor3.map(load_to_db, DATALOAD)
#         print("executor._work_queue.qsize()",executor._work_queue.qsize())
#     print(DATALOAD)
#     load_to_db(DATALOAD)
#     print("TITLE URLSSSSSSSSSSSSSSSSSSSSSSSSSSS",len(TITLE_URLS))
#     # with concurrent.futures.ThreadPoolExecutor() as executor:
#     #     executor.map(get_final, TITLE_URLS)
#     #     print("executor._work_queue.qsize()",executor2._work_queue.qsize())
#     return  None
#
#
# #Here we scrapping all the links to the individual Ads(posts)
# #COUNTER controlling(according to the accounts' types) how many links the request gonna get in the next function
# def get_ad_list(page_url):
#     global COUNTER
#     global TITLE_URLS
#     title_urls = []
#     # for link in page_url:
#     page = requests.get(page_url, headers=headers())
#     soup = BeautifulSoup(page.content, 'html.parser')
#     items = soup.find_all('div',attrs={'data-cy':'l-card'})
#     #print(len(items))
#     for item in items:
#             if COUNTER < 0:
#                 break
#             else:
#                 link = item.a.get('href')
#                 if not link.startswith('https://'):
#                     title_urls.append(link)
#                     TITLE_URLS.append(link)
#                     COUNTER -=1
#                 else:
#                     pass
#     print(len(title_urls))
#     print("TITLE_URLS",len(TITLE_URLS))
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         executor.map(get_final, title_urls)
#         print("executor._work_queue.qsize()",executor._work_queue.qsize())
#     return None
#
#
# #Here we get the data from the individual Ad(post), parsing it and saving it to the DataBase
# def get_final(url):
#     page = requests.get(f'{BASE_URL}{url}', headers=headers())
#     soup = BeautifulSoup(page.content, 'html.parser')
#     items = soup.find(id='root')
#     xxx = items.find_all('div', {'class': 'swiper-zoom-container'}, limit=1)
#     title = items.h1.get_text()
#     seller = items.h4.get_text()
#     price =items.h3.get_text()
#     photo = xxx[0].find_next('img')['src']
#     dataload = Data(
#             title=title,
#             price=price,
#             photo=photo,
#             seller=seller,
#             )
#     DATALOAD.append(dataload)
#
# def load_to_db(bulk_list):
#     # delete all data
#     Data.objects.all().delete()
#     obj = Data.objects.bulk_create(bulk_list)
#     print("LOADED TO DB")




async def get_links(session,url):
    async with session.get(url) as resp:
        text = await resp.text()
        soup = BeautifulSoup(text, 'html.parser')
        items = soup.find_all('div', attrs={'data-cy': 'l-card'})
        global LINKS_COUNTER
        global LOOP
        global PAGES
        # global LINKS_LIST
        links_list2=[]
        for link in items:
            if LINKS_COUNTER == PAGES:
                LOOP = False
                break
            ad_link = link.a.get('href')
            if ad_link.startswith('https://'):
                pass
            else:
                links_list2.append(ad_link)
                LINKS_LIST.append(ad_link)
                LINKS_COUNTER += 1
        return links_list2
async def get_ads_links(text):
    async with aiohttp.ClientSession() as session:
        soup = BeautifulSoup(text, 'html.parser')
        items = soup.find_all('div', attrs={'data-cy': 'l-card'})
        global LINKS_COUNTER
        # global LINKS_LIST
        tasks2 = []
        for link in items:
            if LINKS_COUNTER == PAGES:
                break
            ad_link = link.a.get('href')
            tasks2.append(asyncio.ensure_future(get_ads_data(session, ad_link)))
            data = await asyncio.gather(*tasks2)
            print("done")
            if ad_link.startswith('https://'):
                pass
            else:
                LINKS_LIST.append(ad_link)
                LINKS_COUNTER += 1


async def get_ads_data(session,url):
    async with session.get(f'https://www.olx.ua/{url}') as resp:
        text = await resp.text()
        return await parse_get_ads_data(text)


async def parse_get_ads_data(text):
    #print(text)
    soup =  BeautifulSoup(text, 'html.parser')
    items = soup.find(id='root')
    xxx = items.find_all('div', {'class': 'swiper-zoom-container'}, limit=1)

    try:
        title = items.h1.get_text()
        seller = items.h4.get_text()
        price = items.h3.get_text()
        photo = xxx[0].find_next('img')['src']
        # DB_DATA_LIST.append([title,seller,price,photo])
        # dataload = Data(
        #     title=title,
        #     seller=seller,
        #     price=price,
        #     photo=photo,
        # )
        # DB_DATA_LIST.append(dataload)
        DB_DATA_LIST.append({'title':title,
                            'seller': seller,
                            'price':price,
                            'photo': photo,})
        print(title, seller, price, photo)

        # print(x)
        # return (title, seller, price, photo)
    except:
        # print("ERROR")
        pass
        # dataload = Data(
        #     title=None,
        #     seller= None,
        #     price= None,
        #     photo= None,
        # )
        # DB_DATA_LIST.append(dataload)
# def writer():

    # dataload = Data(
    #     title='1231451',
    #     seller= '15213123',
    #     price= '153236523',
    #     photo= '612643'
    # )
    # print(dataload)
# def load_to_db(bulk_list):
#     global DB_DATA_OBJECT
#     for every in bulk_list:
#         x = Data(
#             title=every[0],
#             seller=every[1],
#             price=every[2],
#             photo=every[3],
#         )
#         DB_DATA_OBJECT.append(x)
#
# def load_to_db2(bulk_list):
#     Data.objects.bulk_create(bulk_list)


async def main(amount):
    async with aiohttp.ClientSession() as session:
        tasks = []
        tasks2 = []
        global LOOP
        global NUMBER
        # while LOOP:
        for number in range(amount):
            url = f'https://www.olx.ua/d/uk/transport/?page={number+1}'
            tasks.append(asyncio.ensure_future(get_links(session, url)))
        original_url = await asyncio.gather(*tasks)
        for link in LINKS_LIST:
            tasks2.append(asyncio.ensure_future(get_ads_data(session, link)))
        original_url = await asyncio.gather(*tasks2)

        # print(len(LINKS_LIST))
        print(len(DB_DATA_LIST))
        print(DB_DATA_LIST)
        # print(LINKS_LIST)
        # print(len(LINKS_LIST))






#This function will be a decorator, checking if user logged in or not
def require_login(func):
    def login_result(request, *args, **kwargs):
        if not request.user.is_authenticated:
            print("user is not logged in, redirected: ",{request})
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        else:
            print(f"user: {request.user.username} logged in, return views function: {func.__name__}")
            return func(request, *args, **kwargs)
    return login_result


#Index.html function, send the user role in context.
#Role needed to display specific parts of HTML code via DJANGO Tags
@require_login
def index(request):
    role = None
    if request.user.groups.filter(name='hundred').exists():
        role = 'hundred'
    if request.user.groups.filter(name='twohundred').exists():
        role = 'twohundred'
    if request.user.groups.filter(name='threehundred').exists():
        role = 'threehundred'
    return render(request,'index.html',context = {'role':role})


#The trigger function/route. When user clicking on "refresh button" - load_data invokes
#it checks the user group, then cleaning the DB, triggering the next function "get_links"
#after success - grabs the new data from the DB, converts it to list and return it as a JSON response
#Finally JS script on the front-end parsing that JSON data and build HTML table out of it.
@require_login
def load_data(request):
    global PAGES
    start_time = time.time()

    if request.user.groups.filter(name='hundred').exists():
        pages=3
        PAGES=100
        # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main(amount=pages))
        ob = [Data(title=i['title'], seller=i['seller'], price=i['price'], photo=i['photo']) for i in DB_DATA_LIST]
        obj = Data.objects.bulk_create(ob)
        data = list(Data.objects.values('id', 'title', 'price', 'photo', 'seller').order_by('-id')[:100])
        print(PAGES, pages)
    if request.user.groups.filter(name='twohundred').exists():
        PAGES = 200
        pages = 5
        # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main(amount=pages))
        ob = [Data(title=i['title'], seller=i['seller'], price=i['price'], photo=i['photo']) for i in DB_DATA_LIST]
        obj = Data.objects.bulk_create(ob)
        # invoke scrape
        # get_links('threehundred')
        # send the new data to the front
        data = list(Data.objects.values('id', 'title', 'price', 'photo', 'seller').order_by('-id')[:200])
        print(PAGES, pages)
    if request.user.groups.filter(name='threehundred').exists():
        # delete all data
        PAGES=300
        pages = 7
        # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main(amount=pages))
        ob = [Data(title=i['title'], seller=i['seller'], price=i['price'], photo=i['photo']) for i in DB_DATA_LIST]
        obj = Data.objects.bulk_create(ob)
        # invoke scrape
        # get_links('threehundred')
        # send the new data to the front
        data = list(Data.objects.values('id', 'title', 'price', 'photo', 'seller').order_by('-id')[:300])
        print(PAGES, pages)

    print("--- %s seconds ---" % (time.time() - start_time))
    return  JsonResponse(data,safe=False)


#Shows the existing data from the database.
#This function invoke by clicking on "existing data" button on the front-end
@require_login
def existing_data(request):
    if request.user.groups.filter(name='hundred').exists():
        data = list(Data.objects.values('id', 'title', 'price', 'photo', 'seller').order_by('-id')[:100])
    if request.user.groups.filter(name='twohundred').exists():
        data = list(Data.objects.values('id', 'title', 'price', 'photo', 'seller').order_by('-id')[:200])
    if request.user.groups.filter(name='threehundred').exists():
        data = list(Data.objects.values('id', 'title', 'price', 'photo', 'seller').order_by('-id')[:300])
    #qs_json = serializers.serialize('json', data)
    return  JsonResponse(data,safe=False)


#Removed the row from the database by it's <id>
#This function invoke by clicking on "delete" button in the table at the front-end
@require_login
def test_delete(request,id):
    Data.objects.filter(id=id).delete()
    data = list(Data.objects.values('id', 'title', 'price', 'photo', 'seller').order_by('id'))
    return  JsonResponse(data,safe=False)
