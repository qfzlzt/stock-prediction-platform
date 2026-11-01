package com.zht.scheduler;

import com.zht.service.KcbWindSyncService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;

@Component
public class KcbSyncScheduler {

    private static final Logger log = LoggerFactory.getLogger(KcbSyncScheduler.class);

    private final KcbWindSyncService kcbWindSyncService;
    private final AtomicBoolean running = new AtomicBoolean(false);
    private final AtomicReference<String> lastSyncTime = new AtomicReference<>("从未运行");
    private final AtomicReference<String> lastSyncResult = new AtomicReference<>("-");

    public KcbSyncScheduler(KcbWindSyncService kcbWindSyncService) {
        this.kcbWindSyncService = kcbWindSyncService;
    }

    @Scheduled(cron = "0 0 16 * * MON-FRI")
    public void scheduledSync() {
        log.info("[KCB定时同步] 工作日 16:00 定时触发");
        doSync("定时任务");
    }

    public String triggerManual() {
        if (running.get()) {
            return "同步任务正在运行中，请稍后再试";
        }
        new Thread(() -> doSync("手动触发"), "kcb-sync-manual").start();
        return "同步任务已在后台启动，请稍后查看状态";
    }

    private void doSync(String trigger) {
        if (!running.compareAndSet(false, true)) {
            log.warn("[KCB同步] 上一次任务未完成，跳过（来源：{}）", trigger);
            return;
        }

        String startTime = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date());
        lastSyncTime.set(startTime);
        log.info("[KCB同步] 开始 | 来源：{}", trigger);

        try {
            String result = kcbWindSyncService.syncIncremental();
            lastSyncResult.set("成功");
            log.info("[KCB同步] {}", result);
        } catch (Exception e) {
            lastSyncResult.set("失败: " + e.getMessage());
            log.error("[KCB同步] 执行异常", e);
        } finally {
            running.set(false);
        }
    }

    public boolean isRunning() {
        return running.get();
    }

    public String getLastSyncTime() {
        return lastSyncTime.get();
    }

    public String getLastSyncResult() {
        return lastSyncResult.get();
    }
}
