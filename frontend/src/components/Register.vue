<template>
	<div id="r_app">
	        <div class="main_div">
	            <div class="info_div">
	                <div>
	                    <div class="logo">股票<span>预测</span></div>
	                    <div class="subtitle">开启您的智能投资之旅</div>
	                    <table class="table_cls">
	                        <tr>
	                            <td>账号：</td>
	                            <td><el-input v-model="form.username" placeholder="请输入账号"></el-input></td>
	                        </tr>
	                        <tr>
	                            <td>密码：</td>
	                            <td><el-input type="password" v-model="form.password" placeholder="请输入密码" show-password></el-input></td>
	                        </tr>
	                    </table>
	                </div>
	                <div class="button-group">
	                    <el-button class="register_btn" @click="register()" type="primary">注册用户</el-button>
	                    <el-button class="login_btn" @click="$router.push('/Login')" type="warning">去登陆</el-button>
	                </div>
					 <div class="features">
					        <div class="feature-item">
					          <div class="feature-icon">📈</div>
					          <div class="feature-text">AI智能预测</div>
					        </div>
					        <div class="feature-item">
					          <div class="feature-icon">🔍</div>
					          <div class="feature-text">深度数据分析</div>
					        </div>
					        <div class="feature-item">
					          <div class="feature-icon">🛡️</div>
					          <div class="feature-text">专业风险评估</div>
					        </div>
					      </div>
	            </div>
	            
	            <div class="stock-chart">
	                <div class="chart-line"></div>
	            </div>
	        </div>
	    </div>
</template>

<script>
	export default {
		
		data(){
			return {
				form:{
					username:"",
					password:"",
				}
			
			}
			
		},
		methods:{
			goPage(url){
				this.$router.push(url)
			},
			register(){
				this.axios({
					method:"POST",
					url:"http://localhost:9090/user/register",
					data:this.form
				}).then((result)=>{
					var r=result.data;
					if(r.code==200){
						this.$message({
							message:"注册成功",
							type: "success"
						});
						this.$router.push('/Login')
					}else{
						this.$message({
							message:r.msg,
							type:"error"
						})
					}
				}).catch((result)=>{
					
				})
			}
		}
	}
</script>

<style>
	 * {
	            margin: 0;
	            padding: 0;
	            box-sizing: border-box;
	            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
	        }
	        
	        /* 确保 html 和 body 完全覆盖 */
	html, body {
	    margin: 0;
	    padding: 0;
	    width: 100%;
	    height: 100%;
	    overflow-x: hidden;
	}
	
	#r_app{
		width: 100%;
	    height: 100%;
		background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
		position: fixed;
		top: 0;
		left: 0;
		overflow-y: auto;
		overflow-x: hidden;
	}
	        .main_div {
	            width: 100%;
	            height: 100%;
	            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
	            display: flex;
	            justify-content: center;
	            align-items: center;
	            position: relative;
	            overflow: hidden;
	        }
	        
	        .info_div {
	            width: 420px;
	            background-color: rgba(255, 255, 255, 0.95);
	            border-radius: 12px;
	            padding: 30px;
	            display: flex;
	            flex-direction: column;
	            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
	            z-index: 10;
	            position: relative;
	        }
	        
	        .logo {
	            font-size: 28px;
	            font-weight: 700;
	            margin-bottom: 10px;
	            color: #1e3c72;
	            text-align: center;
	        }
	        
	        .logo span {
	            color: #4dabf7;
	        }
	        
	        .subtitle {
	            color: #666;
	            margin-bottom: 25px;
	            text-align: center;
	            font-size: 14px;
	        }
	        
	        .table_cls {
	            width: 100%;
	            margin: 15px 0;
	        }
	        
	        .table_cls tr td {
	            padding: 12px 5px;
	            vertical-align: middle;
	        }
	        
	        .table_cls tr td:first-child {
	            width: 80px;
	            font-weight: 500;
	            color: #333;
	        }
	        
	        .button-group {
	            display: flex;
	            justify-content: space-between;
	            margin-top: 20px;
	            gap: 15px;
	        }
	        
	        .register_btn, .login_btn {
	            flex: 1;
	            height: 45px;
	            font-size: 16px;
	            font-weight: 600;
	        }
	        
	        .register_btn {
	            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
	            border: none;
	        }
	        
	        .stock-chart {
	            position: absolute;
	            bottom: 0;
	            left: 0;
	            right: 0;
	            height: 120px;
	            background: rgba(0, 0, 0, 0.2);
	            overflow: hidden;
	            z-index: 1;
	        }
	        
	        .chart-line {
	            position: absolute;
	            bottom: 0;
	            left: 0;
	            width: 100%;
	            height: 100%;
	            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 120" preserveAspectRatio="none"><path d="M0,90 Q300,30 600,90 T1200,30 L1200,120 L0,120 Z" fill="rgba(255,255,255,0.1)"/></svg>');
	            background-size: cover;
	        }
	        
	        @media (max-width: 480px) {
	            .info_div {
	                width: 90%;
	                padding: 20px;
	            }
	            
	            .button-group {
	                flex-direction: column;
	            }
	        }
			.features {
			  display: flex;
			  justify-content: space-around;
			  width: 100%;
			  margin-top: 25px;
			  padding-top: 20px;
			  border-top: 1px solid #eee;
			}
			
			.feature-item {
			  display: flex;
			  flex-direction: column;
			  align-items: center;
			  text-align: center;
			}
			
			.feature-icon {
			  font-size: 24px;
			  margin-bottom: 5px;
			}
			
			.feature-text {
			  font-size: 12px;
			  color: #666;
			}

</style>