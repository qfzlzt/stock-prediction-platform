package com.zht.controller;

import com.zht.commons.r.R;
import com.zht.entity.KcbCloseDaily;
import com.zht.service.KcbCloseDailyService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/kcb-close")
@CrossOrigin(origins = "*")
public class KcbCloseDailyController {

    @Autowired
    private KcbCloseDailyService kcbCloseDailyService;

    /**
     * 按日期范围查询三种科创板收盘价指标
     * GET /api/kcb-close/list?startDate=2024-01-01&endDate=2024-12-31
     */
    @GetMapping("/list")
    public R<List<KcbCloseDaily>> list(
            @RequestParam(required = false) String startDate,
            @RequestParam(required = false) String endDate) {
        List<KcbCloseDaily> data = kcbCloseDailyService.queryByDateRange(startDate, endDate);
        return R.succ(data);
    }
}
