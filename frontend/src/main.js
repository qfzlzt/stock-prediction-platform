import Vue from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import VueAxios from 'vue-axios'
import ElementUI from 'element-ui'; //加入
import 'element-ui/lib/theme-chalk/index.css';//加入s


Vue.use(VueAxios, axios)
Vue.use(ElementUI);//加入

Vue.config.productionTip = false

new Vue({
  render: h => h(App),
  router
}).$mount('#app')
