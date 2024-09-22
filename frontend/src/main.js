import Vue from 'vue';
import App from './App.vue';
import vuetify from './plugins/vuetify'; // ตรวจสอบการนำเข้า
import 'vuetify/dist/vuetify.min.css'; // ตรวจสอบการนำเข้า CSS

Vue.config.productionTip = false;

new Vue({
  vuetify,
  render: h => h(App),
}).$mount('#app');
