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
      <button v-on:click="startArduino">Start reading xbee</button>
      <button v-on:click="stopArduino">Stop reading xbee</button>
      <button v-on:click="fakeAcquisition">Fake points</button>
      <div v-if="this.chartOptions !== undefined">
        <highcharts :options="chartOptions" ref="lineCharts"></highcharts>
      </div>
      <div class="columns">
        <div class="column is-1">
          <button v-on:click="sendCommand('a')" disabled=true>Left</button>
        </div>
        <div class="column is-1">
          <button v-on:click="sendCommand('w')" disabled=true>Forward</button>
          <button v-on:click="sendCommand('s')" disabled=true>Backward</button>
        </div>
        <div class="column is-1">
          <button v-on:click="sendCommand('d')" disabled=true>Right</button>
        </div>
        <div class="column is-1">
          <b-field label="Delta ms">
            <b-input v-model="deltatime"></b-input>
          </b-field>
        </div>
        <div class="column">
          <img src="api/video_feed" width="640" height="480">
        </div>
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

    fakeAcquisition: function () {
      axios.get('/api/startFakeAcq').then(response => {
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

        response.data.pointList.forEach(point => {
          this.light_points.push([point.timestamp, point.lum])
          this.pitemperature_points.push([point.timestamp, point.pitemp])
          this.temperatureDTH_points.push([point.timestamp, point.tempDTH])
          this.humidityDTH_points.push([point.timestamp, point.humDTH])
        })
      })
    },

    defineChartOptions () {
      this.chartOptions['chart'] = {
        type: 'scatter',
        zoomType: 'x'
      }
      this.chartOptions['title'] = {
        text: 'Measurements'
        // margin: -44
      }
      this.chartOptions['xAxis'] = {
        title: {
          text: 'Time'
        },
        type: 'datetime',
        dateTimeLabelFormats: {
          second: '%H:%M:%S'
        }
      }
      this.chartOptions['yAxis'] = {
        title: {
          text: 'Celsius or ADC counts'
        }
        // min: 0,
        // max: 1024
      }
      this.chartOptions['plotOptions'] = {
        series: {
          animation: false
        }
      }
      this.chartOptions['series'].push({
        name: 'PI Temp',
        color: 'rgba(233, 233, 0, 0.7)',
        data: this.pitemperature_points,
        marker: {
          symbol: 'cyrcle'
        }
      })
      this.chartOptions['series'].push({
        name: 'Light',
        color: 'rgba(0, 255, 0, 0.7)',
        data: this.light_points,
        marker: {
          symbol: 'cyrcle'
        }
      })
      this.chartOptions['series'].push({
        name: 'TempDTH',
        color: 'rgba(255, 0, 0, 0.7)',
        data: this.temperatureDTH_points,
        marker: {
          symbol: 'cyrcle'
        }
      })
      this.chartOptions['series'].push({
        name: 'HumDTH',
        color: 'rgba(125, 125, 125, 0.7)',
        data: this.humidityDTH_points,
        marker: {
          symbol: 'cyrcle'
        }
      })
    },

    askOnePoint () {
      // console.log('Request from server to get the last point.')
      axios.get('/api/getSinglePoint').then(r => {
        // console.log(r)
        this.light_points.push([r.data.singlePoint.timestamp, r.data.singlePoint.lum])
        this.pitemperature_points.push([r.data.singlePoint.timestamp, r.data.singlePoint.pitemp])
        this.temperatureDTH_points.push([r.data.singlePoint.timestamp, r.data.singlePoint.tempDTH])
        this.humidityDTH_points.push([r.data.singlePoint.timestamp, r.data.singlePoint.humDTH])
        if (this.light_points.length > 1000) {
          this.light_points.shift()
        }
        if (this.pitemperature_points.length > 1000) {
          this.pitemperature_points.shift()
        }
        if (this.temperatureDTH_points.length > 1000) {
          this.temperatureDTH_points.shift()
        }
        if (this.humidityDTH_points.length > 1000) {
          this.humidityDTH_points.shift()
        }
      })
    }
  },

  mounted () {
    // Asking all of the parameters to draw the page
    this.updatePage()

    // Creating the socket for updates notifications
    this.socket = io()

    // Callback for update event
    this.socket.on('updateSinglePoint', () => this.askOnePoint())

    this.defineChartOptions()

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
