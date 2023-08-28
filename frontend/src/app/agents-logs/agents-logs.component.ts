import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-agents-logs',
  templateUrl: './agents-logs.component.html',
  styleUrls: ['./agents-logs.component.css']
})
export class AgentsLogsComponent implements OnInit {
  logsData: string;
  teams: any;

  constructor() {

    this.teams = {
      "green": [
        {
          "name": "Agt1",
          "logs": "Starting..."
        },
        {
          "name": "Agt2",
          "logs": "Starting..."
        },
        {
          "name": "Agt3",
          "logs": "Starting..."
        }
      ],
      "red": [
        {
          "name": "Agt1",
          "logs": "Starting..."
        },
        {
          "name": "Agt2",
          "logs": "Starting..."
        },
        {
          "name": "Agt3",
          "logs": "Starting..."
        }
      ],
      "blue": [
        {
          "name": "Agt1",
          "logs": "Starting..."
        },
        {
          "name": "Agt2",
          "logs": "Starting..."
        },
        {
          "name": "Agt3",
          "logs": "Starting..."
        }
      ]
    }

  }

  ngOnInit(): void {
  }

}
