<script lang="ts">
import { Scatter } from 'vue-chartjs'
import { Chart as ChartJS, registerables, type Point, type ChartData, type ChartOptions, type ChartDataset } from 'chart.js'
import { type SwitchCurve, type SwitchCurves, SwitchMeta, curveDataToCurve, getCurveData, getSwitchMetaData } from '../types/SwitchCurves'
import VueMultiselect from 'vue-multiselect'

async function getAllCurveData(
  selected: string[],
  showUpstroke: boolean
): Promise<SwitchCurves[]> {

  let data: SwitchCurves[] = []

  for (const selection of selected) {
    data.push(await getCurveData(selection, showUpstroke))
  }

  return data
}

const colours = [
  {
    downstroke: "rgb(54, 162, 235)", // Blue
    upstroke: "rgb(194, 227, 249)",
  },
  {
    downstroke: "rgb(255, 159, 64)", // Orange
    upstroke: "rgb(255, 226, 198)",
  },
  {
    downstroke: "rgb(75, 192, 75)", // Green
    upstroke: "rgb(201, 236, 201)",
  },
  {
    downstroke: "rgb(153, 102, 255)", // Purple
    upstroke: "rgb(224, 209, 255)"
  }
]

export default {
  components: {
    Scatter,
    VueMultiselect,
  },
  data() {
    return {
      showLinear: true,
      showTactile: true,
      showClicky: true,
      showOthers: true,
      available: [] as SwitchMeta[],
      selected: [] as SwitchMeta[],
      showUpstroke: false,
      switchData: null as SwitchCurves[] | null,
      zoom: 100,
    }
  },
  methods: {
    async doCompare() {
      const selectedNames = this.selected.map(item => item.name)
      console.log(`Selected: ${selectedNames.join(", ")}`)

      this.switchData = await getAllCurveData(selectedNames, this.showUpstroke)
    },
    switchCurvesToChartJs(): ChartData<"scatter", Point[], unknown> {
      let datasets: ChartDataset<"scatter", Point[]>[] = []
      let allCurves = this.switchData
      if (allCurves != null) {
        for (const [i, switchCurves] of allCurves.entries()) {
          datasets.push({
            label: switchCurves.name + " downstroke",
            data: switchCurves.downstroke.data,
            borderColor: colours[i].downstroke,
            order: i,
          })
          if (switchCurves.upstroke != null) {
            datasets.push({
              label: switchCurves.name + " upstroke",
              data: switchCurves.upstroke.data,
              borderColor: colours[i].upstroke,
              order: i + 10,
            })
          }
        }
        return {
          datasets: datasets,
        }
      }
      return {
        datasets: [],
      }
    },
    chartJsOptions(): ChartOptions<"scatter"> {
      return {
        showLine: true,
        maintainAspectRatio: false,
        plugins: {
          tooltip: {
            enabled: false,
          },
        },
        animation: {
          duration: 300,
        },
        elements: {
          point: {
            radius: 0,
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: "Travel (mm)",
            },
            min: 0,
            max: 4.5,
            ticks: {
              stepSize: 0.5,
            },
          },
          y: {
            title: {
              display: true,
              text: "Force (gf)",
            },
            min: 0,
            max: this.zoom,
            ticks: {
              stepSize: 20,
            },
          },
        },
      }
    },
    multiSelectLabel(item: SwitchMeta) {
      return `${item.name} (${item.type != null ? item.type : "unknown"})`
    },
    multiSelectOptions() {
      const self = this
      return this.available.filter(function (metaItem) {
        if (!self.showLinear && metaItem.type == "linear") return false
        else if (!self.showClicky && metaItem.type == "clicky") return false
        else if (!self.showTactile && metaItem.type == "tactile") return false
        else if (!self.showOthers && metaItem.type != "linear" && metaItem.type != "clicky" && metaItem.type != "tactile") return false
        else return true
      })
    },
    adjustZoom(amount: number) {
      const newZoom = this.zoom + amount
      if (newZoom >= 60 && newZoom <= 260) {
        this.zoom = newZoom
      }
    },
  },
  mounted() {
    console.log("Started switch selector component")
  },
  async created() {
    ChartJS.register(...registerables)
    console.log("Fetching curve data")
    const csvdata = await getSwitchMetaData()
    this.available = csvdata
  },
}
</script>

<template>

  <div id="switch-selection">
    <div>
      <label for="hideLinear">Show Linear</label>
      <input id="hideLinear" type="checkbox" v-model="showLinear" />
      <label for="hideLinear">Show Tactile</label>
      <input id="hideLinear" type="checkbox" v-model="showTactile" />
      <label for="hideLinear">Show Clicky</label>
      <input id="hideLinear" type="checkbox" v-model="showClicky" />
      <label for="hideLinear">Show Others</label>
      <input id="hideLinear" type="checkbox" v-model="showOthers" />
    </div>
    <div>
      <VueMultiselect
        v-model="selected"
        :options="multiSelectOptions()"
        :allow-empty="true"
        :multiple="true"
        :custom-label="multiSelectLabel"
        :max="4"
        :trackBy="'name'"
        />
    </div>
    <div>
      <label for="upstroke">Display upstroke</label>
      <input id="upstroke" type="checkbox" v-model="showUpstroke" />
    </div>

    <div>
      <button @click="doCompare">Compare</button>
    </div>
  </div>

  <div id="chart">
    <div id="zoom-buttons">
      <button @click="adjustZoom(-20)">Zoom In</button>
      <button @click="adjustZoom(20)">Zoom Out</button>
    </div>
    <Scatter
      v-if="switchData != null"
      :data="switchCurvesToChartJs()" 
      :options="chartJsOptions()"
      />
  </div>

</template>

<style src="vue-multiselect/dist/vue-multiselect.css"></style>

<style scoped>

#switch-selection {
  width: 40em;
}

#chart {
  margin-top: 2em;
  width: 800px;
  height: 500px;
}

#switch-selection input[type=checkbox] {
  margin-left: 1ex;
  margin-right: 1ex;
}

#zoom-buttons {
  float: right;
}

</style>