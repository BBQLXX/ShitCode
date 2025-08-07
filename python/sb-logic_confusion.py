def process_law_data(project_id, company, law_data, common_data):
    if law_data == '' or law_data is None:
        log(f'大司法信息law_data为空:解析失败')
        return ''
    log(f'开始解析{company} 的law_data')
    law_info_list = []
    law_info = law_data['data']
    law_object = ReviewLawInfoSheet()
    law_object.project_id = project_id
    law_object.company = company
    if isinstance(law_info, list) and len(law_info) == 1:
        law_object.data = str(law_info[0])
    else:
        law_object.data = str(law_info)
    law_object.dis_honest = str(law_data['dis_honest'])
    law_object.consumptionRestriction = str(law_data['consumptionRestriction'])
    if law_data['endCase']:
        law_object.endCase = str(law_data['endCase'].get('items', []))
    # log(str(law_data))
    law_object.judicialSale = str(law_data['judicialSale'])
    law_object.judicialAssis = str(law_data['judicialAssis'])
    law_object.executed_people = str(law_data['executed_people'])
    law_object.executedMsg = str(law_data['executedMsg'])
    law_object.taxCredit = str(law_data['taxCredit'])
    law_object.consumptionRestrictionHistory = str(law_data['consumptionRestrictionHistory'])
    log(f"行政处罚数据为：{law_data['administrativePenalty']}")
    if law_data['administrativePenalty']:
        law_object.administrativePenalty = str(law_data['administrativePenalty'])
    law_info_list.append(law_object)
    if common_data is not None and (common_data.get('source') == 'wz' or common_data.get('source') == 'bw'):
        # 前5大客户的law_info
        customer_year_list = common_data['salesTopCorpByAmountList']
        # 最近一年
        year_list = []
        for y in customer_year_list:
            year_list.append(y['year'])
        year_list = [item for item in year_list if item != '']
        if len(year_list) > 0:
            max_year = max(int(num) for num in year_list)
            for y in customer_year_list:
                if y['year'] == str(max_year):
                    for c in y['salesTopCorpByAmountCorpList'][:5]:
                        c_law_object = ReviewLawInfoSheet()
                        c_law_object.company = c['customer']
                        c_law_object.project_id = project_id
                        c_law_object.dis_honest = str(tyc_interface(project_id, c['customer'], "open/hi/dishonest/2.0"))
                        c_law_object.consumptionRestriction = str(tyc_interface(project_id, c['customer'],
                                                                                "open/jr/consumptionRestriction/2.0"))
                        c_law_object.executed_people = str(
                            tyc_interface(project_id, c['customer'], "open/jr/zhixinginfo/2.0"))
                        c_law_object.bankruptcy = str(
                            tyc_interface(project_id, c['customer'], "open/jr/bankruptcy/2.0"))
                        law_info_list.append(c_law_object)

        # 前5大供应商的law
        supplies_year_list = common_data['purchasesTopCorpByAmountList']
        year_list = []
        for a in supplies_year_list:
            year_list.append(a['year'])
        year_list = [item for item in year_list if item != '']
        if len(year_list) > 0:
            max_year = max(int(num) for num in year_list)
            for y in supplies_year_list:
                if y['year'] == str(max_year):
                    for s in y['purchasesTopCorpByAmountCorpList'][:5]:
                        log(f'{s["customer"]}公司{y["year"]}法律信息')
                        s_law_object = ReviewLawInfoSheet()
                        s_law_object.company = s['customer']
                        s_law_object.project_id = project_id
                        s_law_object.dis_honest = str(tyc_interface(project_id, s['customer'], "open/hi/dishonest/2.0"))
                        s_law_object.consumptionRestriction = str(tyc_interface(project_id, s['customer'],
                                                                                "open/jr/consumptionRestriction/2.0"))
                        s_law_object.executed_people = str(
                            tyc_interface(project_id, s['customer'], "open/jr/zhixinginfo/2.0"))
                        s_law_object.bankruptcy = str(
                            tyc_interface(project_id, c['customer'], "open/jr/bankruptcy/2.0"))
                        law_info_list.append(s_law_object)

    with app.app.app_context():
        db.create_all()
        ReviewLawInfoSheet.query.filter_by(company=company).update({"is_deleted": 1})
        db.session.bulk_save_objects(law_info_list)
        db.session.commit()
    return ''


def process_tyc_shareholders_list(upload_time_str, shareholders_list, history_holders_list, company):
    if len(shareholders_list) == 0 or shareholders_list is None:
        log(f'shareholders_list信息为空，解析失败')
        return ''
    add_holders_list = list(shareholders_list)
    # -获取股权穿透信息
    for s in shareholders_list:
        holder_name = s.get('name')
        if '公司' in holder_name or '有限合伙' in holder_name:
            log(f'获取{holder_name}股权穿透信息')
            h = tyc_interface(upload_time_str, holder_name, "open/ic/holder/2.0")
            if h is not None:
                add_holders_list += h

    log('解析股东信息shareholders_list:开始')
    data_obj_list = []
    for s in add_holders_list:
        del s['id']
        s.update(s['capital'][0] if s['capital'] else [])
        data_obj = ReviewHolderInfoSheet(**s)
        data_obj.company = company
        data_obj.project_id = upload_time_str
        data_obj_list.append(data_obj)
    with app.app.app_context():
        # db.create_all()
        # log(shareholders_list[0]['keyword'])
        # shareholders_list[0]['keyword']
        ReviewHolderInfoSheet.query.filter_by(company=company).update(
            {"is_deleted": 1})
        db.session.bulk_save_objects(data_obj_list)
        db.session.commit()
    log('解析股东信息shareholders_list:完成')

    # log('解析历史股东信息history_holders_list:开始')
    # history_holders_obj_list = []
    # if history_holders_list is None:
    #     log('历史股东信息为None')
    # else:
    #     for i in history_holders_list['items']:
    #         del i['id']
    #         i.update(i['capital'][0] if i['capital'] else [])
    #         log(str(i))
    #         del i['capital']
    #         data_obj = ReviewHolderHistoryInfoSheet(**i)
    #         data_obj.company = history_holders_list['keyword']
    #         data_obj.project_id = upload_time_str
    #         history_holders_obj_list.append(data_obj)
    #         # TODO 修改时间戳
    #     with app.app.app_context():
    #         db.create_all()
    #         ReviewHolderHistoryInfoSheet.query.filter_by(company=history_holders_list['keyword']).update(
    #             {"is_deleted": 1})
    #         db.session.bulk_save_objects(history_holders_obj_list)
    #         db.session.commit()
    #     log('解析历史股东信息history_holders_list:完成')

    return ''


def process_tyc_change_info_list(upload_time_str, change_info_list, holders_change, company):
    if change_info_list is None or len(change_info_list) == 0:
        log(f'change_info_list信息为空，解析失败')
        return ''
    log('开始解析变更信息change_info_list')
    data_obj_list = []
    for c in change_info_list:
        del c['_id']
        data_obj = ReviewChangeInfoSheet(**c)
        data_obj.company = company
        data_obj.project_id = upload_time_str
        data_obj_list.append(data_obj)

    with app.app.app_context():
        # company = change_info_list[0]['keyword']
        ReviewChangeInfoSheet.query.filter_by(company=company).update({"is_deleted": 1})
        db.session.bulk_save_objects(data_obj_list)
        db.session.commit()
    log('变更信息解析完成')
    return ''



def process_people_info(project_id, other_basic_data, people_info):
    if other_basic_data == '' or other_basic_data is None:
        log(f'other_basic_data信息为空，解析失败')
        return ''
    log('开始解析other_basic_data信息')
    log(f'other_basic_data:{other_basic_data}')
    people_info_object = ReviewPeopleInfoSheet()
    people_info_object.company = other_basic_data['companyName']
    people_info_object.project_id = project_id
    people_info_object.home_situation = str({"maritalStatus": other_basic_data["isMarried"],
                                             "childrenCount": other_basic_data["childrenStatus"]})
    people_info_object.judicial_person_ID = other_basic_data['farenCardId']
    people_info_object.judicial_person_role = str(people_info['judicial_person_role'])
    with app.app.app_context():
        db.create_all()
        ReviewPeopleInfoSheet.query.filter_by(company=other_basic_data['companyName']).update({"is_deleted": 1})
        db.session.add(people_info_object)
        db.session.commit()
    log('people_info信息入库成功')
    return ''


def process_tyc_basic_info(project_id, basic_info, social_security_data, other_basic_data, common_data,
                           funding_history_list, company):
    if basic_info == '' or basic_info is None:
        log(f'basic_info信息为空，解析失败')
        return ''
    log('开始解析basic_info信息')
    log(f'basic_info:{basic_info}')
    del basic_info['id']
    basic_info['staffList'] = str(basic_info.get('staffList'))
    basic_info['bids'] = str(basic_info.get('bids'))
    ipo = basic_info.get('ipo')
    basic_info['ipo'] = str(ipo.get('items', []) if ipo is not None else [])
    basic_info_object = ReviewBasicInfoSheet(**basic_info)
    basic_info_object.company = company
    basic_info_object.project_id = project_id
    timestamp_ms = basic_info['estiblishTime']
    dt_object = datetime.fromtimestamp(timestamp_ms / 1000.0)
    basic_info_object.estiblishTime = dt_object.strftime("%Y-%m-%d")

    basic_info_object.actualLocation = str(other_basic_data['sjjydz'])
    basic_info_object.socialSecurityRecords = str(social_security_data)
    basic_info_object.other = str(other_basic_data)
    if common_data is None or common_data.get('fumianhangye'):
        basic_info_object.fumianhangye = 'None'
    if funding_history_list:
        basic_info_object.funding_history = str(funding_history_list)
    else:
        default = {
            "items": []
        }
        basic_info_object.funding_history = str(default)
    # basic_info_object.legalPersonName = basic_info['legalPersonName']
    # basic_info_object.staffList = str(basic_info['staffList'])
    # basic_info_object.regLocation = basic_info['regLocation']
    # basic_info_object.regCapital = basic_info['regCapital']
    # basic_info_object.actualCapital = basic_info['actualCapital']
    # basic_info_object.socialStaffNum = basic_info['socialStaffNum']
    # basic_info_object.taxNumber = basic_info['taxNumber']
    # basic_info_object.businessScope = basic_info['businessScope']
    # basic_info_object.industry = basic_info['industry']
    # basic_info_object.tags = basic_info['tags']
    # basic_info_object.alias = basic_info['alias']

    with app.app.app_context():
        db.create_all()
        ReviewBasicInfoSheet.query.filter_by(company=basic_info_object.company).update({"is_deleted": 1})
        db.session.add(basic_info_object)
        db.session.commit()
    log('basic_info信息入库成功')


def tyc_interface(project_id, tyc_input, url, type='base'):
    # 计算一个月前的时间
    one_month_ago = datetime.now() - timedelta(days=30)
    files = InterfaceData.query.filter(
        and_(
            InterfaceData.input == tyc_input,
            InterfaceData.tyc_url == url,
            InterfaceData.is_deleted == 0,
            InterfaceData.create_time >= one_month_ago
        )
    ).order_by(desc(InterfaceData.create_time)).first()
    if files is not None:
        files_schema = OutInterfaceDataSchema()
        output = files_schema.dumps(files)  # str
        output_json = json.loads(output)  # dict
        response = json.loads(output_json.get('response'))
        # log(f'已查询到:{tyc_input}的天眼查{url}数据：' + str(response.get('data'))[:200])
        return response.get('data')

    # 查反担保人的股东信息 和上市公司
    try:
        log(f'调用天眼查{url}接口,入参为:{tyc_input}')
        data = {
            'companyName': tyc_input,
            'url': url
        }
        if type == 'multiBase':
            data = {
                'params': tyc_input,
                'url': url
            }
    except IOError:
        log(f"Error: {url}接口调用失败")
        return ''
    else:
        # log(f'{url}接口出参为：' + res.text)
        result_data = {
            'source_type': '天眼查',
            'input': tyc_input,
            'tyc_url': url,
            'response': res.text
        }
        data_obj_list = []
        data_obj = InterfaceData(**result_data)
        data_obj.project_id = project_id
        data_obj_list.append(data_obj)
        with app.app.app_context():
            db.create_all()
            InterfaceData.query.filter_by(input=tyc_input, tyc_url=url).update({"is_deleted": 1})
            db.session.bulk_save_objects(data_obj_list)
            db.session.commit()

        response_dict = json.loads(res.text)
        return response_dict.get('data')
    # log(response_dict['code'])

    # if res_text['code'] == 200:
    #     holder_list = []
    #     for d in res_text['data']:
    #         holder_list.append(d['name'])
    #     log('当前公司股东列表为：' + str(holder_list))
    # else:
    #     log('当前公司 调用天眼查open/ic/holder/2.0接口无数据')
