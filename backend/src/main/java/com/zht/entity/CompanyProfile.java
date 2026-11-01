package com.zht.entity;

import java.util.Date;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.extension.activerecord.Model;
import java.io.Serializable;

/**
 * 公司概况表(CompanyProfile)表实体类
 *
 * @author makejava
 * @since 2026-03-08 04:46:17
 */
@SuppressWarnings("serial")
public class CompanyProfile extends Model<CompanyProfile> {
    //主键ID
    @TableId(type = IdType.AUTO)
    private Long id;
    //证券代码
    private String stockcode;
    //证券简称
    private String stockname;
    //股票英文简称
    private String englishname;
    //上市版
    private String markettype;
    //股票类别
    private String stockcategory;
    //上市日期
    private Date listingdate;
    //交易状态(L-正常交易,S-停牌,D-退市整理期,T-已退市)
    private Object status;
    //所属行业名称
    private String industrylevel;
    //法定代表人
    private String legalrepresentative;
    //注册资本(元)
    private Double registeredcapital;
    //成立日期
    private Date registrationtime;
    //省份
    private String registrationprovince;
    //员工总数
    private Integer employeecount;
    //公司独立董事(历任)
    private String independentdirectors;
    //公司简介
    private String companyintro;
    //经营范围
    private String businessscope;
    //创建时间
    private Date createdat;
    //更新时间
    private Date updatedat;


    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getStockcode() {
        return stockcode;
    }

    public void setStockcode(String stockcode) {
        this.stockcode = stockcode;
    }

    public String getStockname() {
        return stockname;
    }

    public void setStockname(String stockname) {
        this.stockname = stockname;
    }

    public String getEnglishname() {
        return englishname;
    }

    public void setEnglishname(String englishname) {
        this.englishname = englishname;
    }

    public String getMarkettype() {
        return markettype;
    }

    public void setMarkettype(String markettype) {
        this.markettype = markettype;
    }

    public String getStockcategory() {
        return stockcategory;
    }

    public void setStockcategory(String stockcategory) {
        this.stockcategory = stockcategory;
    }

    public Date getListingdate() {
        return listingdate;
    }

    public void setListingdate(Date listingdate) {
        this.listingdate = listingdate;
    }

    public Object getStatus() {
        return status;
    }

    public void setStatus(Object status) {
        this.status = status;
    }

    public String getIndustrylevel() {
        return industrylevel;
    }

    public void setIndustrylevel(String industrylevel) {
        this.industrylevel = industrylevel;
    }

    public String getLegalrepresentative() {
        return legalrepresentative;
    }

    public void setLegalrepresentative(String legalrepresentative) {
        this.legalrepresentative = legalrepresentative;
    }

    public Double getRegisteredcapital() {
        return registeredcapital;
    }

    public void setRegisteredcapital(Double registeredcapital) {
        this.registeredcapital = registeredcapital;
    }

    public Date getRegistrationtime() {
        return registrationtime;
    }

    public void setRegistrationtime(Date registrationtime) {
        this.registrationtime = registrationtime;
    }

    public String getRegistrationprovince() {
        return registrationprovince;
    }

    public void setRegistrationprovince(String registrationprovince) {
        this.registrationprovince = registrationprovince;
    }

    public Integer getEmployeecount() {
        return employeecount;
    }

    public void setEmployeecount(Integer employeecount) {
        this.employeecount = employeecount;
    }

    public String getIndependentdirectors() {
        return independentdirectors;
    }

    public void setIndependentdirectors(String independentdirectors) {
        this.independentdirectors = independentdirectors;
    }

    public String getCompanyintro() {
        return companyintro;
    }

    public void setCompanyintro(String companyintro) {
        this.companyintro = companyintro;
    }

    public String getBusinessscope() {
        return businessscope;
    }

    public void setBusinessscope(String businessscope) {
        this.businessscope = businessscope;
    }

    public Date getCreatedat() {
        return createdat;
    }

    public void setCreatedat(Date createdat) {
        this.createdat = createdat;
    }

    public Date getUpdatedat() {
        return updatedat;
    }

    public void setUpdatedat(Date updatedat) {
        this.updatedat = updatedat;
    }

    /**
     * 获取主键值
     *
     * @return 主键值
     */
    @Override
    public Serializable pkVal() {
        return this.id;
    }
    }

