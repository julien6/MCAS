import { Component, OnInit } from '@angular/core';
import { ChartOptions } from 'chart.js';

@Component({
  selector: 'app-agents-piecharts',
  templateUrl: './agents-piecharts.component.html',
  styleUrls: ['./agents-piecharts.component.css']
})
export class AgentsPiechartsComponent implements OnInit {

  teams: any

  // Pie
  public pieChartOptions: ChartOptions<'pie'> = {
    responsive: false,
  };
  public pieChartLabels = [ [ 'Download', 'Sales' ], [ 'In', 'Store', 'Sales' ], 'Mail Sales' ];
  public pieChartDatasets = [ {
    data: [ 300, 500, 100 ]
  } ];
  public pieChartLegend = true;
  public pieChartPlugins = [];

  constructor() {

    this.teams = {
      "green": [
        {
          "name": "Agt1",
          "data": {}
        },
        {
          "name": "Agt2",
          "data": {}
        },
        {
          "name": "Agt3",
          "data": {}
        }
      ],
      "red": [
        {
          "name": "Agt1",
          "data": {}
        },
        {
          "name": "Agt2",
          "data": {}
        },
        {
          "name": "Agt3",
          "data": {}
        }
      ],
      "blue": [
        {
          "name": "Agt1",
          "data": {}
        },
        {
          "name": "Agt2",
          "data": {}
        },
        {
          "name": "Agt3",
          "data": {}
        }
      ]
    }

  }

  ngOnInit(): void {
  }

}
