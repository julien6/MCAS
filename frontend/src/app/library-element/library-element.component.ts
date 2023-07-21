import { Component, TemplateRef, ViewChild } from '@angular/core';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MermaidAPI } from 'ngx-markdown';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Inject } from '@angular/core';

@Component({
  selector: 'app-library-element',
  templateUrl: './library-element.component.html',
  styleUrls: ['./library-element.component.css']
})
export class LibraryElementComponent {

  options: MermaidAPI.Config = {
    fontFamily: '"trebuchet ms", verdana, arial, sans-serif',
    logLevel: MermaidAPI.LogLevel.Info,
    theme: MermaidAPI.Theme.Dark
  };

  descriptionFilePath: string;
  dataFilePath: string;
  elementTitle: string;

  constructor(public dialogRef: MatDialogRef<LibraryElementComponent>, @Inject(MAT_DIALOG_DATA) public data: any) {
    this.descriptionFilePath = this.data["md_file_path"];
    this.dataFilePath = this.data["data_file_path"];
    this.elementTitle = this.data["title"]
    console.log(this.descriptionFilePath)
    console.log(this.dataFilePath)
  }

}
