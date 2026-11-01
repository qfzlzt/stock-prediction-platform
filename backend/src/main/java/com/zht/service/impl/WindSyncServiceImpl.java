package com.zht.service.impl;

import com.wind.api.W;
import com.wind.api.struct.WindData;
import com.zht.config.WindDllConfig;
import com.zht.constants.StockPoolConstants;
import com.zht.dao.DailyMarketDataDao;
import com.zht.dao.RealtimeMarketDataDao;
import com.zht.entity.DailyMarketData;
import com.zht.entity.RealtimeMarketData;
import com.zht.entity.dto.WindSyncRequest;
import com.zht.entity.dto.WindSyncResult;
import com.zht.service.WindSyncService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Isolation;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;
import org.springframework.util.StringUtils;

import javax.annotation.PreDestroy;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.TimeUnit;

@Service
public class WindSyncServiceImpl implements WindSyncService {

    @Autowired
    private WindDllConfig.WindReadyChecker windReadyChecker;

    private static final SimpleDateFormat DATE_ONLY_FORMAT = new SimpleDateFormat("yyyy-MM-dd");
    private static final SimpleDateFormat DATE_TIME_FORMAT = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
    private static final DateTimeFormatter LOCAL_DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd");
    private static final DateTimeFormatter LOCAL_DATETIME_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    // 日频参数
    private static final String DAILY_OPTIONS = "ruleType=3;unit=1;VolumeRatio_N=5;MTM_interDay=12;MTM_N=6;MTM_IO=1";

    // 日频字段
    private static final String DAILY_FIELDS =
            "pe_ttm,pb_mrq,pct_chg,ev,mkt_cap_float,total_shares,share_issuing_mkt,maxup,maxdown,chg,vwap,volume,amt,turn,vol_ratio,high,low,open,close,pre_close,adjfactor,MTM";

    // 实时字段
    private static final String REALTIME_FIELDS =
            "rt_date,rt_time,rt_latest,rt_chg,rt_pct_chg,rt_vwap,rt_vol,rt_amt,rt_turn,rt_vol_ratio,rt_high,rt_low,rt_open,rt_pre_close,rt_pre_latest,rt_adj_factor";

    private final DailyMarketDataDao dailyMarketDataDao;
    private final RealtimeMarketDataDao realtimeMarketDataDao;

    public WindSyncServiceImpl(DailyMarketDataDao dailyMarketDataDao,
                               RealtimeMarketDataDao realtimeMarketDataDao) {
        this.dailyMarketDataDao = dailyMarketDataDao;
        this.realtimeMarketDataDao = realtimeMarketDataDao;
    }

    @Override
    @Transactional(rollbackFor = Exception.class, isolation = Isolation.READ_COMMITTED)
    public WindSyncResult syncMarketData(WindSyncRequest request) {
        windReadyChecker.ensureReady();

        // 解析参数
        String tradeDate = resolveTradeDate(request.getTradeDate());
        List<String> stockCodes = resolveStockCodes(request.getStockCodes());
        int days = request.getDays() != null ? request.getDays() : 60;
        int realtimeRetainMinutes = request.getRealtimeRetainMinutes() != null ? request.getRealtimeRetainMinutes() : 30;

        boolean syncDaily = request.getSyncDaily() == null || request.getSyncDaily();
        boolean syncRealtime = request.getSyncRealtime() == null || request.getSyncRealtime();

        System.out.println("========== 开始同步数据 ==========");
        System.out.println("交易日期: " + tradeDate);
        System.out.println("日频查询天数: " + days);
        System.out.println("实时数据保留分钟数: " + realtimeRetainMinutes);
        System.out.println("股票列表: " + stockCodes);

        WindSyncResult result = new WindSyncResult();
        result.setTradeDate(tradeDate);
        result.setStockCount(stockCodes.size());

        List<String> failedStocks = new ArrayList<>();

        // 1. 处理日频数据
        if (syncDaily) {
            processDailyData(stockCodes, tradeDate, days, result, failedStocks);
        }

        // 2. 处理实时数据
        if (syncRealtime) {
            processRealtimeData(stockCodes, realtimeRetainMinutes, result, failedStocks);
        }

        result.setFailedStocks(failedStocks);

        System.out.println("\n========== 同步完成 ==========");
        System.out.println("日频数据保存: " + result.getDailySaved() + " 条");
        System.out.println("日频数据返回: " + (result.getDailyDataList() != null ? result.getDailyDataList().size() : 0) + " 条");
        System.out.println("实时数据保存: " + result.getRealtimeSaved() + " 条");
        System.out.println("实时快照返回: " + (result.getRealtimeSnapshotList() != null ? result.getRealtimeSnapshotList().size() : 0) + " 条");
        System.out.println("失败数量: " + failedStocks.size());
        System.out.println("==============================");

        return result;
    }

    /**
     * 处理日频数据：拉取指定天数历史数据，删除30天前数据，返回最近30天数据
     */
    private void processDailyData(List<String> stockCodes, String targetDate, int days,
                                   WindSyncResult result, List<String> failedStocks) {
        System.out.println("\n--- 处理日频数据 ---");

        // 计算起始日期：从 targetDate 往前推 days 天
        LocalDate endDate = LocalDate.parse(targetDate, LOCAL_DATE_FORMATTER);
        LocalDate startDate = endDate.minusDays(days - 1);
        String startDateStr = startDate.format(LOCAL_DATE_FORMATTER);
        String endDateStr = endDate.format(LOCAL_DATE_FORMATTER);

        // 计算30天前的日期（用于删除）
        LocalDate deleteThresholdDate = endDate.minusDays(days);
        Date deleteThreshold = java.sql.Date.valueOf(deleteThresholdDate);

        System.out.println("日频查询范围: " + startDateStr + " 至 " + endDateStr);
        System.out.println("删除阈值: " + deleteThresholdDate + " 之前的数据");

        List<DailyMarketData> allDailyData = new ArrayList<>();

        // 拉取每只股票的历史日频数据
        for (String stockCode : stockCodes) {
            try {
                List<DailyMarketData> dailyList = fetchDailyDataRange(stockCode, startDateStr, endDateStr);
                if (dailyList != null && !dailyList.isEmpty()) {
                    allDailyData.addAll(dailyList);
                    System.out.println("✅ 成功获取日频数据: " + stockCode + ", 共 " + dailyList.size() + " 条");
                } else {
                    System.out.println("⚠️ " + stockCode + " 无日频数据");
                    failedStocks.add(stockCode + ": daily -> 无数据");
                }
            } catch (Exception e) {
                String errorMsg = stockCode + ": daily -> " + e.getMessage();
                System.err.println("❌ " + errorMsg);
                failedStocks.add(errorMsg);
            }
        }

        // 保存日频数据到数据库（upsert）
        if (!allDailyData.isEmpty()) {
            try {
                // 先删除30天前的旧数据（只删除查询范围内的股票）
                int deletedCount = dailyMarketDataDao.deleteByStockCodesAndTradeDateBefore(stockCodes, deleteThreshold);
                System.out.println("🗑️ 已删除 " + deletedCount + " 条30天前的日频数据");

                // 批量upsert新数据
                dailyMarketDataDao.batchUpsert(allDailyData);
                System.out.println("✅ 成功保存 " + allDailyData.size() + " 条日频数据");
                result.setDailySaved(allDailyData.size());

                // 查询最近30天的数据返回给前端
                List<DailyMarketData> recentData = queryRecentDailyData(stockCodes, startDate, endDate);
                result.setDailyDataList(recentData);
                System.out.println("📊 返回最近日频数据: " + recentData.size() + " 条");

            } catch (Exception e) {
                System.err.println("❌ 保存日频数据失败: " + e.getMessage());
                failedStocks.add("批量保存日频数据失败: " + e.getMessage());
                e.printStackTrace();
            }
        } else {
            System.out.println("⚠️ 没有日频数据可保存");
            // 即使没有新数据，也返回数据库中已有的最近30天数据
            List<DailyMarketData> recentData = queryRecentDailyData(stockCodes, startDate, endDate);
            result.setDailyDataList(recentData);
            System.out.println("📊 返回已有日频数据: " + recentData.size() + " 条");
        }
    }

    /**
     * 查询最近的日频数据（从数据库）
     */
    private List<DailyMarketData> queryRecentDailyData(List<String> stockCodes, LocalDate startDate, LocalDate endDate) {
        try {
            Date start = java.sql.Date.valueOf(startDate);
            Date end = java.sql.Date.valueOf(endDate);
            return dailyMarketDataDao.selectByStockCodesAndDateRange(stockCodes, start, end);
        } catch (Exception e) {
            System.err.println("查询最近日频数据失败: " + e.getMessage());
            return new ArrayList<>();
        }
    }

    /**
     * 拉取指定日期范围内的日频数据
     */
    private List<DailyMarketData> fetchDailyDataRange(String stockCode, String startDate, String endDate) {
        List<DailyMarketData> resultList = new ArrayList<>();
        try {
            WindData windData = W.wsd(
                    stockCode,
                    DAILY_FIELDS,
                    startDate,
                    endDate,
                    DAILY_OPTIONS
            );

            if (windData == null || windData.getErrorId() != 0) {
                return resultList;
            }

            resultList = parseDailyDataRange(windData, stockCode);
        } catch (Exception e) {
            System.err.println("获取 " + stockCode + " 范围数据异常: " + e.getMessage());
        }
        return resultList;
    }

    /**
     * 解析多日日频数据
     */
    @SuppressWarnings("unchecked")
    private List<DailyMarketData> parseDailyDataRange(WindData windData, String stockCode) {
        List<DailyMarketData> resultList = new ArrayList<>();

        try {
            Object fieldsObj = windData.getFields();
            String[] fieldsArray = null;

            if (fieldsObj instanceof String[]) {
                fieldsArray = (String[]) fieldsObj;
            } else if (fieldsObj instanceof List) {
                List<String> fieldsList = (List<String>) fieldsObj;
                fieldsArray = fieldsList.toArray(new String[0]);
            } else if (fieldsObj instanceof Object[]) {
                Object[] objArray = (Object[]) fieldsObj;
                fieldsArray = new String[objArray.length];
                for (int i = 0; i < objArray.length; i++) {
                    fieldsArray[i] = objArray[i] != null ? objArray[i].toString() : null;
                }
            } else {
                return resultList;
            }

            Object datesObj = windData.getTimes();
            String[] datesArray = null;

            if (datesObj instanceof String[]) {
                datesArray = (String[]) datesObj;
            } else if (datesObj instanceof List) {
                List<String> datesList = (List<String>) datesObj;
                datesArray = datesList.toArray(new String[0]);
            } else if (datesObj instanceof Object[]) {
                Object[] objArray = (Object[]) datesObj;
                datesArray = new String[objArray.length];
                for (int i = 0; i < objArray.length; i++) {
                    datesArray[i] = objArray[i] != null ? objArray[i].toString() : null;
                }
            } else {
                return resultList;
            }

            Object dataObj = windData.getData();
            Object[][] dataArray = null;

            if (dataObj instanceof List) {
                List<Object> dataList = (List<Object>) dataObj;
                int rows = datesArray.length;
                int cols = fieldsArray.length;
                dataArray = new Object[rows][cols];
                for (int i = 0; i < rows && i * cols < dataList.size(); i++) {
                    for (int j = 0; j < cols && i * cols + j < dataList.size(); j++) {
                        dataArray[i][j] = dataList.get(i * cols + j);
                    }
                }
            } else if (dataObj instanceof Object[][]) {
                dataArray = (Object[][]) dataObj;
            } else {
                return resultList;
            }

            for (int row = 0; row < datesArray.length && row < dataArray.length; row++) {
                String tradeDate = datesArray[row];
                Object[] rowData = dataArray[row];

                Map<String, Object> valueMap = new HashMap<>();
                for (int col = 0; col < fieldsArray.length && col < rowData.length; col++) {
                    String field = fieldsArray[col];
                    Object value = rowData[col];
                    if (field != null) {
                        valueMap.put(field.toLowerCase(), value);
                    }
                }

                DailyMarketData entity = createDailyEntity(stockCode, tradeDate, valueMap);
                if (entity != null) {
                    resultList.add(entity);
                }
            }
        } catch (Exception e) {
            System.err.println("解析 " + stockCode + " 范围数据失败: " + e.getMessage());
        }

        return resultList;
    }

    /**
     * 创建日频数据实体
     */
    private DailyMarketData createDailyEntity(String stockCode, String tradeDate, Map<String, Object> valueMap) {
        try {
            Double close = toExactDouble(valueMap.get("close"));
            Double shareIssuingMkt = toExactDouble(valueMap.get("share_issuing_mkt"));
            Double mktCapFloat = toExactDouble(valueMap.get("mkt_cap_float"));

            if (mktCapFloat == null && close != null && shareIssuingMkt != null) {
                mktCapFloat = close * shareIssuingMkt;
            }

            DailyMarketData entity = new DailyMarketData();
            entity.setStockCode(stockCode);
            entity.setTradeDate(parseDate(tradeDate));

            entity.setPe(toExactDouble(valueMap.get("pe_ttm")));
            entity.setPb(toExactDouble(valueMap.get("pb_mrq")));
            entity.setPctChg(toExactDouble(valueMap.get("pct_chg")));
            entity.setEv(toExactDouble(valueMap.get("ev")));
            entity.setMktCapFloat(mktCapFloat);
            entity.setTotalShares(toExactDouble(valueMap.get("total_shares")));
            entity.setShareIssuingMkt(toExactDouble(valueMap.get("share_issuing_mkt")));
            entity.setMaxup(toExactDouble(valueMap.get("maxup")));
            entity.setMaxdown(toExactDouble(valueMap.get("maxdown")));
            entity.setChg(toExactDouble(valueMap.get("chg")));
            entity.setVwap(toExactDouble(valueMap.get("vwap")));
            entity.setVolume(toExactDouble(valueMap.get("volume")));
            entity.setAmt(toExactDouble(valueMap.get("amt")));
            entity.setTurn(toExactDouble(valueMap.get("turn")));
            entity.setVolRatio(toExactDouble(valueMap.get("vol_ratio")));
            entity.setHigh(toExactDouble(valueMap.get("high")));
            entity.setLow(toExactDouble(valueMap.get("low")));
            entity.setOpen(toExactDouble(valueMap.get("open")));
            entity.setClose(toExactDouble(valueMap.get("close")));
            entity.setPreClose(toExactDouble(valueMap.get("pre_close")));
            entity.setAdjfactor(toExactDouble(valueMap.get("adjfactor")));

            entity.setCreateTime(new Date());
            entity.setUpdateTime(new Date());

            return entity;
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 处理实时数据：拉取最近30分钟的每分钟数据，删除30分钟前数据，返回最新快照
     */
    private void processRealtimeData(List<String> stockCodes, int retainMinutes,
                                      WindSyncResult result, List<String> failedStocks) {
        System.out.println("\n--- 处理实时数据 ---");

        LocalDateTime now = LocalDateTime.now();
        LocalDateTime thresholdTime = now.minusMinutes(retainMinutes);
        Date thresholdDate = java.sql.Timestamp.valueOf(thresholdTime);

        // 1. 分批删除30分钟前的旧数据（带重试机制）
        deleteOldRealtimeDataBatchWithRetry(stockCodes, thresholdDate, 3);

        // 2. 检查需要拉取的时间段
        List<LocalDateTime> missingTimeSlots = findMissingTimeSlots(stockCodes, thresholdTime, now, retainMinutes);
        System.out.println("需要补录的时间段数量: " + missingTimeSlots.size());

        // 3. 拉取缺失的每分钟数据
        List<RealtimeMarketData> allRealtimeData = new ArrayList<>();
        for (LocalDateTime timeSlot : missingTimeSlots) {
            List<RealtimeMarketData> slotData = fetchRealtimeDataForTimeSlot(stockCodes, timeSlot);
            allRealtimeData.addAll(slotData);
            System.out.println("📊 拉取 " + timeSlot.format(LOCAL_DATETIME_FORMATTER) + " 数据: " + slotData.size() + " 条");

            try {
                TimeUnit.MILLISECONDS.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }

        // 4. 保存新拉取的实时数据（使用 upsert，带重试机制）
        if (!allRealtimeData.isEmpty()) {
            boolean saved = saveRealtimeDataWithRetry(allRealtimeData, 3);
            if (saved) {
                System.out.println("✅ 成功保存 " + allRealtimeData.size() + " 条实时数据");
                result.setRealtimeSaved(allRealtimeData.size());
            } else {
                System.err.println("❌ 保存实时数据失败");
                failedStocks.add("批量保存实时数据失败");
            }
        }

        // 5. 查询最新时间戳的所有股票实时快照返回给前端
        try {
            List<RealtimeMarketData> latestSnapshot = realtimeMarketDataDao.selectLatestSnapshot(stockCodes);
            result.setRealtimeSnapshotList(latestSnapshot);
            System.out.println("📊 返回最新实时快照: " + latestSnapshot.size() + " 条");
        } catch (Exception e) {
            System.err.println("❌ 查询最新快照失败: " + e.getMessage());
        }
    }

    /**
     * 分批删除旧实时数据（带重试机制）
     */
    private void deleteOldRealtimeDataBatchWithRetry(List<String> stockCodes, Date thresholdDate, int maxRetries) {
        int retryCount = 0;
        while (retryCount < maxRetries) {
            try {
                deleteOldRealtimeDataBatch(stockCodes, thresholdDate);
                return;
            } catch (Exception e) {
                retryCount++;
                if (e.getMessage() != null && e.getMessage().contains("Deadlock") && retryCount < maxRetries) {
                    System.out.println("⚠️ 删除操作发生死锁，第 " + retryCount + " 次重试...");
                    try {
                        TimeUnit.MILLISECONDS.sleep(100 * retryCount);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                    }
                } else {
                    System.err.println("删除旧实时数据失败: " + e.getMessage());
                    e.printStackTrace();
                    return;
                }
            }
        }
    }

    /**
     * 分批删除旧实时数据
     */
    private void deleteOldRealtimeDataBatch(List<String> stockCodes, Date thresholdDate) {
        int totalDeleted = 0;
        int batchSize = 1000;
        int maxBatches = 100; // 防止无限循环
        
        for (int batch = 0; batch < maxBatches; batch++) {
            try {
                int deleted = realtimeMarketDataDao.deleteByStockCodesAndTimestampBeforeWithLimit(
                        stockCodes, thresholdDate, batchSize);
                totalDeleted += deleted;
                
                if (deleted < batchSize) {
                    break;
                }
                
                // 避免删除过快，给其他事务机会
                TimeUnit.MILLISECONDS.sleep(50);
            } catch (Exception e) {
                System.err.println("删除批次失败: " + e.getMessage());
                break;
            }
        }
        
        System.out.println("🗑️ 已删除 " + totalDeleted + " 条30分钟前的实时数据");
    }

    /**
     * 保存实时数据（带重试机制）
     */
    private boolean saveRealtimeDataWithRetry(List<RealtimeMarketData> dataList, int maxRetries) {
        int retryCount = 0;
        while (retryCount < maxRetries) {
            try {
                realtimeMarketDataDao.batchUpsert(dataList);
                return true;
            } catch (Exception e) {
                retryCount++;
                if (e.getMessage() != null && e.getMessage().contains("Deadlock") && retryCount < maxRetries) {
                    System.out.println("⚠️ 保存操作发生死锁，第 " + retryCount + " 次重试...");
                    try {
                        TimeUnit.MILLISECONDS.sleep(100 * retryCount);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                    }
                } else {
                    System.err.println("保存实时数据失败: " + e.getMessage());
                    e.printStackTrace();
                    return false;
                }
            }
        }
        return false;
    }

    /**
     * 查找缺失的时间段
     */
    private List<LocalDateTime> findMissingTimeSlots(List<String> stockCodes,
                                                      LocalDateTime startTime,
                                                      LocalDateTime endTime,
                                                      int maxMinutes) {
        List<LocalDateTime> missingSlots = new ArrayList<>();

        // 按分钟遍历时间范围
        LocalDateTime current = startTime.withSecond(0).withNano(0);
        LocalDateTime end = endTime.withSecond(0).withNano(0);

        while (!current.isAfter(end) && missingSlots.size() < maxMinutes) {
            missingSlots.add(current);
            current = current.plusMinutes(1);
        }

        if (missingSlots.size() > maxMinutes) {
            missingSlots = missingSlots.subList(0, maxMinutes);
        }

        return missingSlots;
    }

    /**
     * 拉取指定时间点的实时数据
     */
    private List<RealtimeMarketData> fetchRealtimeDataForTimeSlot(List<String> stockCodes, LocalDateTime timeSlot) {
        List<RealtimeMarketData> resultList = new ArrayList<>();

        try {
            String codes = String.join(",", stockCodes);
            WindData windData = W.wsq(codes, REALTIME_FIELDS);

            if (windData != null && windData.getErrorId() == 0) {
                List<RealtimeMarketData> snapshotList = parseRealtimeSnapshot(windData);

                // 将数据的时间戳设置为目标时间
                for (RealtimeMarketData data : snapshotList) {
                    data.setDatatimestamp(java.sql.Timestamp.valueOf(timeSlot));
                    data.setCreatedat(new Date());
                    data.setUpdatedat(new Date());
                }
                resultList.addAll(snapshotList);
            }
        } catch (Exception e) {
            System.err.println("拉取 " + timeSlot + " 实时数据失败: " + e.getMessage());
        }

        return resultList;
    }

    /**
     * 解析日频数据（单日）
     */
    @SuppressWarnings("unchecked")
    private DailyMarketData parseDailyData(WindData windData, String stockCode, String tradeDate) {
        try {
            Object fieldsObj = windData.getFields();
            String[] fieldsArray = null;

            if (fieldsObj instanceof String[]) {
                fieldsArray = (String[]) fieldsObj;
            } else if (fieldsObj instanceof List) {
                List<String> fieldsList = (List<String>) fieldsObj;
                fieldsArray = fieldsList.toArray(new String[0]);
            } else if (fieldsObj instanceof Object[]) {
                Object[] objArray = (Object[]) fieldsObj;
                fieldsArray = new String[objArray.length];
                for (int i = 0; i < objArray.length; i++) {
                    fieldsArray[i] = objArray[i] != null ? objArray[i].toString() : null;
                }
            } else {
                return null;
            }

            Object dataObj = windData.getData();
            List<Object> dataList = new ArrayList<>();

            if (dataObj instanceof List) {
                dataList = (List<Object>) dataObj;
            } else if (dataObj instanceof Object[][]) {
                Object[][] dataArray = (Object[][]) dataObj;
                if (dataArray.length > 0) {
                    Object[] lastRow = dataArray[dataArray.length - 1];
                    dataList.addAll(Arrays.asList(lastRow));
                }
            } else if (dataObj instanceof Object[]) {
                Object[] dataArray = (Object[]) dataObj;
                dataList.addAll(Arrays.asList(dataArray));
            } else {
                return null;
            }

            if (fieldsArray == null || dataList.isEmpty()) {
                return null;
            }

            Map<String, Object> valueMap = new HashMap<>();
            for (int i = 0; i < fieldsArray.length && i < dataList.size(); i++) {
                String field = fieldsArray[i];
                Object value = dataList.get(i);
                if (field != null) {
                    valueMap.put(field.toLowerCase(), value);
                }
            }

            return createDailyEntity(stockCode, tradeDate, valueMap);
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 解析实时数据快照
     */
    @SuppressWarnings("unchecked")
    private List<RealtimeMarketData> parseRealtimeSnapshot(WindData windData) {
        List<RealtimeMarketData> resultList = new ArrayList<>();

        try {
            Object fieldsObj = windData.getFields();
            String[] fieldsArray = null;

            if (fieldsObj instanceof String[]) {
                fieldsArray = (String[]) fieldsObj;
            } else if (fieldsObj instanceof List) {
                List<String> fieldsList = (List<String>) fieldsObj;
                fieldsArray = fieldsList.toArray(new String[0]);
            } else if (fieldsObj instanceof Object[]) {
                Object[] objArray = (Object[]) fieldsObj;
                fieldsArray = new String[objArray.length];
                for (int i = 0; i < objArray.length; i++) {
                    fieldsArray[i] = objArray[i] != null ? objArray[i].toString() : null;
                }
            } else {
                return resultList;
            }

            Object codesObj = windData.getCodes();
            String[] codesArray = null;

            if (codesObj instanceof String[]) {
                codesArray = (String[]) codesObj;
            } else if (codesObj instanceof List) {
                List<String> codesList = (List<String>) codesObj;
                codesArray = codesList.toArray(new String[0]);
            } else if (codesObj instanceof Object[]) {
                Object[] objArray = (Object[]) codesObj;
                codesArray = new String[objArray.length];
                for (int i = 0; i < objArray.length; i++) {
                    codesArray[i] = objArray[i] != null ? objArray[i].toString() : null;
                }
            } else {
                return resultList;
            }

            Object dataObj = windData.getData();

            if (dataObj instanceof List) {
                List<Object> dataList = (List<Object>) dataObj;
                int expectedSize = fieldsArray.length;
                int stockCount = dataList.size() / expectedSize;

                for (int stockIndex = 0; stockIndex < stockCount && stockIndex < codesArray.length; stockIndex++) {
                    String stockCode = codesArray[stockIndex];
                    Map<String, Object> valueMap = new HashMap<>();

                    for (int fieldIndex = 0; fieldIndex < expectedSize; fieldIndex++) {
                        int dataIndex = stockIndex * expectedSize + fieldIndex;
                        if (dataIndex < dataList.size()) {
                            String field = fieldsArray[fieldIndex];
                            Object value = dataList.get(dataIndex);
                            if (field != null) {
                                valueMap.put(field.toLowerCase(), value);
                            }
                        }
                    }

                    RealtimeMarketData entity = createRealtimeEntity(stockCode, valueMap);
                    if (entity != null) {
                        resultList.add(entity);
                    }
                }
            } else if (dataObj instanceof Object[][]) {
                Object[][] dataArray = (Object[][]) dataObj;

                for (int row = 0; row < dataArray.length && row < codesArray.length; row++) {
                    String stockCode = codesArray[row];
                    Object[] rowData = dataArray[row];

                    Map<String, Object> valueMap = new HashMap<>();
                    for (int col = 0; col < fieldsArray.length && col < rowData.length; col++) {
                        String field = fieldsArray[col];
                        Object value = rowData[col];
                        if (field != null) {
                            valueMap.put(field.toLowerCase(), value);
                        }
                    }

                    RealtimeMarketData entity = createRealtimeEntity(stockCode, valueMap);
                    if (entity != null) {
                        resultList.add(entity);
                    }
                }
            }
        } catch (Exception e) {
            System.err.println("解析实时快照失败: " + e.getMessage());
        }

        return resultList;
    }

    /**
     * 创建实时数据实体
     */
    private RealtimeMarketData createRealtimeEntity(String stockCode, Map<String, Object> valueMap) {
        try {
            RealtimeMarketData entity = new RealtimeMarketData();
            entity.setStockcode(stockCode);

            entity.setLatestprice(toExactBigDecimal(valueMap.get("rt_latest"), 2));
            entity.setPricechange(toExactBigDecimal(valueMap.get("rt_chg"), 2));
            entity.setPricechangerate(toExactBigDecimal(valueMap.get("rt_pct_chg"), 4));
            entity.setAverageprice(toExactBigDecimal(valueMap.get("rt_vwap"), 2));
            entity.setHighestprice(toExactBigDecimal(valueMap.get("rt_high"), 2));
            entity.setLowestprice(toExactBigDecimal(valueMap.get("rt_low"), 2));
            entity.setOpeningprice(toExactBigDecimal(valueMap.get("rt_open"), 2));
            entity.setPrecloseprice(toExactBigDecimal(valueMap.get("rt_pre_close"), 2));
            entity.setCloseprice(toExactBigDecimal(valueMap.get("rt_pre_latest"), 2));

            entity.setTotalvolume(toExactBigDecimal(valueMap.get("rt_vol"), 0));
            entity.setTurnover(toExactBigDecimal(valueMap.get("rt_amt"), 2));
            entity.setTurnoverrate(toExactBigDecimal(valueMap.get("rt_turn"), 4));
            entity.setVolumeratio(toExactBigDecimal(valueMap.get("rt_vol_ratio"), 2));
            entity.setAdjfactor(toExactBigDecimal(valueMap.get("rt_adj_factor"), 4));

            Object rtDateObj = valueMap.get("rt_date");
            Object rtTimeObj = valueMap.get("rt_time");

            String rtDate = rtDateObj == null ? null : String.valueOf(rtDateObj);
            String rtTime = rtTimeObj == null ? null : String.valueOf(rtTimeObj);

            entity.setDatatimestamp(resolveRealtimeTimestamp(rtDate, rtTime));
            entity.setCreatedat(new Date());
            entity.setUpdatedat(new Date());

            return entity;
        } catch (Exception e) {
            return null;
        }
    }

    private Double toExactDouble(Object value) {
        if (value == null) {
            return null;
        }
        try {
            String str = value.toString().trim();
            if (str.isEmpty() || "null".equalsIgnoreCase(str) || "NaN".equalsIgnoreCase(str)) {
                return null;
            }
            return Double.valueOf(str);
        } catch (Exception e) {
            return null;
        }
    }

    private BigDecimal toExactBigDecimal(Object value) {
        if (value == null) {
            return null;
        }
        try {
            String str = value.toString().trim();
            if (str.isEmpty() || "null".equalsIgnoreCase(str) || "NaN".equals(str)) {
                return null;
            }
            return new BigDecimal(str);
        } catch (Exception e) {
            return null;
        }
    }

    private BigDecimal toExactBigDecimal(Object value, int scale) {
        BigDecimal bd = toExactBigDecimal(value);
        if (bd == null) {
            return null;
        }
        try {
            return bd.setScale(scale, RoundingMode.HALF_UP);
        } catch (Exception e) {
            return bd;
        }
    }

    private Date resolveRealtimeTimestamp(String rtDate, String rtTime) {
        if (!StringUtils.hasText(rtDate)) {
            return new Date();
        }
        try {
            String cleanDate = rtDate.trim();
            if (cleanDate.length() == 8 && cleanDate.matches("\\d+")) {
                cleanDate = cleanDate.substring(0, 4) + "-" +
                        cleanDate.substring(4, 6) + "-" +
                        cleanDate.substring(6, 8);
            }

            String time = normalizeRealtimeTime(rtTime);
            return DATE_TIME_FORMAT.parse(cleanDate + " " + time);
        } catch (Exception e) {
            return new Date();
        }
    }

    private String normalizeRealtimeTime(String rtTime) {
        if (!StringUtils.hasText(rtTime)) {
            return DATE_TIME_FORMAT.format(new Date()).substring(11);
        }
        String trimmed = rtTime.trim();
        if (trimmed.length() == 6 && trimmed.matches("\\d+")) {
            return trimmed.substring(0, 2) + ":" + trimmed.substring(2, 4) + ":" + trimmed.substring(4, 6);
        }
        if (trimmed.contains(":")) {
            return trimmed.length() == 5 ? trimmed + ":00" : trimmed;
        }
        return DATE_TIME_FORMAT.format(new Date()).substring(11);
    }

    private Date parseDate(String date) {
        try {
            return DATE_ONLY_FORMAT.parse(date);
        } catch (ParseException e) {
            throw new IllegalStateException("tradeDate 格式必须为 yyyy-MM-dd");
        }
    }

    private String resolveTradeDate(String inputDate) {
        if (StringUtils.hasText(inputDate)) {
            return inputDate.trim();
        }
        return LocalDate.now().format(LOCAL_DATE_FORMATTER);
    }

    private List<String> resolveStockCodes(List<String> requestCodes) {
        Set<String> set = new LinkedHashSet<>();
        if (!CollectionUtils.isEmpty(requestCodes)) {
            for (String code : requestCodes) {
                if (StringUtils.hasText(code)) {
                    set.add(code.trim());
                }
            }
        }
        if (set.isEmpty()) {
            set.addAll(StockPoolConstants.DEFAULT_STOCK_CODES);
        }
        return new ArrayList<>(set);
    }

    @PreDestroy
    public void destroy() {
        try {
            W.stop();
            System.out.println("Wind API连接已关闭");
        } catch (Exception e) {
            System.err.println("关闭Wind API连接失败: " + e.getMessage());
        }
    }
}