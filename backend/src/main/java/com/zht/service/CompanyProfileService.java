package com.zht.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.service.IService;
import com.zht.entity.CompanyProfile;
import com.zht.entity.dto.CompanyQuery;

import java.util.List;

/**
 * 公司概况表(CompanyProfile)表服务接口
 *
 * @author makejava
 * @since 2026-03-08 04:30:47
 */
public interface CompanyProfileService extends IService<CompanyProfile> {


    IPage<CompanyProfile> queryPage(CompanyQuery query);

    List<CompanyProfile> getSimpleList();
}

