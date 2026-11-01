<template>
  <div class="kcb-page">
    <!-- 顶部栏 -->
    <div class="top-bar">
      <div class="top-left">
        <span class="back-btn" @click="$router.push('/Index')">← 返回</span>
        <span class="page-title">全部科创板收盘价指数</span>
      </div>
      <div class="top-right">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="yyyy-MM-dd"
          size="small"
          style="width:260px"
          @change="loadData"
        />
        <el-button type="primary" size="small" style="margin-left:10px" @click="loadData">查询</el-button>
        <el-divider direction="vertical" />
        <el-tooltip :content="syncTooltip" placement="bottom">
          <el-button
            :type="syncStatus.running ? 'warning' : 'success'"
            :loading="syncStatus.running"
            size="small"
            @click="triggerSync"
          >
            {{ syncStatus.running ? '同步中...' : '立即同步' }}
          </el-button>
        </el-tooltip>
      </div>
    </div>

    <!-- 说明卡片 -->
    <div class="desc-cards">
      <div class="desc-card" v-for="item in metricDesc" :key="item.key" :style="{ borderColor: item.color }">
        <div class="desc-dot" :style="{ background: item.color }"></div>
        <div>
          <div class="desc-name">{{ item.name }}</div>
          <div class="desc-sub">{{ item.sub }}</div>
        </div>
        <div class="desc-val" :style="{ color: item.color }">
          {{ latestValues[item.key] !== undefined ? latestValues[item.key].toFixed(2) + ' 元' : '--' }}
        </div>
      </div>
    </div>

    <!-- 折线图 -->
    <div class="chart-card">
      <div v-if="loading" class="loading-mask">
        <i class="el-icon-loading"></i> 加载中...
      </div>
      <div v-else-if="tableData.length === 0" class="empty-tip">
        暂无数据，请先运行 fetch_kcb_close.py 导入数据
      </div>
      <div v-else ref="chartDom" class="chart-dom"></div>
    </div>

    <!-- 数据表格 -->
    <div class="table-card" v-if="tableData.length > 0">
      <div class="table-title">日频数据（最新 {{ tableData.length }} 条）</div>
      <div class="table-wrap">
        <el-table :data="tableData" stripe size="small" height="320">
          <el-table-column prop="tradeDateStr" label="交易日期" width="120" />
          <el-table-column prop="closeArithmetic"    label="算术平均（元）"         align="right" min-width="170" />
          <el-table-column prop="closeFloatWeighted" label="流通股本加权（元）"     align="right" min-width="190" />
          <el-table-column prop="closeTotalWeighted" label="总股本加权（元）"       align="right" min-width="190" />
          <el-table-column prop="stockCount"         label="参与股票数"             align="right" width="120" />
        </el-table>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

const COLORS = {
  arithmetic:    '#5470c6',
  floatWeighted: '#91cc75',
  totalWeighted: '#fac858',
}

export default {
  name: 'KcbIndex',

  data() {
    const today = new Date()
    const sixMonthAgo = new Date(today)
    sixMonthAgo.setMonth(today.getMonth() - 6)

    return {
      dateRange: [this.fmt(sixMonthAgo), this.fmt(today)],
      loading:   false,
      tableData: [],
      chart:     null,
      syncStatus: { running: false, lastSyncTime: '-', lastSyncResult: '-' },
      syncTimer:  null,

      metricDesc: [
        {
          key:   'closeArithmetic',
          name:  '收盘价（算术平均）',
          sub:   '全部科创板股票收盘价简单平均',
          color: COLORS.arithmetic,
        },
        {
          key:   'closeFloatWeighted',
          name:  '收盘价（流通股本加权平均）',
          sub:   '以流通股本为权重的加权平均',
          color: COLORS.floatWeighted,
        },
        {
          key:   'closeTotalWeighted',
          name:  '收盘价（总股本加权平均）',
          sub:   '以总股本为权重的加权平均',
          color: COLORS.totalWeighted,
        },
      ],
    }
  },

  computed: {
    syncTooltip() {
      const s = this.syncStatus
      return `上次同步：${s.lastSyncTime}　结果：${s.lastSyncResult}`
    },
    latestValues() {
      if (!this.tableData.length) return {}
      const last = this.tableData[this.tableData.length - 1]
      return {
        closeArithmetic:    last.closeArithmetic,
        closeFloatWeighted: last.closeFloatWeighted,
        closeTotalWeighted: last.closeTotalWeighted,
      }
    },
  },

  mounted() {
    this.loadData()
    this.fetchSyncStatus()
    // 每 10 秒轮询一次同步状态（同步中时实时刷新）
    this.syncTimer = setInterval(this.fetchSyncStatus, 10000)
  },

  beforeDestroy() {
    if (this.chart) {
      this.chart.dispose()
      this.chart = null
    }
    if (this.syncTimer) clearInterval(this.syncTimer)
  },

  methods: {
    fmt(d) {
      if (!d) return ''
      const date = typeof d === 'string' ? new Date(d) : d
      const y = date.getFullYear()
      const m = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${y}-${m}-${day}`
    },

    tsToDateStr(ts) {
      // Java Date 序列化为毫秒时间戳
      return this.fmt(new Date(ts))
    },

    // ---- 同步相关 ----
    async fetchSyncStatus() {
      try {
        const res = await this.axios({ method: 'GET', url: 'http://localhost:9090/api/kcb-sync/status' })
        const prev = this.syncStatus.running
        this.syncStatus = res.data.data
        // 同步刚完成时，自动刷新图表数据
        if (prev && !this.syncStatus.running) {
          this.$message.success('数据同步完成，正在刷新...')
          this.loadData()
        }
      } catch (_) { /* 后端未启动时静默忽略 */ }
    },

    async triggerSync() {
      if (this.syncStatus.running) return
      try {
        const res = await this.axios({ method: 'POST', url: 'http://localhost:9090/api/kcb-sync/trigger' })
        this.$message.info(res.data.data)
        // 立刻拉一次状态，让按钮变为"同步中"
        setTimeout(this.fetchSyncStatus, 800)
      } catch (e) {
        this.$message.error('触发失败：' + e.message)
      }
    },

    // ---- 数据查询 ----
    async loadData() {
      this.loading = true
      try {
        const [startDate, endDate] = this.dateRange || []
        const res = await this.axios({
          method: 'GET',
          url:    'http://localhost:9090/api/kcb-close/list',
          params: { startDate, endDate },
        })
        const rows = (res.data.data || []).map(item => ({
          ...item,
          tradeDateStr:       this.tsToDateStr(item.tradeDate),
          closeArithmetic:    Number(item.closeArithmetic),
          closeFloatWeighted: Number(item.closeFloatWeighted),
          closeTotalWeighted: Number(item.closeTotalWeighted),
        }))
        this.tableData = rows
        this.$nextTick(() => this.renderChart(rows))
      } catch (e) {
        this.$message.error('数据加载失败：' + e.message)
      } finally {
        this.loading = false
      }
    },

    renderChart(rows) {
      if (!rows.length) return
      const dom = this.$refs.chartDom
      if (!dom) return

      if (!this.chart) {
        this.chart = echarts.init(dom)
      }

      const dates = rows.map(r => r.tradeDateStr)

      const option = {
        tooltip: {
          trigger:   'axis',
          formatter: params => {
            let s = `<b>${params[0].axisValue}</b><br/>`
            params.forEach(p => {
              s += `${p.marker}${p.seriesName}：<b>${p.value.toFixed(4)}</b> 元<br/>`
            })
            return s
          },
        },
        legend: {
          data:   ['算术平均', '流通股本加权', '总股本加权'],
          top:    10,
          right:  20,
        },
        grid: { top: 60, left: 60, right: 30, bottom: 60 },
        dataZoom: [
          { type: 'inside', start: 0, end: 100 },
          { type: 'slider', start: 0, end: 100, height: 25, bottom: 10 },
        ],
        xAxis: {
          type:        'category',
          data:        dates,
          axisLabel:   { rotate: 30, fontSize: 11 },
          boundaryGap: false,
        },
        yAxis: {
          type:      'value',
          name:      '元',
          nameGap:   10,
          axisLabel: { formatter: v => v.toFixed(2) },
          scale:     true,
        },
        series: [
          {
            name:      '算术平均',
            type:      'line',
            data:      rows.map(r => r.closeArithmetic),
            smooth:    true,
            symbol:    'none',
            lineStyle: { color: COLORS.arithmetic, width: 2 },
            itemStyle: { color: COLORS.arithmetic },
          },
          {
            name:      '流通股本加权',
            type:      'line',
            data:      rows.map(r => r.closeFloatWeighted),
            smooth:    true,
            symbol:    'none',
            lineStyle: { color: COLORS.floatWeighted, width: 2 },
            itemStyle: { color: COLORS.floatWeighted },
          },
          {
            name:      '总股本加权',
            type:      'line',
            data:      rows.map(r => r.closeTotalWeighted),
            smooth:    true,
            symbol:    'none',
            lineStyle: { color: COLORS.totalWeighted, width: 2 },
            itemStyle: { color: COLORS.totalWeighted },
          },
        ],
      }

      this.chart.setOption(option)
      window.addEventListener('resize', () => this.chart && this.chart.resize())
    },
  },
}
</script>

<style scoped>
.kcb-page {
  height: 100vh;
  background: #f5f7fa;
  padding: 0 0 40px;
  font-family: 'Microsoft YaHei', sans-serif;
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
}

/* 顶部栏 */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  padding: 14px 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,.08);
}
.top-left { display: flex; align-items: center; gap: 16px; }
.back-btn {
  color: #409eff;
  cursor: pointer;
  font-size: 14px;
}
.back-btn:hover { text-decoration: underline; }
.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e3c72;
}
.top-right { display: flex; align-items: center; }

/* 说明卡片 */
.desc-cards {
  display: flex;
  gap: 16px;
  padding: 20px 24px 0;
}
.desc-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  border-left: 4px solid;
  border-radius: 8px;
  padding: 14px 18px;
  box-shadow: 0 1px 4px rgba(0,0,0,.06);
}
.desc-dot {
  width: 10px; height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.desc-name { font-size: 14px; font-weight: 600; color: #333; }
.desc-sub  { font-size: 12px; color: #888; margin-top: 2px; }
.desc-val  { margin-left: auto; font-size: 18px; font-weight: 700; }

/* 折线图区域 */
.chart-card {
  margin: 16px 24px 0;
  background: #fff;
  border-radius: 8px;
  padding: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,.06);
  min-height: 400px;
  position: relative;
}
.chart-dom { width: 100%; height: 420px; }
.loading-mask, .empty-tip {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  color: #999;
}

/* 数据表格 */
.table-card {
  margin: 16px 24px 0;
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,.06);
}
.table-wrap {
  width: 100%;
  overflow-x: auto;
}
.table-wrap ::v-deep .el-table {
  min-width: 760px;
}
.table-title {
  font-size: 14px;
  font-weight: 600;
  color: #444;
  margin-bottom: 10px;
}
</style>
