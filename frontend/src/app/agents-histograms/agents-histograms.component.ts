import { Component, OnInit } from '@angular/core';
import { ChartConfiguration } from 'chart.js';

@Component({
  selector: 'app-agents-histograms',
  templateUrl: './agents-histograms.component.html',
  styleUrls: ['./agents-histograms.component.css']
})
export class AgentsHistogramsComponent implements OnInit {

  teams: any;

  public barChartLegend = true;
  public barChartPlugins = [];

  public barChartData: ChartConfiguration<'bar'>['data'] = {
    labels: ['action1', 'action2', 'action3', 'action4', 'action5'],
    datasets: [
      { data: [4, 9, 17, 47, 6], label: 'Actions' }
    ]
  };

  public barChartOptions: ChartConfiguration<'bar'>['options'] = {
    responsive: false,
  };

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
