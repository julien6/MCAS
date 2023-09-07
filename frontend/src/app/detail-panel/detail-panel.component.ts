import { Component, OnInit, ViewChild } from '@angular/core';
import { JsonEditorOptions } from "@maaxgr/ang-jsoneditor";
import { DataService } from '../../app/services/app.data.service';
import { ConfigShareService } from '../services/config-share.service';

@Component({
  selector: 'app-detail-panel',
  templateUrl: './detail-panel.component.html',
  styleUrls: ['./detail-panel.component.css'],
})
export class DetailPanelComponent implements OnInit {

  public editorOptions: JsonEditorOptions;
  public sharedConfigurationData: any;
  public configurationData: any;
  public stateData: any;

  public menuBarConfiguration: any;

  // options = {
  //   templates: [
  //     {
  //       text: 'Node',
  //       title: 'Insert a Network Node',
  //       className: 'jsoneditor-type-object',
  //       field: 'NodeTemplate',
  //       value: {
  //         'id': "Undefined ID",
  //         'label': 'Undefined Name',
  //       }
  //     },
  //     {
  //       text: 'Edge',
  //       title: 'Insert a Network Edge',
  //       field: 'EdgeTemplate',
  //       value: {
  //         'id': "Undefined ID",
  //         'from': "Undefined Start Node",
  //         'to': "Undefined End Node",
  //       }
  //     }
  //   ]
  // }

  constructor(private dataService: DataService, private configShareService: ConfigShareService) {
    this.editorOptions = new JsonEditorOptions();
    this.editorOptions.mode = 'code';
    this.editorOptions.mainMenuBar = true;
    this.editorOptions.language = "en";
    // (<any>this.editorOptions).templates = this.options.templates;
    // this.editorOptions.expandAll = true;

    this.configurationData = {};
    this.sharedConfigurationData = this.configurationData;

    this.menuBarConfiguration = this.configShareService.getInitialConfiguration();

  }

  ngOnInit(): void {

    this.configShareService.currentConfiguration$.subscribe((data) => {
      this.menuBarConfiguration = data;
    })

    this.dataService.currentConfigurationData$.subscribe((data) => {
      this.sharedConfigurationData = data;
      this.configurationData = data;
    })

    this.dataService.currentStateData$.subscribe((data) => {
      this.stateData = data;
    })

  }

  showJson(d: Event) {
    this.sharedConfigurationData = d;
  }

}
