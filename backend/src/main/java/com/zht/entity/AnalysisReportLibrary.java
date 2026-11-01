package com.zht.entity;

import java.util.Date;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.extension.activerecord.Model;
import java.io.Serializable;

/**
 * 分析报告数据库表(AnalysisReportLibrary)表实体类
 *
 * @author makejava
 * @since 2026-03-08 04:46:17
 */
@SuppressWarnings("serial")
public class AnalysisReportLibrary extends Model<AnalysisReportLibrary> {
    //报告ID
    @TableId(type = IdType.INPUT)
    private String reportid;
    //A股代码
    private String stockcode;
    //报告标题
    private String reporttitle;
    //报告类型
    private String reporttype;
    //报告摘要
    private String reportabstract;
    //报告正文
    private String reportcontent;
    //报告作者
    private String reportauthor;
    //报告生成时间
    private Date reportgeneratetime;
    //报告状态
    private String reportstatus;
    //创建时间
    private Date createdat;
    //更新时间
    private Date updatedat;


    public String getReportid() {
        return reportid;
    }

    public void setReportid(String reportid) {
        this.reportid = reportid;
    }

    public String getStockcode() {
        return stockcode;
    }

    public void setStockcode(String stockcode) {
        this.stockcode = stockcode;
    }

    public String getReporttitle() {
        return reporttitle;
    }

    public void setReporttitle(String reporttitle) {
        this.reporttitle = reporttitle;
    }

    public String getReporttype() {
        return reporttype;
    }

    public void setReporttype(String reporttype) {
        this.reporttype = reporttype;
    }

    public String getReportabstract() {
        return reportabstract;
    }

    public void setReportabstract(String reportabstract) {
        this.reportabstract = reportabstract;
    }

    public String getReportcontent() {
        return reportcontent;
    }

    public void setReportcontent(String reportcontent) {
        this.reportcontent = reportcontent;
    }

    public String getReportauthor() {
        return reportauthor;
    }

    public void setReportauthor(String reportauthor) {
        this.reportauthor = reportauthor;
    }

    public Date getReportgeneratetime() {
        return reportgeneratetime;
    }

    public void setReportgeneratetime(Date reportgeneratetime) {
        this.reportgeneratetime = reportgeneratetime;
    }

    public String getReportstatus() {
        return reportstatus;
    }

    public void setReportstatus(String reportstatus) {
        this.reportstatus = reportstatus;
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
        return this.reportid;
    }
    }

