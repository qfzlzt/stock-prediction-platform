<template>
  <div class="company-detail-container">
    <!-- 返回按钮 -->
    <div class="back-button">
      <el-button type="primary" icon="el-icon-arrow-left" @click="goBack">返回列表</el-button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-spinner></el-spinner>
      <div class="loading-text">加载公司详情中...</div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <el-alert
        :title="error"
        type="error"
        show-icon>
      </el-alert>
    </div>

    <!-- 公司详情内容 -->
    <div v-else class="company-detail-card">
      <el-card class="detail-card">
        <div slot="header" class="detail-header">
          <span class="company-title">{{ companyDetail.stockname }} ({{ companyDetail.stockcode }})</span>
          <el-tag :type="getStatusTagType(companyDetail.status)" size="medium">
            {{ getStatusLabel(companyDetail.status) }}
          </el-tag>
        </div>

        <!-- 基本信息 -->
        <el-tabs v-model="activeTab" type="border-card">
          <el-tab-pane label="基本信息" name="basic">
            <el-descriptions :column="2" border class="detail-descriptions">
              <el-descriptions-item label="ID">{{ companyDetail.id || '--' }}</el-descriptions-item>
              <el-descriptions-item label="证券代码">{{ companyDetail.stockcode || '--' }}</el-descriptions-item>
              <el-descriptions-item label="证券简称">{{ companyDetail.stockname || '--' }}</el-descriptions-item>
              <el-descriptions-item label="英文简称">{{ companyDetail.englishname || '--' }}</el-descriptions-item>
              <el-descriptions-item label="上市版">{{ companyDetail.markettype || '--' }}</el-descriptions-item>
              <el-descriptions-item label="股票类别">{{ companyDetail.stockcategory || '--' }}</el-descriptions-item>
              <el-descriptions-item label="上市日期">{{ formatDate(companyDetail.listingdate) }}</el-descriptions-item>
              <el-descriptions-item label="交易状态">{{ getStatusLabel(companyDetail.status) }}</el-descriptions-item>
              <el-descriptions-item label="所属行业">{{ companyDetail.industrylevel || '--' }}</el-descriptions-item>
              <el-descriptions-item label="法定代表人">{{ companyDetail.legalrepresentative || '--' }}</el-descriptions-item>
              <el-descriptions-item label="注册资本(元)">{{ formatNumber(companyDetail.registeredcapital) }}</el-descriptions-item>
              <el-descriptions-item label="成立日期">{{ formatDate(companyDetail.registrationtime) }}</el-descriptions-item>
              <el-descriptions-item label="省份">{{ companyDetail.registrationprovince || '--' }}</el-descriptions-item>
              <el-descriptions-item label="员工总数">{{ companyDetail.employeecount ? companyDetail.employeecount + '人' : '--' }}</el-descriptions-item>
              <el-descriptions-item label="独立董事" :span="2">{{ companyDetail.independentdirectors || '--' }}</el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>

          <el-tab-pane label="公司简介" name="intro">
            <div class="text-content">
              <p>{{ companyDetail.companyintro || '暂无公司简介' }}</p>
            </div>
          </el-tab-pane>

          <el-tab-pane label="经营范围" name="scope">
            <div class="text-content">
              <p>{{ companyDetail.businessscope || '暂无经营范围信息' }}</p>
            </div>
          </el-tab-pane>

          <el-tab-pane label="财务状况" name="financial">
            <div v-if="!financialData || financialData.length === 0" class="empty-data">
              暂无财务数据
            </div>
            <el-table v-else :data="financialData" stripe style="width: 100%">
              <el-table-column prop="reportperiod" label="报告年份" width="100"></el-table-column>
              <el-table-column prop="reporttype" label="报告类型" width="100">
                <template slot-scope="scope">{{ getReportTypeLabel(scope.row.reporttype) }}</template>
              </el-table-column>
              <el-table-column prop="totaloperatingrevenue" label="营业总收入(亿元)" width="150">
                <template slot-scope="scope">{{ formatNumber(scope.row.totaloperatingrevenue) }}</template>
              </el-table-column>
              <el-table-column prop="netprofitattributable" label="净利润(亿元)" width="150">
                <template slot-scope="scope">{{ formatNumber(scope.row.netprofitattributable) }}</template>
              </el-table-column>
              <el-table-column prop="basiceps" label="每股收益(元)" width="120">
                <template slot-scope="scope">{{ formatRatio(scope.row.basiceps) }}</template>
              </el-table-column>
              <el-table-column prop="roe" label="ROE(%)" width="100">
                <template slot-scope="scope">{{ formatPercent(scope.row.roe) }}</template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="实时行情" name="realtime">
            <div v-if="!realtimeData || realtimeData.length === 0" class="empty-data">
              暂无实时行情数据
            </div>
            <el-descriptions v-else :column="4" border class="detail-descriptions">
              <el-descriptions-item label="最新价">
                <span :class="realtimeData[0].pricechange >= 0 ? 'positive' : 'negative'">
                  ¥{{ formatPrice(realtimeData[0].latestprice) }}
                </span>
              </el-descriptions-item>
              <el-descriptions-item label="涨跌">
                <span :class="realtimeData[0].pricechange >= 0 ? 'positive' : 'negative'">
                  {{ realtimeData[0].pricechange >= 0 ? '+' : '' }}{{ formatPrice(realtimeData[0].pricechange) }}
                </span>
              </el-descriptions-item>
              <el-descriptions-item label="涨幅">
                <span :class="realtimeData[0].pricechangerate >= 0 ? 'positive' : 'negative'">
                  {{ formatPercent(realtimeData[0].pricechangerate) }}%
                </span>
              </el-descriptions-item>
              <el-descriptions-item label="成交量(手)">{{ formatNumber(realtimeData[0].totalvolume) }}</el-descriptions-item>
              <el-descriptions-item label="成交额(亿元)">{{ formatNumber(realtimeData[0].turnover) }}</el-descriptions-item>
              <el-descriptions-item label="换手率">{{ formatPercent(realtimeData[0].turnoverrate) }}%</el-descriptions-item>
              <el-descriptions-item label="量比">{{ formatRatio(realtimeData[0].volumeratio) }}</el-descriptions-item>
              <el-descriptions-item label="最高价">¥{{ formatPrice(realtimeData[0].highestprice) }}</el-descriptions-item>
              <el-descriptions-item label="最低价">¥{{ formatPrice(realtimeData[0].lowestprice) }}</el-descriptions-item>
              <el-descriptions-item label="开盘价">¥{{ formatPrice(realtimeData[0].openingprice) }}</el-descriptions-item>
              <el-descriptions-item label="收盘价">¥{{ formatPrice(realtimeData[0].closeprice) }}</el-descriptions-item>
              <el-descriptions-item label="数据时间">{{ formatDateTime(realtimeData[0].datatimestamp) }}</el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>

          <el-tab-pane label="系统信息" name="system">
            <el-descriptions :column="2" border class="detail-descriptions">
              <el-descriptions-item label="创建时间">{{ formatDateTime(companyDetail.createdat) }}</el-descriptions-item>
              <el-descriptions-item label="更新时间">{{ formatDateTime(companyDetail.updatedat) }}</el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>

          <!-- ══════════════════════════════════════════════════════ -->
          <!-- AI 预测标签页                                          -->
          <!-- ══════════════════════════════════════════════════════ -->
          <el-tab-pane label="预测涨跌" name="prediction">
            <div class="prediction-panel">

              <!-- 说明横幅 -->
              <el-alert
                type="info"
                :closable="false"
                show-icon
                style="margin-bottom: 20px;">
                <template slot="description">
                  基于历史日频数据，使用机器学习模型预测未来 <strong>5 个交易日</strong>
                  的价格走势方向（看涨 / 看跌）。预测结果仅供参考，不构成投资建议。
                </template>
              </el-alert>

              <!-- 模型选择区 -->
              <el-card class="pred-card" shadow="never">
                <div slot="header" class="pred-card-header">
                  <i class="el-icon-cpu"></i>
                  <span>选择预测模型</span>
                </div>

                <el-radio-group v-model="predModel" class="model-radio-group">
                  <el-radio-button label="lgbm">
                    <i class="el-icon-data-line"></i>
                    LightGBM
                    <div class="model-sub">梯度提升 · 快速稳健</div>
                  </el-radio-button>
                  <el-radio-button label="lstm">
                    <i class="el-icon-time"></i>
                    LSTM
                    <div class="model-sub">时序神经网络 · 捕捉趋势</div>
                  </el-radio-button>
                  <el-radio-button label="gnn">
                    <i class="el-icon-share"></i>
                    GNN
                    <div class="model-sub">图神经网络 · 行业关联</div>
                  </el-radio-button>
                </el-radio-group>

                <!-- 模型说明 -->
                <div class="model-desc-text">
                  <span v-if="predModel === 'lgbm'">
                    <strong>LightGBM</strong>：基于梯度提升决策树，使用最新一日的全量技术指标与市场特征直接预测。
                    速度最快，解释性强，适合快速参考。
                  </span>
                  <span v-if="predModel === 'lstm'">
                    <strong>LSTM</strong>：长短期记忆神经网络，输入最近 20 个交易日的时序特征序列，
                    擅长捕捉价格动量与趋势变化。
                  </span>
                  <span v-if="predModel === 'gnn'">
                    <strong>GNN</strong>：异质图神经网络，同时考虑所有科创板股票间的
                    行业关联（40%）、价格相关性（30%）和估值相似度（30%），
                    通过图传播挖掘跨股关联信号。
                  </span>
                </div>

                <el-button
                  type="primary"
                  size="medium"
                  icon="el-icon-s-promotion"
                  :loading="predLoading"
                  :disabled="!companyDetail.stockcode"
                  @click="runPrediction"
                  style="margin-top: 16px;">
                  {{ predLoading ? '预测中...' : '开始预测' }}
                </el-button>
              </el-card>

              <!-- 错误提示 -->
              <el-alert
                v-if="predError"
                :title="predError"
                type="error"
                show-icon
                style="margin-top: 16px;">
              </el-alert>

              <!-- 预测结果卡片 -->
              <el-card
                v-if="predResult"
                ref="predResultCard"
                class="pred-result-card"
                shadow="always"
                style="margin-top: 20px;">
                <div slot="header" class="pred-result-header">
                  <span>预测结果 · {{ predResult.model }}</span>
                  <el-tag size="small" type="info">{{ predResult.trade_date }} 数据</el-tag>
                </div>

                <!-- 核心结论 -->
                <div class="pred-verdict-row">
                  <div
                    class="pred-verdict"
                    :class="predResult.pred_label === 1 ? 'verdict-up' : 'verdict-down'">
                    <span class="verdict-icon">
                      {{ predResult.pred_label === 1 ? '↑' : '↓' }}
                    </span>
                    <span class="verdict-text">{{ predResult.label_name }}</span>
                  </div>
                  <div class="pred-confidence">
                    <div class="conf-label">置信度</div>
                    <div class="conf-value">{{ predResult.confidence }}%</div>
                    <el-progress
                      :percentage="predResult.confidence"
                      :color="predResult.pred_label === 1 ? '#f56c6c' : '#67c23a'"
                      :stroke-width="8"
                      :show-text="false"
                      style="width:120px; margin-top:6px;">
                    </el-progress>
                  </div>
                </div>

                <!-- 详细数据 -->
                <el-descriptions :column="2" border style="margin-top: 16px;">
                  <el-descriptions-item label="预测方向">
                    <span :class="predResult.pred_label === 1 ? 'positive' : 'negative'">
                      <strong>{{ predResult.label_name }}</strong>
                    </span>
                  </el-descriptions-item>
                  <el-descriptions-item label="预测周期">
                    未来 {{ predResult.horizon_days }} 个交易日
                  </el-descriptions-item>
                  <el-descriptions-item label="看涨概率">
                    <span class="positive">{{ predResult.proba_up }}%</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="看跌概率">
                    <span class="negative">{{ predResult.proba_down }}%</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="判断阈值">
                    {{ predResult.threshold_pct }}%
                  </el-descriptions-item>
                  <el-descriptions-item label="数据基准日">
                    {{ predResult.trade_date }}
                  </el-descriptions-item>

                  <!-- LSTM 专有 -->
                  <el-descriptions-item
                    v-if="predResult.sequence_len"
                    label="输入序列长度">
                    {{ predResult.sequence_len }} 个交易日
                  </el-descriptions-item>

                  <!-- GNN 专有 -->
                  <el-descriptions-item
                    v-if="predResult.n_stocks_graph"
                    label="图内股票数">
                    {{ predResult.n_stocks_graph }} 只
                  </el-descriptions-item>
                </el-descriptions>

                <!-- GNN 关系权重 -->
                <div
                  v-if="predResult.relation_weights && Object.keys(predResult.relation_weights).length"
                  style="margin-top: 14px;">
                  <div class="rel-weight-title">图关系权重</div>
                  <div class="rel-weight-row">
                    <div
                      v-for="(w, name) in predResult.relation_weights"
                      :key="name"
                      class="rel-weight-item">
                      <el-progress
                        type="circle"
                        :percentage="Math.round(w * 100)"
                        :width="64"
                        :stroke-width="6">
                      </el-progress>
                      <div class="rel-name">{{ relNameMap[name] || name }}</div>
                    </div>
                  </div>
                </div>

                <!-- 说明文字 -->
                <div class="pred-desc-text">{{ predResult.desc }}</div>

              </el-card>

            <!-- ── FinBERT 机构研报情绪 ─────────────────────── -->
            <el-card class="sent-card" shadow="never">
              <div slot="header" class="sent-header">
                <span>📰 机构研报情绪分析</span>
                <el-tag size="small" type="info" style="margin-left:8px">FinBERT</el-tag>
              </div>

              <!-- 加载中 -->
              <div v-if="sentLoading" class="sent-loading">
                <i class="el-icon-loading"></i> 正在分析研报情绪...
              </div>

              <!-- 错误 -->
              <el-alert v-else-if="sentError" :title="sentError" type="warning" :closable="false" show-icon style="margin:8px 0"/>

              <!-- 无报告 -->
              <div v-else-if="sentResult && sentResult.report_count === 0" class="sent-empty">
                暂无研报数据
              </div>

              <!-- 结果 -->
              <div v-else-if="sentResult">
                <!-- 总体情绪 -->
                <div class="sent-overall">
                  <div class="sent-verdict" :style="{color: sentResult.overall_color}">
                    {{ sentResult.overall_sentiment === 'Positive' ? '▲' : sentResult.overall_sentiment === 'Negative' ? '▼' : '─' }}
                    {{ sentResult.overall_sentiment_cn }}
                  </div>
                  <div class="sent-meta">基于 {{ sentResult.report_count }} 篇机构研报</div>
                </div>

                <!-- 三色概率条 -->
                <div class="sent-bar-wrap">
                  <div class="sent-bar-label">
                    <span class="pos-text">看多 {{ sentResult.avg_pos }}%</span>
                    <span class="neu-text">中性 {{ sentResult.avg_neu }}%</span>
                    <span class="neg-text">看空 {{ sentResult.avg_neg }}%</span>
                  </div>
                  <div class="sent-bar">
                    <div class="sent-bar-pos" :style="{width: sentResult.avg_pos + '%'}"></div>
                    <div class="sent-bar-neu" :style="{width: sentResult.avg_neu + '%'}"></div>
                    <div class="sent-bar-neg" :style="{width: sentResult.avg_neg + '%'}"></div>
                  </div>
                </div>

                <!-- 逐篇明细 -->
                <div class="sent-reports">
                  <div v-for="rpt in sentResult.reports" :key="rpt.reportId" class="sent-report-item">
                    <el-tag
                      size="mini"
                      :type="rpt.sentiment==='Positive'?'success':rpt.sentiment==='Negative'?'danger':'info'"
                      style="margin-right:6px;flex-shrink:0">
                      {{ rpt.sentiment==='Positive'?'看多':rpt.sentiment==='Negative'?'看空':'中性' }}
                    </el-tag>
                    <span class="sent-report-title">{{ rpt.title }}</span>
                    <span class="sent-report-prob">
                      <span class="pos-text">{{ rpt.proba_pos }}%</span> /
                      <span class="neu-text">{{ rpt.proba_neu }}%</span> /
                      <span class="neg-text">{{ rpt.proba_neg }}%</span>
                    </span>
                  </div>
                </div>
              </div>
            </el-card>

            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      companyId: null,
      companyDetail: {},
      financialData: [],
      realtimeData: [],
      loading: true,
      error: null,
      activeTab: 'basic',

      // ── AI 预测 ──────────────────────────────────────────
      predModel:   'lgbm',
      predLoading: false,
      predResult:  null,
      predError:   null,
      relNameMap: {
        industry:       '行业关联',
        corr:           '价格相关',
        valuation_sim:  '估值相似',
        volume_sync:    '成交联动',
      },

      // ── FinBERT 情绪分析 ──────────────────────────────────
      sentResult:  null,
      sentLoading: false,
      sentError:   null,
    }
  },

  mounted() {
    this.initData();
  },

  watch: {
    // 切换股票时清空预测结果
    '$route.query.id'() {
      this.predResult  = null;
      this.predError   = null;
      this.sentResult  = null;
      this.sentError   = null;
      this.initData();
    },
    activeTab(val) {
      if (val === 'prediction') this.loadSentiment();
    },
  },

  methods: {
    // 初始化所有数据
    async initData() {
      // 从URL参数获取公司ID
      this.companyId = this.$route.query.id;
      console.log('获取到的公司ID:', this.companyId);
      
      if (!this.companyId) {
        this.error = '未提供公司ID';
        this.loading = false;
        return;
      }
      
      try {
        // 先加载公司详情
        await this.loadCompanyDetail();
        
        // 公司详情加载成功后，再加载财务和实时数据
        if (this.companyDetail && this.companyDetail.stockcode) {
          console.log('开始加载财务和实时数据，股票代码:', this.companyDetail.stockcode);
          await Promise.all([
            this.loadFinancialData(),
            this.loadRealtimeData()
          ]);
        } else {
          console.warn('股票代码为空，跳过财务和实时数据加载');
        }
      } catch (error) {
        console.error('数据加载失败:', error);
        this.error = '数据加载失败，请稍后重试';
      } finally {
        this.loading = false;
        console.log('所有数据加载完成');
      }
    },

    // 加载公司详情
    loadCompanyDetail() {
      return new Promise((resolve, reject) => {
        console.log('正在加载公司详情，ID:', this.companyId);
        
        this.axios.get(`http://localhost:9090/api/company-profiles/${this.companyId}`)
          .then(response => {
            const r = response.data;
            console.log('公司详情响应:', r);
            
            if (r.code === 200) {
              this.companyDetail = r.data;
              console.log('公司详情加载成功，股票代码:', this.companyDetail.stockcode);
              resolve();
            } else {
              this.error = r.msg || '加载公司详情失败';
              reject(new Error(this.error));
            }
          })
          .catch(error => {
            console.error('加载公司详情失败:', error);
            this.error = '网络错误，加载公司详情失败';
            reject(error);
          });
      });
    },

    // 加载财务数据
    loadFinancialData() {
      return new Promise((resolve) => {
        // 检查股票代码
        if (!this.companyDetail.stockcode) {
          console.warn('股票代码为空，跳过财务数据加载');
          this.financialData = [];
          resolve();
          return;
        }
        
        console.log('开始加载财务数据，股票代码:', this.companyDetail.stockcode);
        
        this.axios.get('http://localhost:9090/api/financial-reports/reporttype', {
          params: { stockCode: this.companyDetail.stockcode }
        })
        .then(response => {
          const r = response.data;
          console.log('财务数据响应:', r);
          
          if (r.code === 200) {
            this.financialData = r.data || [];
            console.log('财务数据加载成功，条数:', this.financialData.length);
          } else {
            console.warn('财务数据加载失败:', r.msg);
            this.financialData = [];
          }
          resolve();
        })
        .catch(error => {
          console.error('加载财务数据失败:', error);
          this.financialData = [];
          resolve();
        });
      });
    },

    // 加载实时数据
    loadRealtimeData() {
      return new Promise((resolve) => {
        // 检查股票代码
        if (!this.companyDetail.stockcode) {
          console.warn('股票代码为空，跳过实时数据加载');
          this.realtimeData = [];
          resolve();
          return;
        }
        
        console.log('开始加载实时数据，股票代码:', this.companyDetail.stockcode);
        
        this.axios.get('http://localhost:9090/api/realtime-market-data/list', {
          params: { stockCode: this.companyDetail.stockcode }
        })
        .then(response => {
          const r = response.data;
          console.log('实时数据响应:', r);
          
          if (r.code === 200) {
            this.realtimeData = r.data || [];
            console.log('实时数据加载成功，条数:', this.realtimeData.length);
          } else {
            console.warn('实时数据加载失败:', r.msg);
            this.realtimeData = [];
          }
          resolve();
        })
        .catch(error => {
          console.error('加载实时数据失败:', error);
          this.realtimeData = [];
          resolve();
        });
      });
    },

    // 返回上一页
    goBack() {
      this.$router.go(-1);
    },

    // 格式化函数
    formatDate(dateString) {
      if (!dateString) return '--';
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return dateString;
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
      } catch (error) {
        return dateString;
      }
    },

    formatDateTime(dateTimeString) {
      if (!dateTimeString) return '--';
      try {
        const date = new Date(dateTimeString);
        if (isNaN(date.getTime())) return dateTimeString;
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
      } catch (error) {
        return dateTimeString;
      }
    },

    formatNumber(num) {
      if (num === null || num === undefined || isNaN(num)) return '--';
      if (Math.abs(num) >= 100000000) {
        return (num / 100000000).toFixed(2) + '亿';
      } else if (Math.abs(num) >= 10000) {
        return (num / 10000).toFixed(2) + '万';
      }
      return num.toFixed(2);
    },

    formatRatio(value) {
      if (value === null || value === undefined || isNaN(value)) return '--';
      return value.toFixed(2);
    },

    formatPercent(value) {
      if (value === null || value === undefined || isNaN(value)) return '--';
      return value.toFixed(2);
    },

    formatPrice(value) {
      if (value === null || value === undefined || isNaN(value)) return '--';
      return value.toFixed(2);
    },

    getReportTypeLabel(type) {
      const map = {
        'Q1': '一季报',
        'S1': '半年报',
        'Q3': '三季报',
        'A': '年报'
      };
      return map[type] || type;
    },

    getStatusLabel(status) {
      const map = {
        'L': '正常交易',
        'S': '停牌',
        'D': '退市整理期',
        'T': '已退市'
      };
      return map[status] || status;
    },

    getStatusTagType(status) {
      const map = {
        'L': 'success',
        'S': 'warning',
        'D': 'danger',
        'T': 'info'
      };
      return map[status] || 'info';
    },

    // ── FinBERT 情绪分析 ──────────────────────────────────
    loadSentiment() {
      if (!this.companyDetail.stockcode) return;
      if (this.sentResult || this.sentLoading) return;   // 已有结果或正在加载则跳过
      this.sentLoading = true;
      this.sentError   = null;
      this.axios.get('http://localhost:8083/api/ml/sentiment', {
        params: { stockCode: this.companyDetail.stockcode },
        timeout: 30000,
      })
      .then(res => {
        if (res.data.code === 200) {
          this.sentResult = res.data.data;
        } else {
          this.sentError = res.data.msg || '情绪分析失败';
        }
      })
      .catch(() => {
        this.sentError = '情绪分析服务不可用，请确认 Flask 服务已启动';
      })
      .finally(() => { this.sentLoading = false; });
    },

    // ── AI 预测 ────────────────────────────────────────────
    runPrediction() {
      if (!this.companyDetail.stockcode) {
        this.$message.warning('暂未获取到股票代码，请稍后重试');
        return;
      }
      this.predLoading = true;
      this.predResult  = null;
      this.predError   = null;

      this.axios.get('http://localhost:8083/api/ml/predict', {
        params: {
          stockCode: this.companyDetail.stockcode,
          model:     this.predModel,
        },
        timeout: 60000,
      })
      .then(response => {
        const r = response.data;
        if (r.code === 200) {
          this.predResult = r.data;
          this.$message.success('预测完成');
        } else {
          this.predError = r.msg || '预测失败，请检查服务是否已启动';
        }
      })
      .catch(err => {
        if (err.code === 'ECONNABORTED') {
          this.predError = '请求超时，GNN 模型推理较慢，请稍后重试';
        } else if (err.response && err.response.data) {
          const d = err.response.data;
          this.predError = d.msg || JSON.stringify(d);
        } else {
          this.predError = 'AI 预测服务不可用，请确认已运行 predict_service/app.py（端口 8083）';
        }
      })
      .finally(() => {
        this.predLoading = false;
      });
    },
  },
}
</script>

<style scoped>
.company-detail-container {
  margin-top: -60px;
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.back-button {
  margin-bottom: 20px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 100px;
  background: white;
  border-radius: 8px;
}

.loading-text {
  margin-top: 20px;
  color: #666;
  font-size: 16px;
}

.error-container {
  padding: 20px;
  background: white;
  border-radius: 8px;
}

.company-detail-card {
  max-width: 1400px;
  margin: 0 auto;
}

.detail-card {
  border-radius: 8px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.company-title {
  font-size: 20px;
  font-weight: 600;
  color: #1e3c72;
}

.detail-descriptions {
  margin-top: 20px;
}

.text-content {
  padding: 20px;
  min-height: 200px;
  line-height: 1.8;
  font-size: 14px;
  color: #333;
}

.empty-data {
  padding: 50px;
  text-align: center;
  color: #999;
  font-size: 14px;
}

.positive {
  color: #f56c6c;
  font-weight: 600;
}

.negative {
  color: #67c23a;
  font-weight: 600;
}

::v-deep .el-descriptions__label {
  width: 150px;
  background-color: #f8f9fa;
  font-weight: 500;
}

::v-deep .el-tabs--border-card {
  border: none;
  box-shadow: none;
}

/* ══════════════════════════════════════════════
   AI 预测面板
══════════════════════════════════════════════ */
.prediction-panel {
  padding: 4px 0;
  max-height: 75vh;
  overflow-y: auto;
  padding-right: 4px;
}

/* 模型选择卡片 */
.pred-card {
  border-radius: 8px;
}
.pred-card-header {
  display: flex;
  align-items: center;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}
.pred-card-header i {
  margin-right: 8px;
  color: #409eff;
  font-size: 18px;
}

/* 模型单选按钮组 */
.model-radio-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
::v-deep .model-radio-group .el-radio-button__inner {
  padding: 10px 20px;
  text-align: left;
  line-height: 1.5;
  height: auto;
  white-space: normal;
  min-width: 140px;
}
.model-sub {
  font-size: 11px;
  color: #909399;
  margin-top: 2px;
  font-weight: 400;
}
::v-deep .model-radio-group .el-radio-button.is-active .model-sub {
  color: rgba(255,255,255,0.75);
}

/* 模型说明文字 */
.model-desc-text {
  margin-top: 14px;
  padding: 10px 14px;
  background: #f5f7fa;
  border-left: 3px solid #409eff;
  border-radius: 4px;
  font-size: 13px;
  color: #606266;
  line-height: 1.7;
}

/* ── 预测结果卡片 ── */
.pred-result-card {
  border-radius: 8px;
}
.pred-result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 15px;
  font-weight: 600;
}

/* 核心判断行 */
.pred-verdict-row {
  display: flex;
  align-items: center;
  gap: 32px;
  padding: 16px 0 8px;
}
.pred-verdict {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 28px;
  border-radius: 8px;
  min-width: 140px;
  justify-content: center;
}
.verdict-up {
  background: #fff1f0;
  border: 2px solid #f56c6c;
}
.verdict-down {
  background: #f0fff4;
  border: 2px solid #67c23a;
}
.verdict-icon {
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
}
.verdict-up .verdict-icon   { color: #f56c6c; }
.verdict-down .verdict-icon { color: #67c23a; }
.verdict-text {
  font-size: 26px;
  font-weight: 700;
}
.verdict-up .verdict-text   { color: #f56c6c; }
.verdict-down .verdict-text { color: #67c23a; }

/* 置信度区 */
.pred-confidence {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.conf-label {
  font-size: 12px;
  color: #909399;
}
.conf-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

/* GNN 关系权重 */
.rel-weight-title {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 10px;
}
.rel-weight-row {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}
.rel-weight-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.rel-name {
  font-size: 12px;
  color: #606266;
}

/* 预测说明文字 */
.pred-desc-text {
  margin-top: 14px;
  font-size: 12px;
  color: #909399;
  font-style: italic;
}

/* ── FinBERT 情绪卡片 ──────────────────────────────────── */
.sent-card { margin-top: 16px; }
.sent-header { display: flex; align-items: center; font-weight: 600; }
.sent-loading { text-align: center; color: #909399; padding: 20px 0; }
.sent-empty  { text-align: center; color: #c0c4cc; padding: 20px 0; }

.sent-overall {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}
.sent-verdict {
  font-size: 22px;
  font-weight: 700;
}
.sent-meta { font-size: 12px; color: #909399; }

.sent-bar-wrap { margin-bottom: 14px; }
.sent-bar-label {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  margin-bottom: 4px;
}
.sent-bar {
  display: flex;
  height: 10px;
  border-radius: 5px;
  overflow: hidden;
  background: #f0f0f0;
}
.sent-bar-pos { background: #67c23a; transition: width .4s; }
.sent-bar-neu { background: #909399; transition: width .4s; }
.sent-bar-neg { background: #f56c6c; transition: width .4s; }

.sent-reports { display: flex; flex-direction: column; gap: 8px; }
.sent-report-item {
  display: flex;
  align-items: center;
  font-size: 13px;
  padding: 6px 8px;
  background: #fafafa;
  border-radius: 4px;
}
.sent-report-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #303133;
}
.sent-report-prob { font-size: 12px; margin-left: 8px; flex-shrink: 0; color: #909399; }
.pos-text { color: #67c23a; font-weight: 600; }
.neu-text { color: #909399; }
.neg-text { color: #f56c6c; font-weight: 600; }
</style>