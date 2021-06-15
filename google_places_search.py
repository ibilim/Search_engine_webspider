### data mining from google maps

import urllib.parse, urllib.request, urllib.error
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import re
import pandas as pd
import numpy as np
#ctx = ssl.create_default_context()
#ctx.check_hostname = False
#ctx.verify_mode =ssl.CERT_NONE
source='https://www.google.com/search?q='

head={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

def get_infos(place):
    url=source+quote_plus(place)   ##makes research 
    req=urllib.request.Request(url,headers=head)
    file=urllib.request.urlopen(req).read()
    soup=BeautifulSoup(file,'html.parser')
    place_info={}     ## creates dictionary
    ###
    tags_name=soup('div')
    company_names=[]
    for tag in tags_name:
        if  tag.get('class',None)!=None and ' '.join(tag.get('class',None))=='BNeawe deIvCb AP7Wnd':
            company_names.append(tag.contents)
    place_info['Company_name']=company_names[0][0]
    print('Finding company name...')
    print('company name:',place_info['Company_name'])
    ###
    tags=soup('span')
    addr_phone=[]
    for tag in tags:
        if tag.get('class',None)!= None and ' '.join(tag.get('class',None))=='BNeawe tAd8D AP7Wnd':
            addr_phone.append(tag.contents[0])
    place_info['address']=addr_phone[0]
    if addr_phone[-1][:3].isnumeric() and addr_phone[-1][-3:].isnumeric():
        place_info['phone']=addr_phone[-1]
    else:
        place_info['phone']='None'
    ###
    tags_web=soup('a')
    web_pages=[]
    for tag in tags_web:
        if tag.get('class',None)!= None and ' '.join(tag.get('class',None))=='VGHMXd':
            web_pages.append(tag.get('href',None))
        else:
            continue
    if len(web_pages)>1:
        web_page=re.findall(r'(https?:\/\/\d?\d?[\w\W]+/)',web_pages[1])
    else:
        web_page=[None]
        
    place_info['web_page']=web_page[0]
    ###
    if place_info['web_page']==None:
        place_info['twitt_account']='None'
        place_info['facebook_account']='None'
        place_info['instagram_account']='None'
    else:
        try:
            req=urllib.request.Request(place_info['web_page'],headers=head)
            file=urllib.request.urlopen(req).read()
            soup=BeautifulSoup(file,'html.parser')
            for i in str(soup).split():
                if 'instagram.com' in i:
                    try:
                        place_info['instagram_account']='https://www.' +re.findall(r'instagram.com/\w+/?',i)[0]
                    except:
                        place_info['instagram_account']='None'

                if 'twitter.com' in i:
                    try:
                        place_info['twitt_account']='https://www.' +re.findall(r'twitter.com/\w+/?',i)[0]
                    except:
                        place_info['twitt_account']='None'

                if 'facebook.com' in i:
                    try:
                        place_info['facebook_account']='https://www.' +re.findall(r'facebook.com/\w+/?',i)[0]
                    except:
                        place_info['facebook_account']='None'
            if 'instagram.com' not in str(soup):
                place_info['instagram_account']='None'
            if 'twitter.com' not in str(soup):
                place_info['twitt_account']='None'
            if 'facebook.com' not in str(soup):
                place_info['facebook_account']='None'
        except HTTPError as e:
            if hasattr(e, 'reason'):
                #print('We failed to reach a server.')
                #print('Reason: ', e.reason)
                place_info['twitt_account']='None'
                place_info['facebook_account']='None'
                place_info['instagram_account']='None'
            elif hasattr(e, 'code'):
                #print('The server couldn\'t fulfill the request.')
                #print('Error code: ', e.code)
                place_info['twitt_account']='None'
                place_info['facebook_account']='None'
                place_info['instagram_account']='None' 
    ###
    if place_info['web_page']==None:
        place_info['e-mail']='None'
    else:
        try:
            req=urllib.request.Request(place_info['web_page'],headers=head)
            file=urllib.request.urlopen(req).read()
            soup=BeautifulSoup(file,'html.parser')
            e_mails=[i for i in str(soup).split() if '@' in i]
            emails=re.findall(r'[-?.?_?\w]+@[-?.?_?\w]+',' '.join(e_mails))
            email=[]
            for i in emails:
                if '.de' or '.com' or '.org' or '.net' in str(i):
                    email.append(i)
                else:
                    continue
            #email=[i for i in emails if '.de' or '.com' or '.org' or '.net' in str(i)]
            print(email)
            place_info['e-mail']=email[0]
        except:
            place_info['e-mail']='None'
    return [value for value in place_info.values()]
  ## The following script calls the above function and saves the results in excel format.
  def get_info_as_excel(filename):
    print('Please enter your file name with its extension:')
    places=open(filename,encoding='utf-8').read()
    lst=places.split('\n')
    full_info=[]
    for i in lst:
        full_info.append(get_infos(i[1:]))
    df=pd.DataFrame(full_info,columns=['Company_name','address','phone','webpage','intagram','twitter','facebook','email'])
    print('Writing the results to excel...')
    
    return df.to_excel('places.xlsx')
  
