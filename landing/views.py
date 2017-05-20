# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json

from django.http import HttpResponse, QueryDict
from django.db.models import Q
from django.shortcuts import render
from .models import Page, Creative, CreativePart, Segment, LineItem, ABRule
from django.conf import settings

def index(request):
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
    content = {}
    line_items = LineItem.objects.order_by('priority').all()
    for line_item in line_items:
        segment = line_item.segment
        rule = segment.content
        res = eval(rule)
        if res:
            query = QueryDict(request.META['QUERY_STRING'])
            abrules = ABRule.objects.filter(line_item=line_item.id).all()
            target_abrule = abrules[0]
            target_number = target_abrule.cnt / float(target_abrule.percentage)
            for abrule in abrules:
                tmp_target_number = abrule.cnt / float(abrule.percentage)
                if tmp_target_number < target_number:
                    target_number = tmp_target_number
                    target_abrule = abrule

            target_abrule.cnt = target_abrule.cnt + 1
            target_abrule.save()
            creative = target_abrule.creative
            content = eval(creative.content)


    return render(request, 'index.html', content)

def landing(request, url):
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
    preview = request.GET.get('preview', False)
    content = {}
    page = None
    try:
        page = Page.objects.get(url=url)
        # Log: page id success loaded
    except Page.DoesNotExist:
        page = Page.objects.filter(purpose="default")
        if len(page):
            page = page[0]
            # Log: default page id success loaded
        else:
            page = Page.objects.filter()[0]
            # Log: other page id success loaded

    creative = None
    # creative_id = request.GET.get('creative_id', request.COOKIES.get('creative_id_for_page_%s'%page.url))
    # Только для прямого вызова креатива
    creative_id = request.GET.get('creative_id')
    if creative_id is not None:
        try:
            creative = Creative.objects.get(pk=creative_id)
            # Log: creative id success loaded
        except Creative.DoesNotExist:
            pass

    # Сюда сохраним отработавшую стратегию
    active_line_item = None
    if not creative:
        line_items = LineItem.objects.filter(page=page).order_by('priority').all()
        # Log: lineitems (id list) success loaded
        for line_item in line_items:
            segment = line_item.segment
            rule = segment.content
            res = eval(rule)
            if res:
                active_line_item = line_item
                query = QueryDict(request.META['QUERY_STRING'])
                # Ищем креатив для конкретной стратегии на случай если пользователь уже видел креатив (попал в ab-test)
                creative_id = request.COOKIES.get('creative_id_for_page_%s_and_li_%s'%(page.url, line_item.id))
                if creative_id is not None:
                    try:
                        creative = Creative.objects.get(pk=creative_id)
                        # Log: creative id success loaded
                    except Creative.DoesNotExist:
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
                            creative = target_abrule.creative
                    break

    # Если стратегия не отработала, то смотрим, есть ли хоть один креатив для этой страницы
    if creative is None and active_line_item is not None:
        creative_id = request.COOKIES.get('creative_id_for_page_%s'%page.url)
        if creative_id is not None:
            try:
                creative = Creative.objects.get(pk=creative_id)
                # Log: creative id success loaded
            except Creative.DoesNotExist:
                pass

    # Загружаем содержимое креатива
    if creative is not None:
        content.update(eval(creative.content))
        content["creative"] = creative

    content["preview"] = preview
    content["page"] = page
    # Пока так, потом будем менять в зависимости от лэндинга
    content["host"] = request.META['HTTP_HOST']

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

    return response


def generate(request):
    creative_parts = CreativePart.objects.all()

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
            creatives = creatives.filter(creativepart = item)
            content_list.append("{}: {}".format(json.dumps(item.name), item.content if item.executable else json.dumps(item.content)))

        content = "{%s}"%(",".join(content_list))

        if len(creatives):
            for creative in creatives:
                creative.content = content
                creative.save()
        else:
            creative = Creative.objects.create(title="test-%s"%i, content=content)
            for item in r:
                creative.creativepart_set.add(item)


    return HttpResponse(result)
