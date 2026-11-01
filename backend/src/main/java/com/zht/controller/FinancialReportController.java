// FinancialReportController.java
package com.zht.controller;

import com.zht.commons.r.R;
import com.zht.entity.FinancialReport;
import com.zht.entity.FinancialReportVO;
import com.zht.entity.dto.FinancialQuery;
import com.zht.service.FinancialReportService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/financial-reports")
@CrossOrigin(origins = "*")
@Slf4j
public class FinancialReportController {
    
    @Autowired
    private FinancialReportService financialReportService;
    
    @GetMapping("/list")
    public R<List<FinancialReportVO>> queryList(FinancialQuery query) {
        List<FinancialReportVO> list = financialReportService.queryList(query);
        return R.succ(list);
    }
    
    @GetMapping("/reporttype")
    public R<List<FinancialReport>> getBystockCode(@RequestParam String stockCode) {
        List<FinancialReport> report = financialReportService.getByStockCode(stockCode);
        log.info("aaaaaaaaaaaaaaaaaaaaa{}",report);
        return R.succ(report);
    }
    
    @PostMapping
    public R<?> add(@RequestBody FinancialReport report) {
        financialReportService.save(report);
        return R.succ(null);
    }
    
    @PutMapping("/{stockCode}")
    public R<?> update(@PathVariable String stockCode, @RequestBody FinancialReport report) {
        report.setStockcode(stockCode);
        financialReportService.updateById(report);
        return R.succ(null);
    }
    
    @DeleteMapping("/{stockCode}")
    public R<?> delete(@PathVariable String stockCode) {
        financialReportService.removeById(stockCode);
        return R.succ(null);
    }
    
    @GetMapping("/export")
    public void export(FinancialQuery query) {
        // 导出Excel逻辑
    }
}