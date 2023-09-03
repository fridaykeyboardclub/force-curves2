import { parse } from 'csv-parse/browser/esm/sync'
import axios from 'axios';

const basePath = "/force-curves2"

export interface SwitchCurves {
  name: string;
  downstroke: SwitchCurve;
  upstroke: SwitchCurve | null;
}

export interface SwitchCurve {
  data: {
    x: number;
    y: number;
  }[];
}

export class SwitchMeta {
  readonly name: string
  readonly type: string

  constructor(name: string, type: string) {
    this.name = name
    this.type = type
  }
}

export async function getSwitchMetaData(): Promise<SwitchMeta[]> {
  const csvresponse = await axios.get(basePath + "/data/switchmeta.csv")
  const parsedArrays = parse(csvresponse.data, {
    columns: false,
    skip_empty_lines: true,
  })
  return parsedArrays.map(function (elem: any[]) {
    const switchType = elem.length == 2 ? elem[1] : undefined
    return new SwitchMeta(elem[0] as string, switchType)
  })
}

export function curveDataToCurve(name: string, csvData: string, downstroke: boolean): SwitchCurve {
  const parsedArray = parse(csvData, {
    columns: false,
    skip_empty_lines: true,
  })
  return {
    data: parsedArray.map(function (elem: string[]) {
      return {x: parseFloat(elem[0]), y: parseFloat(elem[1])}
    }),
  }
}

export async function getCurveData(name: string, showUpstroke: boolean): Promise<SwitchCurves> {
  console.log(`Getting data for ${name} downstroke`)
  const downstrokeCurve = curveDataToCurve(
    name,
    (await axios.get(`${basePath}/data/csv_output/${name}.downstroke.csv`)).data,
    true
  )

  let upstrokeCurve = null
  if (showUpstroke) {
    console.log(`Getting data for ${name} downstroke`)
    upstrokeCurve = curveDataToCurve(
      name,
      (await axios.get(`${basePath}/data/csv_output/${name}.upstroke.csv`)).data,
      false
    )
  }
  
  return {
    name: name,
    downstroke: downstrokeCurve,
    upstroke: upstrokeCurve,
  }
}