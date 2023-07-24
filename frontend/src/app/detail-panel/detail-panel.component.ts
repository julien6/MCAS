import { Component, OnInit, ViewChild } from '@angular/core';
import { JsonEditorOptions } from "@maaxgr/ang-jsoneditor";
import { WorldStateService } from '../services/app.worldState.service';
import { ConfigShareService } from '../services/config-share.service';

@Component({
  selector: 'app-detail-panel',
  templateUrl: './detail-panel.component.html',
  styleUrls: ['./detail-panel.component.css'],
})
export class DetailPanelComponent implements OnInit {

  public editorOptions: JsonEditorOptions;
  public sharedData: any;
  public visualData: any;

  public menuBarConfiguration: any;

  public lastAgent: string;

  public lastMetrics: any;

  options = {
    templates: [
      {
        text: 'Node',
        title: 'Insert a Network Node',
        className: 'jsoneditor-type-object',
        field: 'NodeTemplate',
        value: {
          'id': "Undefined ID",
          'label': 'Undefined Name',
        }
      },
      {
        text: 'Edge',
        title: 'Insert a Network Edge',
        field: 'EdgeTemplate',
        value: {
          'id': "Undefined ID",
          'from': "Undefined Start Node",
          'to': "Undefined End Node",
        }
      }
    ]
  }

  constructor(private worldStateService: WorldStateService, private configShareService: ConfigShareService) {
    this.editorOptions = new JsonEditorOptions();
    this.editorOptions.mode = 'code';
    this.editorOptions.mainMenuBar = true;
    this.editorOptions.language = "en";
    // (<any>this.editorOptions).templates = this.options.templates;
    // this.editorOptions.expandAll = true;

    this.visualData = this.worldStateService.getInitialState();
    this.sharedData = this.visualData;

    this.menuBarConfiguration = this.configShareService.getInitialConfiguration();

  }

  ngOnInit(): void {

    this.configShareService.currentConfiguration$.subscribe((data) => {
      this.menuBarConfiguration = data;
    })

    this.worldStateService.currentNetworkGraph$.subscribe((data) => {
      this.sharedData = data;
      this.visualData = data;
    })

    this.worldStateService.currentNetworkGraph$.subscribe((data) => {
      this.sharedData = data;
      this.visualData = data;
    })

    this.worldStateService.currentLastAgent$.subscribe((data) => {
      this.lastAgent = data
    })

    this.worldStateService.currentLastMetrics$.subscribe((data) => {
      this.lastMetrics = data
    })

  }

  showJson(d: Event) {
    this.sharedData = d;
  }

}
