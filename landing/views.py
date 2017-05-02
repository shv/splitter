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
    page = Page.objects.get(url=url)

    creative = None
    content = {}
    creative_id = request.GET.get('creative_id', request.COOKIES.get('creative_id_for_page_%s'%page.url))
    if creative_id is not None:
        creative = Creative.objects.get(pk=creative_id)

    if not creative:
        line_items = LineItem.objects.filter(page=page).order_by('priority').all()
        for line_item in line_items:
            segment = line_item.segment
            rule = segment.content
            res = eval(rule)
            if res:
                query = QueryDict(request.META['QUERY_STRING'])
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
    if creative:
        content = eval(creative.content)
        content["creative"] = creative
        content["preview"] = preview

    response = render(request, page.template, content)
    if creative and not preview:
        max_age = 365 * 24 * 60 * 60  #one year
        expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie('creative_id_for_page_%s'%page.url, creative.id, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)

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
