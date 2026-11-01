 // AnalysisReportLibraryController.java
package com.zht.controller;


import com.zht.commons.r.R;
import com.zht.entity.AnalysisReportLibrary;
import com.zht.entity.dto.AnalysisQuery;
import com.zht.service.AnalysisReportLibraryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/analysis-reports")
@CrossOrigin(origins = "*")
public class AnalysisReportLibraryController {
    
    @Autowired
    private AnalysisReportLibraryService analysisReportLibraryService;
    
    @GetMapping("/list")
    public R<List<AnalysisReportLibrary>> queryList(AnalysisQuery query) {
        List<AnalysisReportLibrary> list = analysisReportLibraryService.queryList(query);
        return R.succ(list);
    }
    
    @GetMapping("/{reportId}")
    public R<AnalysisReportLibrary> getById(@PathVariable String reportId) {
        AnalysisReportLibrary report = analysisReportLibraryService.getById(reportId);
        return R.succ(report);
    }
    
    @PostMapping
    public R<?> add(@RequestBody AnalysisReportLibrary report) {
        analysisReportLibraryService.save(report);
        return R.succ(null);
    }
    
    @PutMapping("/{reportId}")
    public R<?> update(@PathVariable String reportId, @RequestBody AnalysisReportLibrary report) {
        report.setReportid(reportId);
        analysisReportLibraryService.updateById(report);
        return R.succ(null);
    }
    
    @DeleteMapping("/{reportId}")
    public R<?> delete(@PathVariable String reportId) {
        analysisReportLibraryService.removeById(reportId);
        return R.succ(null);
    }
    
    @GetMapping("/download/{reportId}")
    public void download(@PathVariable String reportId) {
        // 下载报告逻辑
    }
    
    @GetMapping("/export")
    public void export(AnalysisQuery query) {
        // 导出Excel逻辑
    }
}