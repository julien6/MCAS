import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-agents-pixels',
  templateUrl: './agents-pixels.component.html',
  styleUrls: ['./agents-pixels.component.css']
})
export class AgentsPixelsComponent implements OnInit {

  teams: any
  data: any = {}

  ngOnInit() {

    this.data = {
      "0": {
        "observations": [0, 1, 2, 10],
        "actions": [0, 1]
      },
      "1": {
        "observations": [0, 1, 2, 14, 41, 0, 7],
        "actions": [1, 2, 3]
      },
      "2": {
        "observations": [0, 1, 2, 16],
        "actions": [0]
      }
    }

  }

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


}
