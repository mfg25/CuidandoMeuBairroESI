import decodeToken from 'jwt-decode'
import Vapi from 'vuex-rest-api'
import { baseUrls } from '@/configs'
import { http, addToStore } from '@/utils'

const baseURL = baseUrls.auth

function realExp (validPeriod) {
  let now = new Date()
  // Convert valid period from minutes to miliseconds, add it to now and
  // return for future checks, to see if it's still valid. We use this value
  // for checks instead of the exp field in the tokens because server and
  // clients may differ time settings.
  return now.getTime() + validPeriod * 60000
}

function saveMicroToken (data) {
  localStorage.microToken = data.microToken
  localStorage.microTokenValidTime = realExp(data.microTokenValidPeriod)
}

function saveTokens (state, json) {
  // if (json && json.mainToken) {
  localStorage.mainToken = json.mainToken
  localStorage.mainTokenValidTime = realExp(json.mainTokenValidPeriod)
  state.username = decodeUsername(localStorage.mainToken)
  saveMicroToken(json)
  // } else {
  //   dispatch('addError', 'error_token_json')
  // }
}

function handleError (state, error) {
  state.errorData = JSON.parse(error.response.data.message)
}

function validMainToken () {
  let now = new Date()
  // Check if main token is still valid for 30s
  return localStorage.mainToken && (now < localStorage.mainTokenValidTime - 30000)
}

function decodeUsername (token) {
  return decodeToken(localStorage.mainToken).username
}

export default addToStore(new Vapi({
  axios: http,
  baseURL,
  state: {
    username: null,
    userInfo: null,
    errorData: null
  }
}).get({
  action: 'getUserInfo',
  property: 'userInfo',
  path: ({ username }) => `/users/${username}`,
  onSuccess: (state, payload, axios, { params }) => {
    state.userInfo = payload.data
  }
}).post({
  action: 'loginUser',
  property: 'username',
  path: '/login/local',
  onSuccess: (state, payload, axios, { params }) => {
    saveTokens(state, payload.data)
    // TODO limpar cache dos dados desse usuário para poder pegar dados completos
  },
  onError: handleError
}).post({
  action: 'registerUser',
  path: '/users',
  onSuccess: (state, payload) => {
    saveTokens(state, payload.data)
  },
  onError: handleError
}).post({
  action: 'forgotPassword',
  property: 'expResetCode',
  path: '/reset_password',
  onError: handleError,
  onSuccess: async (state, payload) => {
    state.expResetCode = payload.data.exp
  }
}).put({
  action: 'resetPassword',
  property: 'username',
  path: '/reset_password',
  onError: handleError,
  onSuccess: async (state, payload) => {
    saveTokens(state, payload.data)
    // TODO limpar cache dos dados desse usuário para poder pegar dados completos
  }
}).getStore(),
{
  mutations: {
    setUsername (state, username) {
      state.username = username
    },
    clearUserData (state) {
      localStorage.removeItem('mainToken')
      localStorage.removeItem('microToken')
      state.username = null
    },
    setAuthError (state, error) {
      state.errorData = error
    }
  },
  actions: {
    loadPrevAuthData ({ commit }) {
      if (validMainToken()) {
        commit('setUsername', decodeUsername(localStorage.mainToken))
      }
      // TODO se não for valido talvez devesse deletar?
    },
    async getMicroToken ({ dispatch }) {
      var now = new Date()

      // Check if micro token is still valid for 30s
      if (now < localStorage.microTokenValidTime - 30000) {
        console.log('auth:getMicroToken: no need to renew token')
      } else {
        let url = `${baseURL}/renew_micro_token`
        let data = {
          token: localStorage.mainToken
        }
        console.log('auth:getMicroToken: renewing token with:', data)
        try {
          let response = await http.post(url, data)
          console.log('response', response)
          if (response.data) saveMicroToken(response.data)
          else return null
        } catch (err) {
          dispatch('clearUserData')
          dispatch('addError', 'error_renew_token')
        }
      }
      console.log('token:', localStorage.microToken)
      return localStorage.microToken
    },
    async logout ({ dispatch }) {
      let data = { token: localStorage.mainToken }
      dispatch('clearUserData')
      try {
        await http.post(`${baseURL}/logout`, data)
      } catch (err) {
        dispatch('addError', 'error_logout_server')
      }
    },
    clearUserData ({ commit }) {
      // TODO limpar cache para não deixar dados sigilosos
      // if (state.username) userinfo.forgetUser(this._currUsername)
      commit('clearUserData')
    },
    requireLogin ({ state, commit }) {
      if (!state.username) {
        commit('openModal', 'login')
      }
    }
  }
})

// loadUsername ({ dispatch, commit }) {
//   if (localStorage.mainToken) {
//     var now = new Date()
//     // Check if main token is still valid for 30s
//     if (now < localStorage.mainTokenValidTime - 30000) {
//       try {
//         commit('setUsername', decodeToken(localStorage.mainToken).username)
//       } catch (err) {
//         dispatch('clearUserData')
//         dispatch('addError', 'error_decode_token')
//         return null
//       }
//     } else {
//       // Clear tokens if main token is too old
//       dispatch('clearUserData')
//     }
//   }
//   return true
// },

//     async showErrorMessage(err) {
//         let msg = JSON.parse((await err.response.json()).message)
//         this.trigger(riot.SEC('authError'), msg)
//     }

//     async resetPassword(params) {
//         try {
//             this.saveTokens(await ajax({
//                 url: api + "/reset_password",
//                 data: {
//                     username: params.username,
//                     password: params.password,
//                     email: params.email,
//                     code: params.code
//                 },
//                 method: 'put',
//             }))
//         } catch(err) {
//             await this.showErrorMessage(err)
//         }
//     }
