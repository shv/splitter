# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json
import logging

from django.http import HttpResponse, QueryDict, Http404
from django.db.models import Q
from django.shortcuts import render
from .models import Host, Page, CreativeGroup, Creative, CreativePart, Segment, LineItem, ABRule
from django.conf import settings

logger = logging.getLogger(__name__)
statistics_logger = logging.getLogger("statistics")

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

    # Сюда складывается вся инфа для статистики
    statistics = {}

    try:
        host = Host.objects.get(domain=request.META['HTTP_HOST'])
        statistics["host"] = host.id
    except Host.DoesNotExist:
        raise Http404("Domain does not exist")

    preview = request.GET.get('preview', False)
    statistics["preview"] = preview
    content = {}
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

    # Загружаем содержимое креатива
    if creative is not None:
        content.update(eval(creative.content))
        content["creative"] = creative
        statistics["creative"] = creative.id

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

    # log
    # creative
    statistics_logger.info(statistics)

    return response


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
