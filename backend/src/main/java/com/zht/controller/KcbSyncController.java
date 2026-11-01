package com.zht.controller;

import com.zht.commons.r.R;
import com.zht.scheduler.KcbSyncScheduler;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 科创板数据同步控制器
 * POST /api/kcb-sync/trigger  —— 手动触发一次同步
 * GET  /api/kcb-sync/status   —— 查询当前同步状态
 */
@RestController
@RequestMapping("/api/kcb-sync")
@CrossOrigin(origins = "*")
public class KcbSyncController {

    @Autowired
    private KcbSyncScheduler kcbSyncScheduler;

    /**
     * 手动触发数据同步（异步，立即返回）
     */
    @PostMapping("/trigger")
    public R<String> trigger() {
        String msg = kcbSyncScheduler.triggerManual();
        return R.succ(msg);
    }

    /**
     * 查询同步状态
     */
    @GetMapping("/status")
    public R<Map<String, Object>> status() {
        Map<String, Object> info = new LinkedHashMap<>();
        info.put("running",        kcbSyncScheduler.isRunning());
        info.put("lastSyncTime",   kcbSyncScheduler.getLastSyncTime());
        info.put("lastSyncResult", kcbSyncScheduler.getLastSyncResult());
        return R.succ(info);
    }
}
