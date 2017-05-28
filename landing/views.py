# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json
import logging
# import pytelegrambotapi
import re
import time
import urllib
import urllib2
import uuid


from django.http import HttpResponse, QueryDict, Http404, HttpResponseRedirect
from django.db.models import Q
from django.shortcuts import render
from .models import Host, Page, CreativeGroup, Creative, CreativePart, Segment, LineItem, ABRule, Order
from django.conf import settings
from django.views.decorators.cache import never_cache
from jsonview.decorators import json_view

logger = logging.getLogger(__name__)
statistics_logger = logging.getLogger("statistics")


def send_to_telegramm(text):
    telegramm_url = 'https://api.telegram.org/bot{}/sendMessage'.format(settings.TELEGRAMM_TOKEN)
    values = { 'chat_id': '284295163','text': text.encode('utf-8')}
    data = urllib.urlencode(values)
    req = urllib2.Request(telegramm_url, data)
    resp = urllib2.urlopen(req)
    result = resp.read()


@never_cache
@json_view
def create_order(request):
    if request.method == 'POST':
        description = "Offer_id: {}".format(request.POST["offer_id"])
        order = Order.objects.create(phone=request.POST["phone"], description=description, status="new", session_id=request.session.session_key)

        result = {"status": "ok", "offer_id": request.POST["offer_id"], "order_id": order.id}

        send_to_telegramm("Заказ на набор {}! Телефон: {}. Номер заказа: {}".format(request.POST["offer_id"], request.POST["phone"], result["order_id"]))

        ts = time.time()
        impression_id = request.POST.get('impression_id')
        preview = request.GET.get('preview', False)
        statistics = {
            "action": "create_order",
            "sessionid": request.session.session_key,
            "timestamp": ts,
            "datetime": datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%SZ'),
            "impression_id": impression_id,
            "http_referer": request.META.get('HTTP_REFERER'),
            "preview": preview,
            "cookies": request.COOKIES,
            "query_string": request.META['QUERY_STRING'],
            "offer_id": request.POST["offer_id"],
            "phone": request.POST["phone"],
            "order_id": result["order_id"],
        }
        statistics_logger.info(json.dumps(statistics))

        return result


@never_cache
def landing(request, url):
    # send_to_telegramm("Пришел новый заказ! Смотри")

    # Логика прилипания креатива:
    #   В первый раз пользователю назначается креатив исходя из его сегмента и распределения во AB
    #   При следующем заходе, если пользователь попал в сегмент, то ищется предыдущий креатив в этом сегменте
    #   Если пользователь не попал в сегмент, то ищется последний показанный креатив
    #   Если креатив не найден, то ничего не показываем (дефолтный шаблон)
    # 
    # creative = get_object_or_404(Question, pk=question_id)

    # request.COOKIES
    # request.META
    #    HTTP_REFERER
    #    HTTP_COOKIE
    #    TERM_SESSION_ID
    #    HTTP_HOST
    #    PATH_INFO
    #    QUERY_STRING
    # request.GET.get("w")

    # Пока так прокидываем идентификатор показа
    # В урл добавляем его скриптом, чтобы не фиксировался и не индексировался
    impression_id = request.GET.get('impression_id')
    if impression_id:
        query_string = request.META['QUERY_STRING']
        query_string = query_string.replace('impression_id='+impression_id, "").replace("&&", "&")
        # Пока что предполагаем, что идентификато ссылающейся кнопки может быть только при наличии impression_id
        referer_button = request.GET.get('referer_button')
        referer_button_val = referer_button if referer_button else ''
        query_string = query_string.replace('referer_button='+referer_button_val, "").replace("&&", "&")
        query_string = re.sub(r"^&$", "", query_string)
        new_url = "{}".format(request.path)
        if query_string:
            new_url = new_url + "?" + query_string
        response = HttpResponseRedirect(new_url) # replace redirect with HttpResponse or render
        response.set_cookie('impression_id', impression_id, max_age=30)
        response.set_cookie('referer_button', referer_button_val, max_age=10 if referer_button else 0)
        return response

    # Уникальный идентификатор показа. Записывается только в лог и прокидывается во все события дальше
    impression_id = request.COOKIES.get('impression_id', str(uuid.uuid4()))
    # Имя ссылающейся кнопки для разделения статистики кликов. Сначала из кук, потом из строки запроса
    referer_button = request.COOKIES.get('referer_button', request.GET.get('referer_button'))


    # У каждого пользователя должна быть сесссия. По ней буем дальше трэкать стату
    if not request.session.session_key:
        request.session.create()


    ts = time.time()
    # Сюда складывается вся инфа для статистики
    content = {}
    statistics = {
        "action": "landing",
        "sessionid": request.session.session_key,
        "timestamp": ts,
        "datetime": datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%SZ'),
        "impression_id": impression_id,
        "user_agent": request.META.get('HTTP_USER_AGENT'),
        "remote_addr": request.META.get('REMOTE_ADDR'),
        "http_x_real_ip": request.META.get('HTTP_X_REAL_IP'),
        "http_x_forwarded_for": request.META.get('HTTP_X_FORWARDED_FOR'),
        "http_referer": request.META.get('HTTP_REFERER'),
        "referer_button": referer_button,
    }
    logger.debug("---META: {}".format(request.META))

    try:
        host = Host.objects.get(domain=request.META['HTTP_HOST'])
        statistics["host"] = host.id
    except Host.DoesNotExist:
        raise Http404("Domain does not exist")

    preview = request.GET.get('preview', False)
    statistics["preview"] = preview
    page = None
    try:
        page = Page.objects.get(url=url, host=host)
        statistics["page"] = page.id
        # Log: page id success loaded
    except Page.DoesNotExist:
        raise Http404("Poll does not exist")

    creative = None
    # creative_id = request.GET.get('creative_id', request.COOKIES.get('creative_id_for_page_%s'%page.url))
    # Только для прямого вызова креатива
    creative_id = request.GET.get('creative_id')
    if creative_id is not None:
        try:
            creative = Creative.objects.get(pk=creative_id)
            statistics["creative_from_request"] = creative.id
            # Log: creative id success loaded
        except Creative.DoesNotExist:
            pass

    statistics["cookies"] = request.COOKIES
    query = QueryDict(request.META['QUERY_STRING'])
    statistics["query_string"] = request.META['QUERY_STRING']

    # Сюда сохраним отработавшую стратегию
    active_line_item = None
    if not creative:
        logger.debug("No creative")
        line_items = LineItem.objects.filter(page=page).order_by('priority').all()
        # Log: lineitems (id list) success loaded
        for line_item in line_items:
            logger.debug("Line item: {}".format(line_item.title))
            segment = line_item.segment
            rule = segment.content
            logger.error("---Rule: {}".format(rule))
            res = eval(rule)
            logger.error("---Res: {}".format(res))
            if res:
                active_line_item = line_item
                statistics["line_item"] = line_item.id
                # Ищем креатив для конкретной стратегии на случай если пользователь уже видел креатив (попал в ab-test)
                creative_id = request.COOKIES.get('creative_id_for_page_%s_and_li_%s'%(page.url, line_item.id))
                if creative_id is not None:
                    try:
                        creative = Creative.objects.get(pk=creative_id)
                        statistics["creative_from_cookies_line_item"] = creative.id
                    except Creative.DoesNotExist:
                        pass

                if not creative:
                    abrules = ABRule.objects.filter(line_item=line_item.id).all()
                    if len(abrules):
                        target_abrule = abrules[0]
                        target_number = target_abrule.cnt / float(target_abrule.percentage)
                        for abrule in abrules:
                            tmp_target_number = abrule.cnt / float(abrule.percentage)
                            if tmp_target_number < target_number:
                                target_number = tmp_target_number
                                target_abrule = abrule

                        target_abrule.cnt = target_abrule.cnt + 1
                        target_abrule.save()
                        statistics["abrule"] = abrule.id
                        creative = target_abrule.creative
                        statistics["creative_generated"] = creative.id

                    break

    # Если стратегия не отработала, то смотрим, есть ли хоть один креатив для этой страницы
    if creative is None and active_line_item is not None:
        creative_id = request.COOKIES.get('creative_id_for_page_%s'%page.url)
        if creative_id is not None:
            try:
                creative = Creative.objects.get(pk=creative_id)
                statistics["creative_from_cookies_page"] = creative.id
            except Creative.DoesNotExist:
                pass

    orders = Order.objects.filter(status="new", session_id=request.session.session_key).all()
    if len(orders):
        content["has_orders"] = True

    # Загружаем содержимое креатива
    if creative is not None:
        content["smart"] = eval(creative.content)
        content["creative"] = creative
        statistics["creative"] = creative.id

    content["preview"] = preview
    content["page"] = page
    # Пока так, потом будем менять в зависимости от лэндинга
    content["host"] = request.META['HTTP_HOST']
    content["statistics"] =  statistics

    # Подготавливаем шаблон
    response = render(request, page.template, content)

    # Ставим нужные куки
    if creative and not preview:
        max_age = 365 * 24 * 60 * 60  #one year
        expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
        # Ставим куку для страницы, на случай если стратегия не отработала
        response.set_cookie('creative_id_for_page_%s'%page.url, creative.id, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)
        # Ставим куку для конкретной стратегии
        if active_line_item:
            response.set_cookie('creative_id_for_page_%s_and_li_%s'%(page.url, active_line_item.id), creative.id, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)

    # log
    # creative
    statistics_logger.info(json.dumps(statistics))

    return response


@never_cache
def generate(request):
    creative_groups = CreativeGroup.objects.all()
    for creative_group in creative_groups:
        creative_parts = CreativePart.objects.filter(creativegroup = creative_group).all()

        # Это ебанутый способ (но рабочий) сгенерировать все комбинации креативов
        s_dict = {}
        s_index = []
        for s in creative_parts:
            if s.name not in s_dict:
                s_dict[s.name] = [s]
                s_index.append(s.name)
            else:
                s_dict[s.name].append(s)

        s_array = []
        total_combitations = 1
        for s_i in s_index:
            s_array.append(s_dict[s_i])
            total_combitations = total_combitations * len(s_dict[s_i])

        result = []
        for i in range(total_combitations):
            result.append([])

        N = total_combitations
        for s_line in s_array:
            cnt = len(s_line)
            N = N / cnt # Количество повторений каждого элемента
            M = total_combitations / N / cnt # На сколько нужно домножить до заполнения столбца
            for i in range(cnt):
                    for n in range(N):
                        for m in range(M):
                            k = i * N + n + total_combitations / M * m
                            result[k].append(s_line[i])

        #Creative.objects.filter().delete()
        for i, r in enumerate(result):
            content_list = []
            creatives = Creative.objects
            for item in r:
                creatives = creatives.filter(creativepart = item, creativegroup = creative_group)
                content_list.append("{}: {}".format(json.dumps(item.name), item.content if item.executable else json.dumps(item.content)))

            content = "{%s}"%(",".join(content_list))

            if len(creatives):
                for creative in creatives:
                    creative.content = content
                    creative.save()
            else:
                creative = Creative.objects.create(title="%s-%s"%(creative_group.title, i), content=content, creativegroup = creative_group)
                for item in r:
                    creative.creativepart_set.add(item)


    return HttpResponse(result)
