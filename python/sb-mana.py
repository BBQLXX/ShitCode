
    def init_from_history_data(self):
        # -获取基础信息
        self.basic_info = tyc_interface(self.project_id, self.company, "open/ic/baseinfoV3/2.0")
        # 招投标信息 投标、中标
        # self.basic_info['bids'] = tyc_interface(self.project_id, self.company, "open/m/bids/2.0")
        # IPO进展
        self.basic_info['ipo'] = tyc_interface(self.project_id, self.company, "open/stock/list")

        # 法人在外任职  TODO 在外任职企业 所属行业数量
        self.people_info['judicial_person_role'] = tyc_interface(self.project_id,
                                                                 f'humanName={self.basic_info["legalPersonName"]}',
                                                                 "v4/open/roles",
                                                                 type='multiBase')
        # -获取股东信息
        self.shareholders_list = tyc_interface(self.project_id, self.company, "open/ic/holder/2.0")
        # 股权变更
        self.holders_change = tyc_interface(self.project_id, self.company, "open/ic/holderChange/2.0")

        # -获取历史股东信息
        # self.history_holders_list = tyc_interface(self.project_id, self.company, "open/hi/holder/2.0")
        # -获取变更信息
        self.change_info_list = tyc_interface(self.project_id, self.company, "open/ic/changeinfo/2.0")
        # 失信
        self.law_data['dis_honest'] = tyc_interface(self.project_id, self.company, "open/hi/dishonest/2.0")
        # 限高
        self.law_data['consumptionRestriction'] = tyc_interface(self.project_id, self.company,
                                                                "open/jr/consumptionRestriction/2.0")
        # 历史限高
        self.law_data['consumptionRestrictionHistory'] = tyc_interface(self.project_id, self.company,
                                                                       "open/hi/human/consumptionRestriction")
        # 终本
        self.law_data['endCase'] = tyc_interface(self.project_id, self.company, "open/jr/endCase/2.0")
        # 被执行
        self.law_data['executed_people'] = tyc_interface(self.project_id, self.company, "open/jr/zhixinginfo/2.0")
        # 历史被执行
        self.law_data['executedMsg'] = tyc_interface(self.project_id, self.company, "open/hi/zhixing/2.0")
        # 司法拍卖
        self.law_data['judicialSale'] = tyc_interface(self.project_id, self.company, 'open/mr/judicialSale/3.0')
        # 司法协助
        self.law_data['judicialAssis'] = tyc_interface(self.project_id, self.company, 'v4/open/judicial')
        # 税务评级
        self.law_data['taxCredit'] = tyc_interface(self.project_id, self.company, 'open/m/taxCredit/2.0')
        # 行政处罚
        self.law_data['administrativePenalty'] = tyc_interface(self.project_id, self.company,
                                                               'open/mr/punishmentInfo/3.0')
        # 专利
        self.product_data['search'] = tyc_interface(self.project_id, self.company, "open/ipr/patents/search/2.0")
        # 软著
        self.product_data['soft'] = tyc_interface(self.project_id, self.company, "open/ipr/copyReg/2.0")
        # 融资历史
        self.funding_history_list = tyc_interface(self.project_id, self.company, "open/cd/findHistoryRongzi/2.0")

        if self.basic_info and self.basic_info.get('taxNumber'):
            self.social_security_data = get_interface_data(self.project_id, '社保',
                                                           DataSources.SOCIAL_SECURITY_URL.value,
                                                           {'creditNo': self.basic_info['taxNumber']})
        # 获取大司法信息
        self.law_data['data'] = get_interface_data(self.project_id, '大司法', DataSources.LAW_URL.value,
                                                   {'orgname': self.company})
        # 获取其他基础信息
        self.other_basic_data = get_interface_data(self.project_id, '其他基础信息', DataSources.OTHER_BASIC_INFO.value,
                                                   {'companyName': self.company})
        # 获取common信息
        self.common_data = get_interface_data(self.project_id, 'common信息', DataSources.FIN_REPORT_URL.value,
                                              {'companyName': self.company})

        # # -获取历史股东信息
        # history_holders_list = tyc_interface(upload_time_str, company, "open/hi/holder/2.0")
        # # -获取变更信息
        # change_info_list = tyc_interface(upload_time_str, company, "open/ic/changeinfo/2.0")
        # log(str(change_info_list))

        # # 获取社保信息 入参企业社会信用代码
        social_security_data = ''
        # if basic_info and basic_info.get('taxNumber'):
        #     social_security_data = get_interface_data(upload_time_str, '社保', DataSources.SOCIAL_SECURITY_URL.value,
        #                                               {'creditNo': basic_info['taxNumber']})
        # # 获取大司法信息
        # law_data = get_interface_data(upload_time_str, '大司法', DataSources.LAW_URL.value,
        #                               {'orgname': company})
        # # 获取其他基础信息
        # other_basic_data = get_interface_data(upload_time_str, '其他基础信息', DataSources.OTHER_BASIC_INFO.value,
        #                                       {'companyName': company})
        # # 获取common信息
        # common_data = get_interface_data(upload_time_str, 'common信息', DataSources.FIN_REPORT_URL.value,
        #                                  {'companyName': company})
        #
        # return ''