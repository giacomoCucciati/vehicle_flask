<template>
  <div>
    <div>
      <b-field label="Port list">
        <b-select placeholder="Select a port" v-model='selectedPort'>
          <option
            v-for="port in port_list"
            :value="port"
            :key="port">
            {{ port }}
          </option>
        </b-select>
      </b-field>
      <button v-on:click="startArduino">Connect Arduino</button>
      <button v-on:click="stopArduino">Disconnect Arduino</button>
      <div class="columns">
        <div class="column is-1">
          <button v-on:click="sendCommand('a')">Left</button>
        </div>
        <div class="column is-1">
          <button v-on:click="sendCommand('w')">Forward</button>
          <button v-on:click="sendCommand('s')">Backward</button>
        </div>
        <div class="column is-1">
          <button v-on:click="sendCommand('d')">Right</button>
        </div>
        <div class="column is-1">
          <b-field label="Delta ms">
            <b-input v-model="deltatime"></b-input>
          </b-field>
        </div>
        <!-- <div class="column">
          <img src="api/video_feed" width="640" height="480">
        </div> -->
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import io from 'socket.io-client'

const charList = new Map([['a', 0], ['s', 0], ['d', 0], ['w', 0]])

export default {
  name: 'InitPage',
  data () {
    return {
      port_list: [],
      light_points: [],
      pitemperature_points: [],
      temperatureDTH_points: [],
      humidityDTH_points: [],
      selectedPort: '',
      chartOptions: {
        series: []
      },
      deltatime: 0
    }
  },

  methods: {
    startArduino: function () {
      console.log('Selected port: ', this.selectedPort)
      axios.post('/api/startArduino', {selectedPort: this.selectedPort}).then(response => {
        console.log(response.data.message)
      })
    },

    stopArduino: function () {
      axios.get('/api/stopArduino').then(response => {
        console.log(response.data.message)
      })
    },

    sendCommand: function (theCommand) {
      console.log(theCommand)
      let clicktime = (new Date()).getTime()
      axios.post('/api/sendCommandToArduino', {command: theCommand, clicktime: clicktime}).then(response => {
        console.log(response.data.message)
        this.deltatime = response.data.servertime * 1000 - clicktime
        console.log('server time ', response.data.servertime, ' clicktime ', clicktime)
      })
    },

    releaseCommand: function (theCommand) {
      console.log(theCommand)
      axios.post('/api/releaseCommandToArduino', {command: theCommand}).then(response => {
        console.log(response.data.message)
      })
    },

    updatePage: function () {
      axios.get('/api/getPageUpdate').then(response => {
        this.port_list = response.data.portlist
        this.selectedPort = response.data.selectedPort
      })
    }
  },

  mounted () {
    // Asking all of the parameters to draw the page
    this.updatePage()

    // Creating the socket for updates notifications
    this.socket = io()

    document.onkeypress = (evt) => {
      evt = evt || window.event
      var charCode = evt.keyCode || evt.which
      var charStr = String.fromCharCode(charCode)
      charStr = charStr.toLowerCase()
      if (charList.has(charStr)) {
        if (!charList.get(charStr)) {
          this.sendCommand(charStr)
          charList.set(charStr, 1)
        }
      }
    }

    document.onkeyup = (evt) => {
      evt = evt || window.event
      var charCode = evt.keyCode || evt.which
      var charStr = String.fromCharCode(charCode)
      charStr = charStr.toLowerCase()
      if (charList.has(charStr)) {
        this.releaseCommand(charStr)
        charList.set(charStr, 0)
      }
    }
  },

  beforeRouteLeave (to, from, next) {
    this.socket.close()
    next()
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
