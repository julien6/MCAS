import { Component, OnInit } from '@angular/core';
import {MatTableModule} from '@angular/material/table';

@Component({
  selector: 'app-network-nodes',
  templateUrl: './network-nodes.component.html',
  styleUrls: ['./network-nodes.component.css']
})
export class NetworkNodesComponent implements OnInit {

  logsData: string;

  constructor() { }

  ngOnInit(): void {
  }

}
