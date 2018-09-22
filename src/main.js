import Vue from 'vue'
import i18n from './i18n'
import { sync } from 'vuex-router-sync'
import App from './App.vue'
import router from './router'
import store from './stores'
import Assets from './assets'
import ModalBox from '@/components/ModalBox'
import ButtonSpinner from '@/components/ButtonSpinner'
import StyledSelect from '@/components/StyledSelect.vue'

import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
// import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import '@/css/app.sass'

import L from 'leaflet'

delete L.Icon.Default.prototype._getIconUrl

L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png')
})

Vue.config.productionTip = false

Vue.use(Assets)
Vue.component('modal-box', ModalBox)
Vue.component('button-spinner', ButtonSpinner)
Vue.component('styled-select', StyledSelect)

sync(store, router)

// store.subscribe((mutation, state) => {
//   console.log(mutation.type)
//   console.log(mutation.payload)
//   if (mutation.type == 'route/ROUTE_CHANGED')
//     console.log(store.route.params)
// })

new Vue({
  router,
  store,
  i18n,
  render: h => h(App)
}).$mount('#app')
