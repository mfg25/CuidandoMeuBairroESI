import config from 'config'
import ajax from '../utils/ajax.js'
import MapStore from './mapStore'
import auth from './auth'
import msgs from '../store/msgs'
import {registerSignals} from '../utils/helpers'

var api = config.apiurl_subscriptions


class Subscriptions extends MapStore {
    constructor(signal) {
        super(signal)
        this.forceKey = 's'
        registerSignals(
            this,
            'subscribeExpense subscribePedido unsubscribeExpense',
            true
        )
    }
    ajaxParams(key) {
      // TODO: Não enviar se user for none
      console.log('request!', key, auth.getUsername(), this._map)
      return {
        url: `${api}/subscriptions`,
        method: 'post',
        data: {
            subscriber: auth.getUsername()
        }}
    }
    processResponse(json) {
        // orderComments(json.comments)
      console.log('response', json)
      let subscriptions = {}
      json.subscriptions.forEach((s) => subscriptions[s.tag] = s)
        return subscriptions
    }

    async subscribe(tag, author, errorMsg) {
      let params = {
        url: `${api}/subscriptions`,
        method: 'put',
        data: {
          token: await auth.getMicroToken(),
          subscriptions: [{
            tag,
            author,
            template_data: {link: window.location.href}
          }]}}

        let json = null
        try {
            json = await ajax(params)
            if (json) {
              this.load('eusinho', true)
            }
        } catch(err) {
            msgs.addError(errorMsg)
        }
        return json
    }

    // Subscribe to expense
    async subscribeExpense(params) {
      return await this.subscribe(params.id, params.author, 'Error to subscribe')
    }

  // Subscribe to pedido
  async subscribePedido(params) {
    return await this.subscribe(params.id, params.author, 'Error to subscribe')
  }

  async unsubscribe(tag, errorMsg) {
    let params = {
      url: `${api}/subscriptions`,
      method: 'delete',
      data: {
        token: await auth.getMicroToken(),
        tags: [tag]}}

    let json = null
    try {
      json = await ajax(params)
      if (json) {
        this.load('eusinho', true)
      }
    } catch(err) {
      msgs.addError(errorMsg)
    }
    return json
  }

  // Unsubscribe to expense
  async unsubscribeExpense(params) {
    return await this.unsubscribe(params.id, 'Error to subscribe')
  }
}

let subscriptions = new Subscriptions('subscriptions')

export default subscriptions
