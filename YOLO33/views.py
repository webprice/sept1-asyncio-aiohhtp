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
# BASE_URL = 'https://www.olx.ua'
# UA_LIST = [
#   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
#   'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
#   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
#   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
#   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
# ]
#
#
# def headers():
#     # Pick a random user agent
#     user_agent = random.choice(UA_LIST)
#     # Set the headers
#
#     headers = {'User-Agent': user_agent}
#     return  headers


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
    try:
        soup =  BeautifulSoup(text, 'html.parser')
        items = soup.find(id='root')
        xxx = items.find_all('div', {'class': 'swiper-zoom-container'}, limit=1)

        try:
            title = items.h1.get_text()
            seller = items.h4.get_text()
            price = items.h3.get_text()
            photo = xxx[0].find_next('img')['src']
            DB_DATA_LIST.append({'title':title,
                                'seller': seller,
                                'price':price,
                                'photo': photo,})
            print(title, seller, price, photo)
        except:
            pass
    except:
        pass

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
        # print(len(DB_DATA_LIST))
        # print(DB_DATA_LIST)


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
